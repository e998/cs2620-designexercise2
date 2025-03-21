#!/usr/bin/env python3
import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import argparse
import os
import grpc
import chat_pb2
import chat_pb2_grpc

class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Client (gRPC)")
        self.username = None
        self.stub = None
        self.channel = None
        # For bidirectional sessions, active_bidi in ["check", "delete", "deactivate"]
        self.active_bidi = None
        # Queue to route input during bidirectional sessions
        self.bidi_queue = None

        # Frames for different pages
        self.welcome_frame = tk.Frame(self.root)
        self.login_frame = tk.Frame(self.root)
        self.register_frame = tk.Frame(self.root)
        self.chat_frame = tk.Frame(self.root)

        # Build each page
        self.build_welcome_frame()
        self.build_login_frame()
        self.build_register_frame()
        self.build_chat_frame()

        self.show_welcome_page()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    # UI Building
    def build_welcome_frame(self):
        label = tk.Label(self.welcome_frame, text="Welcome to EST!\nPlease choose an option:", font=("Helvetica", 16))
        label.pack(pady=10)
        login_btn = tk.Button(self.welcome_frame, text="Login", width=15, command=self.show_login_page)
        login_btn.pack(pady=5)
        register_btn = tk.Button(self.welcome_frame, text="Register", width=15, command=self.show_register_page)
        register_btn.pack(pady=5)

    def build_login_frame(self):
        label = tk.Label(self.login_frame, text="Login", font=("Helvetica", 16))
        label.pack(pady=10)
        self.login_username_var = tk.StringVar()
        self.login_password_var = tk.StringVar()
        tk.Label(self.login_frame, text="Username:").pack(pady=5)
        tk.Entry(self.login_frame, textvariable=self.login_username_var).pack(pady=5)
        tk.Label(self.login_frame, text="Password:").pack(pady=5)
        tk.Entry(self.login_frame, textvariable=self.login_password_var, show="*").pack(pady=5)
        tk.Button(self.login_frame, text="Submit", width=10, command=self.handle_login).pack(pady=5)
        self.login_error_label = tk.Label(self.login_frame, text="", fg="red")
        self.login_error_label.pack(pady=5)

    def build_register_frame(self):
        label = tk.Label(self.register_frame, text="Register", font=("Helvetica", 16))
        label.pack(pady=10)
        self.reg_username_var = tk.StringVar()
        self.reg_password_var = tk.StringVar()
        self.reg_confirm_var = tk.StringVar()
        tk.Label(self.register_frame, text="Username:").pack(pady=5)
        tk.Entry(self.register_frame, textvariable=self.reg_username_var).pack(pady=5)
        tk.Label(self.register_frame, text="Password:").pack(pady=5)
        tk.Entry(self.register_frame, textvariable=self.reg_password_var, show="*").pack(pady=5)
        tk.Label(self.register_frame, text="Confirm Password:").pack(pady=5)
        tk.Entry(self.register_frame, textvariable=self.reg_confirm_var, show="*").pack(pady=5)
        tk.Button(self.register_frame, text="Submit", width=10, command=self.handle_register).pack(pady=5)
        self.register_error_label = tk.Label(self.register_frame, text="", fg="red")
        self.register_error_label.pack(pady=5)

    def build_chat_frame(self):
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap='word', width=80, height=24)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.tag_configure("right", justify="right")
        self.input_frame = tk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        self.message_entry = tk.Entry(self.input_frame, width=70)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", self.send_message)
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=(5,0))

    # Page Navigation
    def show_welcome_page(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.chat_frame.pack_forget()
        self.welcome_frame.pack(fill="both", expand=True)

    def show_login_page(self):
        self.welcome_frame.pack_forget()
        self.register_frame.pack_forget()
        self.login_error_label.config(text="")
        self.login_frame.pack(fill="both", expand=True)

    def show_register_page(self):
        self.welcome_frame.pack_forget()
        self.login_frame.pack_forget()
        self.register_error_label.config(text="")
        self.register_frame.pack(fill="both", expand=True)

    def show_chat_page(self):
        self.welcome_frame.pack_forget()
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.chat_frame.pack(fill="both", expand=True)

    # Login/ Registration Handling
    def handle_login(self):
        username = self.login_username_var.get().strip()
        password = self.login_password_var.get().strip()
        if not username or not password:
            self.login_error_label.config(text="Please enter both username and password.")
            return
        threading.Thread(target=self.login_thread, args=(username, password), daemon=True).start()

    def login_thread(self, username, password):
        try:
            self.channel = grpc.insecure_channel(f"{HOST}:{PORT}")
            self.stub = chat_pb2_grpc.ChatStub(self.channel)
            response = self.stub.Login(chat_pb2.LoginRequest(username=username, password=password))
            if "Welcome" in response.server_message:
                self.username = username
                self.root.after(0, self.show_chat_page)
                self.append_message("Welcome, " + username + "!", sent_by_me=False)
                threading.Thread(target=self.process_messages_flow, daemon=True).start()
            else:
                err_msg = "Login error: " + response.server_message
                self.root.after(0, lambda err_msg=err_msg: self.login_error_label.config(text=err_msg))
                self.channel.close()
                self.channel = None
                self.stub = None
        except Exception as e:
            err_msg = "Login error: " + str(e)
            self.root.after(0, lambda err_msg=err_msg: self.login_error_label.config(text=err_msg))
            if self.channel:
                self.channel.close()
                self.channel = None
                self.stub = None

    def handle_register(self):
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get().strip()
        confirm = self.reg_confirm_var.get().strip()
        if not username or not password or not confirm:
            self.register_error_label.config(text="Please fill in all fields.")
            return
        if password != confirm:
            self.register_error_label.config(text="Passwords do not match.")
            return
        threading.Thread(target=self.register_thread, args=(username, password, confirm), daemon=True).start()

    def register_thread(self, username, password, confirm):
        try:
            self.channel = grpc.insecure_channel(f"{HOST}:{PORT}")
            self.stub = chat_pb2_grpc.ChatStub(self.channel)
            response = self.stub.Register(chat_pb2.RegisterRequest(username=username, password=password, confirm_password=confirm))
            if "successful" in response.server_message.lower():
                self.username = username
                self.root.after(0, self.show_chat_page)
                self.append_message("Welcome, " + username + "!", sent_by_me=False)
                threading.Thread(target=self.process_messages_flow, daemon=True).start()
            else:
                err_msg = response.server_message
                self.root.after(0, lambda err_msg=err_msg: self.register_error_label.config(text=err_msg))
                self.channel.close()
                self.channel = None
                self.stub = None
        except Exception as e:
            err_msg = "Registration error: " + str(e)
            self.root.after(0, lambda err_msg=err_msg: self.register_error_label.config(text=err_msg))
            if self.channel:
                self.channel.close()
                self.channel = None
                self.stub = None

    # Message Flows
    def process_messages_flow(self):
        """CheckMessages called upon initial login but afterwards, use ReceiveMessages to pull new messages."""
        self.check_messages_stream()
        self.receive_messages_stream()

    def check_messages_stream(self):
        self.active_bidi = "check"
        self.bidi_queue = queue.Queue()
        def request_generator():
            yield chat_pb2.CheckMessagesRequest(username=self.username)
            while True:
                user_input = self.bidi_queue.get()
                if user_input in ("1", "2"):
                    yield chat_pb2.CheckMessagesRequest(username=self.username, choice=user_input)
                else:
                    yield chat_pb2.CheckMessagesRequest(username=self.username, sender=user_input)
        try:
            responses = self.stub.CheckMessages(request_generator(), metadata=(('username', self.username),))
            for resp in responses:
                self.append_message(resp.server_message, sent_by_me=False)
                if resp.server_message == "Skipping reading messages." or resp.server_message == "Invalid choice. Aborting.":
                    sys.exit(0)
                    break
        except grpc.RpcError as err:
            if err.code() == grpc.StatusCode.CANCELLED:
                pass
            else:
                self.append_message("Error in check_messages_stream: " + str(err), sent_by_me=False)
        finally:
            self.active_bidi = None

    def receive_messages_stream(self):
        """Automatically pull new messages after the backlog is processed."""
        try:
            responses = self.stub.ReceiveMessages(chat_pb2.ReceiveRequest(username=self.username))
            for resp in responses:
                display = f"[{resp.timestamp}] {resp.sender}: {resp.message}"
                self.append_message(display, sent_by_me=False)
        except Exception as e:
            self.append_message("Error in receive_messages_stream: " + str(e), sent_by_me=False)

    def history_messages_stream(self):
        self.active_bidi = "history"
        self.bidi_queue = queue.Queue()
        def request_gen():
            # Step 1: Trigger the history prompt by sending an initial request with empty confirmation.
            yield chat_pb2.HistoryRequest(username=self.username, confirmation="")
            # Step 2: Wait for user's input for the userID 
            confirmation = ""
            while not confirmation:
                confirmation = self.bidi_queue.get().strip()
            yield chat_pb2.HistoryRequest(username=self.username, confirmation=confirmation.lower())
        try:
            responses = self.stub.History(request_gen(), metadata=(('username', self.username),))
            for resp in responses:
                self.append_message(resp.server_message, sent_by_me=False)
        except grpc.RpcError as e:
            self.append_message("Error in history_messages_stream: " + str(e), sent_by_me=False)
        finally:
            self.active_bidi = None
        

    def delete_last_message_stream(self):
        self.active_bidi = "delete"
        self.bidi_queue = queue.Queue()
        def request_gen():
            # Step 1: Trigger the deletion prompt by sending an initial request with empty confirmation.
            yield chat_pb2.DeleteRequest(username=self.username, confirmation="")
            # Step 2: Wait for user's confirmation input from the GUI.
            confirmation = ""
            while not confirmation:
                confirmation = self.bidi_queue.get().strip()
            yield chat_pb2.DeleteRequest(username=self.username, confirmation=confirmation.lower())
        try:
            responses = self.stub.DeleteLastMessage(request_gen(), metadata=(('username', self.username),))
            for resp in responses:
                self.append_message(resp.server_message, sent_by_me=False)
        except grpc.RpcError as e:
            self.append_message("Error in delete_last_message_stream: " + str(e), sent_by_me=False)
        finally:
            self.active_bidi = None

    def deactivate_account_stream(self):
        self.active_bidi = "deactivate"
        self.bidi_queue = queue.Queue()
        def request_gen():
            yield chat_pb2.DeactivateRequest(username=self.username, confirmation="")
            confirmation = ""
            while not confirmation:
                confirmation = self.bidi_queue.get().strip()
            yield chat_pb2.DeactivateRequest(username=self.username, confirmation=confirmation.lower())
        try:
            responses = self.stub.DeactivateAccount(request_gen(), metadata=(('username', self.username),))
            for resp in responses:
                self.append_message(resp.server_message, sent_by_me=False)
                if "removed" in resp.server_message:
                    self.close_connection()
        except Exception as e:
            self.append_message("Error in deactivate_account_stream: " + str(e), sent_by_me=False)
        finally:
            self.active_bidi = None

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if not message:
            return
        self.message_entry.delete(0, tk.END)
        # Bidirectional routes
        if self.active_bidi:
            if self.bidi_queue:
                self.bidi_queue.put(message)
            self.append_message(message, sent_by_me=True)
            return

        # Regular commands
        self.append_message(message, sent_by_me=True)
        if message.lower() == "check":
            threading.Thread(target=self.check_messages_stream, daemon=True).start()
            return
        if message.lower() == "delete":
            threading.Thread(target=self.delete_last_message_stream, daemon=True).start()
            return
        if message.lower() == "deactivate":
            threading.Thread(target=self.deactivate_account_stream, daemon=True).start()
            return
        if message.lower() == "search":
            response = self.stub.SearchUsers(chat_pb2.SearchRequest(username=self.username),
                                               metadata=(('username', self.username),))
            self.append_message(response.server_message, sent_by_me=False)
            if response.success and response.usernames:
                self.append_message("Users: " + ", ".join(response.usernames), sent_by_me=False)
            return
        if message.lower() == "history":
            threading.Thread(target=self.history_messages_stream, daemon=True).start()
            return
        if message.lower() == "logoff":
            response = self.stub.Logoff(chat_pb2.LogoffRequest(username=self.username),
                                          metadata=(('username', self.username),))
            self.append_message(response.server_message, sent_by_me=False)
            self.close_connection()
            return
        if message.startswith("@"):
            response = self.stub.SendMessage(chat_pb2.GeneralMessage(command="sendmessage", message=message),
                                             metadata=(('username', self.username),))
            self.append_message(response.server_message, sent_by_me=False)
            return
        response = self.stub.SendMessage(chat_pb2.GeneralMessage(command="sendmessage", message=message),
                                         metadata=(('username', self.username),))
        self.append_message(response.server_message, sent_by_me=False)

    def append_message(self, message, sent_by_me=False):
        self.chat_display.configure(state='normal')
        if sent_by_me:
            self.chat_display.insert(tk.END, message + "\n", "right")
        else:
            self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.yview(tk.END)

    def close_connection(self):
        if self.channel:
            self.channel.close()
        self.channel = None
        self.stub = None
        self.username = None
        self.chat_frame.pack_forget()
        self.show_welcome_page()

    def on_close(self):
        try:
            if self.stub and self.username:
                self.stub.Logoff(chat_pb2.LogoffRequest(username=self.username))
        except Exception:
            pass
        self.close_connection()
        self.root.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the chat client (gRPC).")
    parser.add_argument("--host", default=os.getenv("CHAT_SERVER_HOST", "127.0.0.1"), help="Server hostname or IP")
    parser.add_argument("--port", type=int, default=int(os.getenv("CHAT_SERVER_PORT", 65432)), help="Port number")
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    ChatClient()