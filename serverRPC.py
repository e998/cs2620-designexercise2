import time
import traceback
import argparse
import os

import pymysql
import pymysql.cursors
import bcrypt

import grpc
from concurrent import futures

import chat_pb2
import chat_pb2_grpc

# Command-line arguments
parser = argparse.ArgumentParser(description="Start the chat server (gRPC).")
parser.add_argument("--host", default=os.getenv("CHAT_SERVER_HOST", "0.0.0.0"), help="Server hostname or IP")
parser.add_argument("--port", type=int, default=int(os.getenv("CHAT_SERVER_PORT", 65432)), help="Port number")
args = parser.parse_args()
HOST = args.host
PORT = args.port

# Database connection
def connectsql():
    return pymysql.connect(
        host="localhost",
        user='root',
        password='',
        database='db262',
        cursorclass=pymysql.cursors.DictCursor
    )

# Helper functions
def checkRealUsername(username):
    with connectsql() as db:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE username=%s", (username,))
            row = cur.fetchone()
            return row['cnt'] > 0

def checkValidPassword(password):
    if len(password) < 7:
        return False
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in ['_', '@', '$', '#', '!'] for c in password)
    return has_upper and has_digit and has_special

def hashPass(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def checkRealPassword(username, plain_text):
    with connectsql() as db:
        with db.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username=%s", (username,))
            row = cur.fetchone()
            if not row:
                return False
            stored_hash = row['password']
    return bcrypt.checkpw(plain_text.encode('utf-8'), stored_hash.encode('utf-8'))

class ChatService(chat_pb2_grpc.ChatServicer):
    def Register(self, request, context):
        reg_username = request.username.strip()
        reg_password = request.password.strip()
        confirm_password = request.confirm_password.strip()

        if not reg_username or not reg_password or not confirm_password:
            return chat_pb2.Response(
                command="1",
                server_message="Registration canceled: All fields are required."
            )
        if checkRealUsername(reg_username):
            return chat_pb2.Response(
                command="1",
                server_message="Username taken. Please choose another."
            )
        if not checkValidPassword(reg_password):
            return chat_pb2.Response(
                command="1",
                server_message="Invalid password: Must be >=7 chars, include uppercase, digit, and special char."
            )
        if reg_password != confirm_password:
            return chat_pb2.Response(
                command="1",
                server_message="Passwords do not match."
            )
        hashed = hashPass(reg_password)
        try:
            with connectsql() as db:
                with db.cursor() as cur:
                    cur.execute("INSERT INTO users (username, password, active) VALUES (%s, %s, 1)",
                                (reg_username, hashed))
                db.commit()
            return chat_pb2.Response(
                command="1",
                server_message="Registration successful. You are now logged in!"
            )
        except Exception:
            traceback.print_exc()
            return chat_pb2.Response(
                command="1",
                server_message="Server error during registration."
            )

    def Login(self, request, context):
        username = request.username.strip()
        password = request.password.strip()

        if not checkRealUsername(username):
            return chat_pb2.Response(
                command="2",
                server_message="User not found."
            )
        if not checkRealPassword(username, password):
            return chat_pb2.Response(
                command="2",
                server_message="Incorrect password."
            )
        # Mark user active
        with connectsql() as db:
            with db.cursor() as cur:
                cur.execute("UPDATE users SET active=1 WHERE username=%s", (username,))
            db.commit()
        return chat_pb2.Response(
            command="2",
            server_message=f"Welcome, {username}!"
        )

    def SendMessage(self, request, context):
        full_text = request.message.strip()
        md = dict(context.invocation_metadata())
        sender = md.get("username", "unknown")
        if not full_text.startswith("@"):
            return chat_pb2.SendMessageResponse(
                success=False,
                server_message="Message must start with '@username' for a direct message."
            )
        parts = full_text.split(" ", 1)
        if len(parts) < 2:
            return chat_pb2.SendMessageResponse(
                success=False,
                server_message="Invalid format. Use '@username message'."
            )
        target_username = parts[0][1:]
        message = parts[1]
        if not checkRealUsername(target_username):
            return chat_pb2.SendMessageResponse(
                success=False,
                server_message="Recipient does not exist."
            )
        try:
            with connectsql() as db:
                with db.cursor() as cur:
                    cur.execute(
                        "INSERT INTO messages (receiver, sender, message, isread) VALUES (%s, %s, %s, 0)",
                        (target_username, sender, message)
                    )
                    db.commit()
            return chat_pb2.SendMessageResponse(
                success=True,
                server_message=""
            )
        except Exception:
            traceback.print_exc()
            return chat_pb2.SendMessageResponse(
                success=False,
                server_message="Error storing message."
            )

    def CheckMessages(self, request_iterator, context):
        """
        Bidirectional conversation:
         1. The first request must contain the username.
         2. The server checks unread count and asks: read (1) or skip (2).
         3. The client replies with a choice.
         4. If "1", the server lists senders and then asks which sender.
         5. The client replies with the sender’s name and the server streams messages.
        """
        try:
            username = None
            stage = 0  # 0=await username, 1=await read/skip, 2=await sender
            for req in request_iterator:
                if stage == 0:
                    username = req.username.strip()
                    if not username:
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message="No username provided. Aborting."
                        )
                        break

                    with connectsql() as db:
                        with db.cursor() as cur:
                            cur.execute("""
                                SELECT COUNT(*) AS cnt
                                FROM messages
                                WHERE receiver=%s AND isread=0
                            """, (username,))
                            row = cur.fetchone()
                            unread_count = row['cnt']

                    if unread_count == 0:
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message="You have 0 unread messages."
                        )
                        break
                    else:
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message=(
                                f"You have {unread_count} unread messages.\n"
                                f"Type '1' to read them, or '2' to skip."
                            )
                        )
                        stage = 1
                        continue

                elif stage == 1:
                    choice = req.choice.strip()
                    if choice == "2":
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message="Skipping reading messages."
                        )
                        break
                    elif choice == "1":
                        with connectsql() as db:
                            with db.cursor() as cur:
                                cur.execute("""
                                    SELECT sender, COUNT(*) as num
                                    FROM messages
                                    WHERE receiver=%s AND isread=0
                                    GROUP BY sender
                                """, (username,))
                                senders_info = cur.fetchall()
                        if not senders_info:
                            yield chat_pb2.CheckMessagesResponse(
                                command="checkmessages",
                                server_message="No unread messages found."
                            )
                            break

                        senders_str = ", ".join([f"{r['sender']}({r['num']})" for r in senders_info])
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message=f"Unread from: {senders_str}\nType the sender's name to read those messages."
                        )
                        stage = 2
                        continue
                    else:
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message="Invalid choice. Please type '1' or '2'."
                        )
                        continue

                elif stage == 2:
                    chosen_sender = req.sender.strip()
                    if not chosen_sender:
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message="Please provide a valid sender name."
                        )
                        continue

                    with connectsql() as db:
                        with db.cursor() as cur:
                            cur.execute("""
                                SELECT messageid, sender, message, datetime
                                FROM messages
                                WHERE receiver=%s AND sender=%s AND isread=0
                                ORDER BY messageid
                            """, (username, chosen_sender))
                            msgs = cur.fetchall()
                    if not msgs:
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message=f"No unread messages from {chosen_sender}."
                        )
                        break

                    batch_size = 5
                    for i in range(0, len(msgs), batch_size):
                        batch = msgs[i:i+batch_size]
                        for m in batch:
                            ts = m['datetime'].strftime("%Y-%m-%d %H:%M:%S")
                            yield chat_pb2.CheckMessagesResponse(
                                command="checkmessages",
                                server_message=f"{ts} {m['sender']}: {m['message']}",
                                sender=m['sender'],
                                message_body=m['message']
                            )
                        # Mark batch as read
                        batch_ids = [m['messageid'] for m in batch]
                        placeholders = ','.join(['%s'] * len(batch_ids))
                        with connectsql() as db:
                            with db.cursor() as cur:
                                cur.execute(f"""
                                    UPDATE messages
                                    SET isread=1
                                    WHERE messageid IN ({placeholders})
                                """, batch_ids)
                            db.commit()
                        yield chat_pb2.CheckMessagesResponse(
                            command="checkmessages",
                            server_message="(This batch marked as read.)"
                        )
                    yield chat_pb2.CheckMessagesResponse(
                        command="checkmessages",
                        server_message="Done reading messages from this sender."
                    )
                    break
        except Exception as e:
            traceback.print_exc()
            yield chat_pb2.CheckMessagesResponse(
                command="checkmessages",
                server_message="Error: " + str(e)
            )

    def Logoff(self, request, context):
        username = request.username.strip()
        if not username:
            return chat_pb2.Response(
                command="logoff",
                server_message="No username provided."
            )
        try:
            with connectsql() as db:
                with db.cursor() as cur:
                    cur.execute("UPDATE users SET active=0 WHERE username=%s", (username,))
                db.commit()
            return chat_pb2.Response(
                command="logoff",
                server_message=f"{username} has been logged off."
            )
        except Exception:
            traceback.print_exc()
            return chat_pb2.Response(
                command="logoff",
                server_message="Logoff error."
            )

    def SearchUsers(self, request, context):
        username = request.username.strip()
        try:
            with connectsql() as db:
                with db.cursor() as cur:
                    cur.execute("SELECT username FROM users")
                    rows = cur.fetchall()
            all_users = [r['username'] for r in rows if r['username'] != username]
            return chat_pb2.SearchResponse(
                success=True,
                usernames=all_users,
                server_message="User list retrieved."
            )
        except Exception:
            traceback.print_exc()
            return chat_pb2.SearchResponse(
                success=False,
                usernames=[],
                server_message="Error searching users."
            )

    def DeleteLastMessage(self, request_iterator, context):
        """
        Bidirectional conversation for delete:
         1. Server sends a prompt asking confirmation.
         2. Client sends back the confirmation.
         3. Server performs deletion if confirmed.
        """
        try:
            yield chat_pb2.Response(
                command="delete",
                server_message="Are you sure you want to delete your last unread message? (yes/no)"
            )
            for req in request_iterator:
                username = req.username.strip()
                confirm = req.confirmation.strip().lower()
                if confirm == 'yes':
                    with connectsql() as db:
                        with db.cursor() as cur:
                            cur.execute("""
                                SELECT messageid FROM messages
                                WHERE sender=%s AND isread=0
                                ORDER BY messageid DESC LIMIT 1
                            """, (username,))
                            row = cur.fetchone()
                            if not row:
                                yield chat_pb2.Response(
                                    command="delete",
                                    server_message="No unread messages to delete."
                                )
                                break
                            last_id = row['messageid']
                            cur.execute("DELETE FROM messages WHERE messageid=%s", (last_id,))
                            db.commit()
                    yield chat_pb2.Response(
                        command="delete",
                        server_message="Your last unread message was deleted."
                    )
                    break
                else:
                    yield chat_pb2.Response(
                        command="delete",
                        server_message="Delete canceled."
                    )
                    break
        except Exception as e:
            traceback.print_exc()
            yield chat_pb2.Response(
                command="delete",
                server_message="Error: " + str(e)
            )

    def DeactivateAccount(self, request_iterator, context):
        """
        Bidirectional conversation for deactivation:
         1. Server sends a prompt.
         2. Client replies with confirmation.
         3. Server deactivates account if confirmed.
        """
        try:
            yield chat_pb2.Response(
                command="deactivate",
                server_message="Are you sure you want to deactivate your account? (yes/no)"
            )
            for req in request_iterator:
                username = req.username.strip()
                confirmation = req.confirmation.strip().lower()
                if confirmation == 'yes':
                    with connectsql() as db:
                        with db.cursor() as cur:
                            cur.execute("DELETE FROM messages WHERE sender=%s", (username,))
                            cur.execute("DELETE FROM users WHERE username=%s", (username,))
                        db.commit()
                    yield chat_pb2.Response(
                        command="deactivate",
                        server_message="Your account and sent messages are removed."
                    )
                    break
                else:
                    yield chat_pb2.Response(
                        command="deactivate",
                        server_message="Deactivation canceled."
                    )
                    break
        except Exception as e:
            traceback.print_exc()
            yield chat_pb2.Response(
                command="deactivate",
                server_message="Error: " + str(e)
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(ChatService(), server)
    address = f"{HOST}:{PORT}"
    server.add_insecure_port(address)
    server.start()
    print(f"Server started on {address}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()