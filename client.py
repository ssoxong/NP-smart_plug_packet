import socket
import pickle
from pattern import plug
import threading
import os


# 서버 정보
server_host = '127.0.0.1'
server_port = 9002

# 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_port))
print("Server connect!!")

# 서버에 데이터 전송
print("Please enter yout data.")

IP_P100 = input("IP P100: ")
client_socket.send(IP_P100.encode())

email = input("email: ")
client_socket.send(email.encode())

password = input("password: ")
client_socket.send(password.encode())

#plug class 생성
myPlug = plug()
myPlug.getPattern() 
myPlug.printPattern()

#소켓으로 보내기 위해서 plug 객체 바이트화 필요
myPlugencoding = pickle.dumps(myPlug)
client_socket.sendall(myPlugencoding)

# 서버로부터 데이터 수신
while True:
    # 수신된 데이터 출력
    response = client_socket.recv(1024).decode()
    print(response)

    # 사용자 패턴과 다른 경우 아래의 문장이 수신됨
    answer=""
    if(response == "You are using at the wrong time. Are you sure you are?"):
        #Timeout 되면 실행하는 함수
        def sendans(): 
            #answer=""이기 때문에 turnoff된다
            client_socket.send(answer.encode())
            t.cancel()

            #사용자의 입력 없이 timeout 발생시 프로세스 종료
            client_socket.close()
            os._exit(0)
        
        #60초 동안 input 없으면 timeout
        timeout = 60
        t = threading.Timer(timeout, sendans)

        t.start()
        answer = input(f"You have {timeout} seconds to answer: ")
        t.cancel()
        t.join()

        #입력이 있었다면 입력에 따라 plug 상태 변경
        client_socket.send(answer.encode())
