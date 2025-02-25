# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import chat_pb2 as chat__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in chat_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ChatStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/Chat/Register',
                request_serializer=chat__pb2.RegisterRequest.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                _registered_method=True)
        self.Login = channel.unary_unary(
                '/Chat/Login',
                request_serializer=chat__pb2.LoginRequest.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                _registered_method=True)
        self.SendMessage = channel.unary_unary(
                '/Chat/SendMessage',
                request_serializer=chat__pb2.GeneralMessage.SerializeToString,
                response_deserializer=chat__pb2.SendMessageResponse.FromString,
                _registered_method=True)
        self.CheckMessages = channel.stream_stream(
                '/Chat/CheckMessages',
                request_serializer=chat__pb2.CheckMessagesRequest.SerializeToString,
                response_deserializer=chat__pb2.CheckMessagesResponse.FromString,
                _registered_method=True)
        self.Logoff = channel.unary_unary(
                '/Chat/Logoff',
                request_serializer=chat__pb2.LogoffRequest.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                _registered_method=True)
        self.SearchUsers = channel.unary_unary(
                '/Chat/SearchUsers',
                request_serializer=chat__pb2.SearchRequest.SerializeToString,
                response_deserializer=chat__pb2.SearchResponse.FromString,
                _registered_method=True)
        self.DeleteLastMessage = channel.stream_stream(
                '/Chat/DeleteLastMessage',
                request_serializer=chat__pb2.DeleteRequest.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                _registered_method=True)
        self.DeactivateAccount = channel.stream_stream(
                '/Chat/DeactivateAccount',
                request_serializer=chat__pb2.DeactivateRequest.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                _registered_method=True)
        self.ReceiveMessages = channel.unary_stream(
                '/Chat/ReceiveMessages',
                request_serializer=chat__pb2.ReceiveRequest.SerializeToString,
                response_deserializer=chat__pb2.ReceiveResponse.FromString,
                _registered_method=True)


class ChatServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckMessages(self, request_iterator, context):
        """Bidirectional streaming for interactive message checking
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logoff(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SearchUsers(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteLastMessage(self, request_iterator, context):
        """Bidirectional streaming for delete and deactivation confirmations
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeactivateAccount(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReceiveMessages(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=chat__pb2.RegisterRequest.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=chat__pb2.LoginRequest.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'SendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMessage,
                    request_deserializer=chat__pb2.GeneralMessage.FromString,
                    response_serializer=chat__pb2.SendMessageResponse.SerializeToString,
            ),
            'CheckMessages': grpc.stream_stream_rpc_method_handler(
                    servicer.CheckMessages,
                    request_deserializer=chat__pb2.CheckMessagesRequest.FromString,
                    response_serializer=chat__pb2.CheckMessagesResponse.SerializeToString,
            ),
            'Logoff': grpc.unary_unary_rpc_method_handler(
                    servicer.Logoff,
                    request_deserializer=chat__pb2.LogoffRequest.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'SearchUsers': grpc.unary_unary_rpc_method_handler(
                    servicer.SearchUsers,
                    request_deserializer=chat__pb2.SearchRequest.FromString,
                    response_serializer=chat__pb2.SearchResponse.SerializeToString,
            ),
            'DeleteLastMessage': grpc.stream_stream_rpc_method_handler(
                    servicer.DeleteLastMessage,
                    request_deserializer=chat__pb2.DeleteRequest.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'DeactivateAccount': grpc.stream_stream_rpc_method_handler(
                    servicer.DeactivateAccount,
                    request_deserializer=chat__pb2.DeactivateRequest.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'ReceiveMessages': grpc.unary_stream_rpc_method_handler(
                    servicer.ReceiveMessages,
                    request_deserializer=chat__pb2.ReceiveRequest.FromString,
                    response_serializer=chat__pb2.ReceiveResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Chat', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('Chat', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Chat(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Chat/Register',
            chat__pb2.RegisterRequest.SerializeToString,
            chat__pb2.Response.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Chat/Login',
            chat__pb2.LoginRequest.SerializeToString,
            chat__pb2.Response.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Chat/SendMessage',
            chat__pb2.GeneralMessage.SerializeToString,
            chat__pb2.SendMessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CheckMessages(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/Chat/CheckMessages',
            chat__pb2.CheckMessagesRequest.SerializeToString,
            chat__pb2.CheckMessagesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Logoff(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Chat/Logoff',
            chat__pb2.LogoffRequest.SerializeToString,
            chat__pb2.Response.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SearchUsers(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Chat/SearchUsers',
            chat__pb2.SearchRequest.SerializeToString,
            chat__pb2.SearchResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteLastMessage(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/Chat/DeleteLastMessage',
            chat__pb2.DeleteRequest.SerializeToString,
            chat__pb2.Response.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeactivateAccount(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/Chat/DeactivateAccount',
            chat__pb2.DeactivateRequest.SerializeToString,
            chat__pb2.Response.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReceiveMessages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/Chat/ReceiveMessages',
            chat__pb2.ReceiveRequest.SerializeToString,
            chat__pb2.ReceiveResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
