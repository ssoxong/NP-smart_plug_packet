import socket
import argparse
import pickle
from pattern import plug
import datetime
import threading
import os
import sys


# 서버 정보
server_host = '127.0.0.1'
server_port = 9002

# 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_port))

# 서버에 데이터 전송
print("Server connect!!")

IP_P100 = input("IP P100: ")
email = input("email: ")
password = input("password: ")
client_socket.send(IP_P100.encode())
client_socket.send(email.encode())
client_socket.send(password.encode())

myPlug = plug()
myPlug.getPattern() 
myPlug.printPattern()

myPlugencoding = pickle.dumps(myPlug)

client_socket.sendall(myPlugencoding)

# 서버로부터 데이터 수신
while True:
    response = client_socket.recv(1024).decode()

    # 수신된 데이터 출력
    print(response)

    # 사용자 패턴과 다른 경우
    answer=""
    if(response == "You are using at the wrong time. Are you sure you are?"):
        def sendans(): #Timeout 되면 실행하는 함수
            #answer=""이기 때문에 turnoff된다
            client_socket.send(answer.encode())
            t.cancel()

            #사용자의 입력 없이 timeout 발생시 프로세스 종료
            client_socket.close()
            os._exit(0)
        
        timeout = 60
        #60초 동안 input 없으면 timeout
        t = threading.Timer(timeout, sendans)

        t.start()
        answer = input(f"You have {timeout} seconds to answer: ")
        t.cancel()
        t.join()
        client_socket.send(answer.encode())


# 연결 종료
client_socket.close()
