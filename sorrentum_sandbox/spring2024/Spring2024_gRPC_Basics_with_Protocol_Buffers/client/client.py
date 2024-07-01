import grpc
import sys
sys.path.append('..')
import chat_pb2
import chat_pb2_grpc


def send_message(stub):
    user_id = input("Enter your user ID: ")
    username = input("Enter your username: ")
    user = chat_pb2.User(user_id=user_id, username=username)
    chat_room_stream = stub.JoinChatRoom(iter([user]))
    for chat_room in chat_room_stream:
        print(f"Joined chat room {chat_room.room_id}")
        for message in chat_room.history:
            print(f"{message.user.username}: {message.message}")

    while True:
        message = input("Enter your message: ")
        chat_message = chat_pb2.ChatMessage(user=user, message=message)
        response = stub.JoinChat(iter([chat_message]))
        for resp in response:
            print(f"Server response: {resp.message}")


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = chat_pb2_grpc.ChatServiceStub(channel)
    send_message(stub)


if __name__ == '__main__':
    main()
