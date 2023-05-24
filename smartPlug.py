from PyP100 import PyP100
from dotenv import load_dotenv
from pattern import plug
from dateutil.parser import parse

from os import system
from datetime import datetime, timedelta
#from packetSniffer import getPacket
from scapy.all import *
import os
import time
load_dotenv()

global plugState
global myPlug

def checkTime(pipe):
    print("Start checkTime")
    start_time = time.time()
    
    while True:
        # elapsed_time = time.time() - start_time
        # #시간 경과한 경우 알림
        # limit_time = 3
        # if elapsed_time >= limit_time:
        #     print("user over limit time!!")
            
        #     # 시간을 초기화
        #     start_time = time.time()
        
        # 파이프 값을 받았을때 실행
        if pipe.recv():
            data = datetime.strptime(pipe.recv(), '%Y-%m-%d %H:%M')
            print("check Time: ", data)
            # 받은 데이터에서 day, time 추출
            getDay = data.weekday()      #월 0 ~ 일 6   
            getTime = data.time()
            

            p100 = PyP100.P100(os.getenv('IP_P100'), os.getenv('email'), os.getenv('password')) #Creates a P100 plug object 환경 변수로 설정한 이메일, 비밀번호 가져오기

            p100.handshake() #Creates the cookies required for further methods
            p100.login()
            info = p100.getDeviceInfo() #Returns dict with all the device info of the connected plug
            # print(info)
            if info['result']['device_on']: #info (json형태) 
                print("State: Turn On")
                # 이전에 off 상태 였다면
                if plugState == 0:
                    plugState = 1
                    start_time = time.time()    #시간 초기화
                    if(myPlug.matchPattern(getDay, getTime)):
                        print("wrong using time!!")
                        #사용불가시간에 사용함, 클라이언트에게 알림
            else:
                print("State: Turn Off")
                # 이전에 on 상태 였다면
                if plugState == 1:
                    plugState = 0
                    start_time = time.time()    #시간 초기화


def getPacket(pipe):
    print("Start getPacket")
    # lastpacket 시간 스니퍼 실행 시점으로 초기화
    global lastpacket
    lastpacket = datetime.now()
    print("패킷 캡쳐 시작: ", lastpacket)

    sniff(iface='로컬 영역 연결* 2', prn=lambda pkt: packet_callback(pkt, pipe),
          filter=f'''ip host {os.getenv('IP_p100')} 
          and not ip host {os.getenv('IP_local')}''')
    
# 패킷 캡쳐 콜백 함수
def packet_callback(packet, pipe):
    global lastpacket  # 전역 변수로 선언
    time_scope = timedelta(seconds=2)

    # 패킷이 처음 발생하고 4초가 지나지 않으면 무시
    # 한 동작 당 한꺼번에 여러개의 패킷이 발생하기 때문에...
    if datetime.fromtimestamp(packet.time) < lastpacket+time_scope:
        return
    else:
        raw_packet_time = datetime.fromtimestamp(packet.time)
        lastpacket = raw_packet_time
        packet_time = raw_packet_time.strftime("%Y-%m-%d %H:%M")

        print("Packet time:", packet_time)
        print(packet.summary())  # 캡처한 패킷 보여주기 
        pipe.send(packet_time)


#여기 없으면 이상하게 Pipe 오류남..
from multiprocessing import Process, Pipe
                  
if __name__ == '__main__' :
    print("start smartplug")
    print(os.getpid())
    p100 = PyP100.P100(os.getenv('IP_P100'), os.getenv('email'), os.getenv('password')) #Creates a P100 plug object 환경 변수로 설정한 이메일, 비밀번호 가져오기

    p100.handshake() #Creates the cookies required for further methods
    p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
    
    #p100.turnOn() #Turns the connected plug on
    #p100.turnOff() #Turns the connected plug off
    ##p100.toggleState() #상태 변경

    #p100.turnOnWithDelay(10) #Turns the connected plug on after 10 seconds
    #p100.turnOffWithDelay(10) #Turns the connected plug off after 10 seconds

    info = p100.getDeviceInfo() #연결된 플러그에 대한 정보를 info에 저장
    if info['result']['device_on']: #info (json형태) 
        print("State: Turn On")
        plugState = 1
    else:
        print("State: Turn Off")
        plugState = 0

    pluginfo = p100.getDeviceName() #Returns the name of the connected plug set in the app
    print(pluginfo)

    # myPlug pattern 생성
    print("create plug")
    myPlug = plug()
    myPlug.getPattern()  
    myPlug.printTime()

    get_pipe, check_pipe = Pipe()

    p0 = Process(target = getPacket, args = (get_pipe,))
    p0.start()
    p1 = Process(target = checkTime, args = (check_pipe,))
    p1.start()

    p0.join()
    p1.join()