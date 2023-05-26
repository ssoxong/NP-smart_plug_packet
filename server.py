import socket
import threading
import smartPlug
import pickle
import queue
import select

# Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = '127.0.0.1'  # Server host address
server_port = 9002  # Server port number
server_socket.bind((server_host, server_port))
server_socket.listen(5)  # Listen for incoming connections

def handle_client(sock):
    # Handle client requests here
    conn, addr = sock
    with conn:
        print("with")
        while True:

            #인자로 받은 값 파싱
            IP_P100 = conn.recv(1024).decode()
            email = conn.recv(1024).decode()
            password = conn.recv(1024).decode()
            myPlugdecoding = conn.recv(4096)
            myPlug = pickle.loads(myPlugdecoding)
            
            response = "Start SmartPlug init..."
            conn.send(response.encode())
            smartPlug.main(IP_P100, email, password, myPlug)

            response = "Start Packet Monitoring..."
            conn.send(response.encode())

            #가장 마지막에 받은 패킷을 사용하기 위해 LIFO 이용
            buffer = queue.LifoQueue()
            p0 = threading.Thread(target=smartPlug.getPacket, args=(buffer,addr))
            p0.start()
            p1 = threading.Thread(target=smartPlug.checkTime, args=(buffer,conn))
            p1.start()
            p0.join()
            p1.join()

            break

client_sockets = []

def start_server():
    while True:
        # 소켓 리스트 설정 (서버 소켓 + 현재 연결된 클라이언트 소켓들)
        sockets_list = [server_socket] + client_sockets

        # 읽을 수 있는 소켓 리스트, _, _ = select.select(읽을 소켓 리스트)
        readables, _, _ = select.select(sockets_list, [], [])

        # 읽을 수 있는 소켓에 대해 처리
        for sock in readables:
            if sock == server_socket:
                # 새로운 클라이언트 연결
                client_socket, client_address = server_socket.accept()
                print("Connected with client:", client_address)

                # 클라이언트 소켓 리스트에 추가
                client_sockets.append(client_socket)
                
            else:
                # 기존 클라이언트로부터 데이터 수신 및 처리
                client_socket = sock
                handle_client(client_socket)

if __name__ == "__main__":
    # Start the server
    start_server()
