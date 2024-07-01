import grpc
import sys
sys.path.append('..')
import chat_pb2
import chat_pb2_grpc
from concurrent import futures
import datetime


class ChatServicer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.chat_rooms = {}

    def JoinChat(self, request_iterator, context):
        for message in request_iterator:
            # Received messages are processed here
            print(f"Received message from {message.user.user_id}: {message.message}")
            now = datetime.datetime.now()
            current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            with open('message_history.txt', 'a') as file:
                file.write('userid: {}, userName: {}, message: {}, time: {}\n'.format(message.user.user_id, message.user.username, message.message, current_datetime))


            # Server sends message to all clients
            yield chat_pb2.ChatMessage(user=message.user, message="Received your message!")

    def JoinChatRoom(self, request_iterator, context):
        for user in request_iterator:
            # The logic for users to join the chat room is handled here.
            print(f"User {user.user_id} joined the chat room.")
            if user.user_id not in self.chat_rooms:
                self.chat_rooms[user.user_id] = chat_pb2.ChatRoom(
                    room_id="room1",
                    users=[user],
                    history=[]
                )
                now = datetime.datetime.now()
                current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
                with open('login_history.txt', 'a') as file:
                    file.write('userid: {}, userName: {}, time: {}\n'.format(user.user_id, user.username, current_datetime))

            else:
                self.chat_rooms[user.user_id].users.append(user)

            # Send chat room information and history
            for room_id, chat_room in self.chat_rooms.items():
                # print(room_id, chat_room)
                yield chat_room


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
