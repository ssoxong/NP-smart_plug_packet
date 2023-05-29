import socket
import threading
import smartPlug
import pickle
import queue
import select

#서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = '127.0.0.1'  # Server host address
server_port = 9002  # Server port number
server_socket.bind((server_host, server_port))
server_socket.listen(5)  #최대 5개 연결 가능

client_connections = []

def handle_client(conn, addr):
    with conn:
        print("Connected with client:", addr)
        while True:
            # 인자로 받은 값 파싱
            IP_P100 = conn.recv(1024).decode()
            email = conn.recv(1024).decode()
            password = conn.recv(1024).decode()
            myPlugdecoding = conn.recv(4096)
            myPlug = pickle.loads(myPlugdecoding)
            
            #client에게 진행상황 알리는 send
            response = "Start SmartPlug init..."
            conn.send(response.encode())
            smartPlug.main(IP_P100, email, password, myPlug)

            response = "Start Packet Monitoring..."
            conn.send(response.encode())

            # 가장 마지막에 받은 패킷을 사용하기 위해 LIFO 이용
            buffer = queue.LifoQueue()

            # 멀티스레드 사용
            # p0은 패킷을 캡쳐하는 스레드
            # p1은 발생한 패킷을 사용자 패턴과 매치하는 스레드
            th0 = threading.Thread(target=smartPlug.getPacket, args=(buffer, addr))
            th0.start()
            th1 = threading.Thread(target=smartPlug.checkTime, args=(buffer, conn))
            th1.start()
            th0.join()
            th1.join()
            break

def start_server():
    while True:
        #소켓 리스트 생성
        sockets_list = [server_socket] + client_connections

        #관심있는 소켓 지정
        readable_sockets, _, _ = select.select(sockets_list, [], [])

        #관심있는 소켓 관찰
        for readable_socket in readable_sockets:
            #새로운 client
            if readable_socket == server_socket:
                conn, addr = server_socket.accept()
                client_connections.append(conn)
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()

            #연결된 client의 요청은 smartPlug로 넘어감


if __name__ == "__main__":
    start_server()
