from PyP100 import PyP100
from dotenv import load_dotenv
load_dotenv()
from pattern import plug
from dateutil.parser import parse

from os import system
from datetime import datetime, timedelta
#from packetSniffer import getPacket
from scapy.all import *
import os
import time

def main(IP_P100, email, pwd, myPluglocal):
    global p100
    p100 = PyP100.P100(IP_P100, email, pwd)

    p100.handshake()
    p100.login()

    global plugState
    global myPlug
    myPlug = myPluglocal #파라미터로 받은 값 global선언

    info = p100.getDeviceInfo() #연결된 플러그에 대한 정보를 info에 저장
    if info['result']['device_on']: #info (json형태) 
        print("State: Turn On")
        plugState = 1
    else:
        print("State: Turn Off")
        plugState = 0

    pluginfo = p100.getDeviceName() #Returns the name of the connected plug set in the app
    print(pluginfo)


def checkTime(buffer, clnt):
    global p100
    global plugState
    global myPlug

    print("Start checkTime")    
    while True:        
        # 파이프 값을 받았을때 실행
        while not buffer.empty(): 
            data = datetime.strptime(buffer.get(), '%Y-%m-%d %H:%M')
            # buffer.clear() #버퍼 초기화
            print("check Time: ", data)

            # 받은 데이터에서 day, time 추출
            getDay = data.weekday()      #월 0 ~ 일 6   
            getTime = int(data.strftime("%H"))
            # print(getDay)
            # print(getTime)
    
            info = p100.getDeviceInfo() #현재 연결되어있는 plug 정보 (json형태)
            # print(info)
            if info['result']['device_on']: #info (json형태) 
                print("State: Turn On")
                # 이전에 off 상태 였다면
                if plugState == 0:
                    plugState = 1

                     #사용불가시간에 사용함, 클라이언트에게 알림
                    if(myPlug.matchPattern(getDay, getTime)):
                        status = "You are using at the wrong time. Are you sure you are?" 
                        clnt.send(status.encode())

                        answer  = None

                        while True:
                            if(clnt):
                                answer = clnt.recv(1024).decode()
                                if(answer == "Yes"): 
                                    break
                                else :
                                    status = "Turn off the plug"
                                    clnt.send(status.encode())
                                    p100.turnOff()
                                    plugState=0
                                    break
                            
            else:
                print("State: Turn Off")
                # 이전에 on 상태 였다면
                if plugState == 1:
                    plugState = 0


def getPacket(buffer,addr):
    print("Start getPacket")
    # lastpacket 시간 스니퍼 실행 시점으로 초기화
    global lastpacket
    lastpacket = datetime.now()
    print("패킷 캡쳐 시작: ", lastpacket)

    #공유자원에서 P100의 ip 불러오기
    sniff(iface='로컬 영역 연결* 2', prn=lambda pkt: packet_callback(pkt, buffer,addr),
          filter=f'''ip host {p100.getDeviceInfo()['result']['ip']} 
          and not ip host {os.getenv('IP_local')}''')
    
    
# 패킷 캡쳐 콜백 함수
def packet_callback(packet, buffer,addr):
    global lastpacket  # 전역 변수로 선언
    time_scope = timedelta(seconds=2)

    # 패킷이 처음 발생하고 2초가 지나지 않으면 무시
    # 한 동작 당 한꺼번에 여러개의 패킷이 발생하기 때문에...
    if datetime.fromtimestamp(packet.time) < lastpacket+time_scope:
        return
    else:
        raw_packet_time = datetime.fromtimestamp(packet.time)
        lastpacket = raw_packet_time
        packet_time = raw_packet_time.strftime("%Y-%m-%d %H:%M")

        print("Packet time:", packet_time)
        print("Client ",addr,": ",packet.summary())  # 캡처한 패킷 보여주기 
        buffer.put(packet_time)

if __name__ == "__main__":
    main()