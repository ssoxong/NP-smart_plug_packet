from PyP100 import PyP100
from dotenv import load_dotenv
from pattern import plug
from dateutil.parser import parse
from os import system
from datetime import datetime, timedelta
from scapy.all import *
import os
import time
import threading
import queue

#환경변수 로드
load_dotenv()


def main():
    print("start smartplug")
    print(os.getpid())

    global p100
    #Creates a P100 plug object 환경 변수로 설정한 이메일, 비밀번호 가져오기
    p100 = PyP100.P100(os.getenv('IP_P100'), os.getenv('email'), os.getenv('password')) 

    p100.handshake() #Creates the cookies required for further methods
    p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods

    #p100.turnOn() #Turns the connected plug on
    #p100.turnOff() #Turns the connected plug off
    ##p100.toggleState() #상태 변경

    #p100.turnOnWithDelay(10) #Turns the connected plug on after 10 seconds
    #p100.turnOffWithDelay(10) #Turns the connected plug off after 10 seconds

    global plugState

    info = p100.getDeviceInfo() #연결된 플러그에 대한 정보를 info에 저장
    if info['result']['device_on']: #info (json형태) 
        print("State: Turn On")
        plugState = 1   #init plugState
    else:
        print("State: Turn Off")
        plugState = 0   #init plugState

    pluginfo = p100.getDeviceName() #Returns the name of the connected plug set in the app
    print(pluginfo)

    # myPlug pattern 생성
    print("create plug")
    global myPlug

    myPlug = plug()
    myPlug.getPattern() 
    myPlug.printPattern()

def checkTime(buffer):
    global p100
    global plugState
    global myPlug

    print("Start checkTime")
    start_time = time.time()
    
    while True:
        # 경과한 시간
        elapsed_time = time.time() - start_time
        
        # limit time 설정
        limit_time = 60     #60초
        
        if elapsed_time >= limit_time:      #limit time을 초과한 경우 알림
            print("!\n!\n!!!!!!!!!!!!!!!!!!user over limit time!!!!!!!!!!!!!!!!!!\n!\n!")
            
            # 시간을 초기화
            start_time = time.time()
        
        # 버퍼에 값이 있을때 실행
        while not buffer.empty(): 
            
            #버퍼 안의 값을 data에 가져옴
            data = datetime.strptime(buffer.get(), '%Y-%m-%d %H:%M')
            print("check Time: ", data)

            # 받은 데이터에서 요일, 시간 추출
            getDay = data.weekday()      # 요일 월 0 ~ 일 6   
            getTime = int(data.strftime("%H")) # 시간 0~23
    
            info = p100.getDeviceInfo() #Returns dict with all the device info of the connected plug
            if info['result']['device_on']: #info (json형태) 
                print("State: Turn On")
                if plugState == 0:      # 이전에 off 상태 였다면
                    plugState = 1       # change the plugState
                    start_time = time.time()    #시간 초기화
                    
                    #사용불가시간에 사용함, 클라이언트에게 알림
                    if(myPlug.matchPattern(getDay, getTime)):   
                        print("!\n!\n!!!!!!!!!!!!!!!!!!wrong using time!!!!!!!!!!!!!!!!!!!!\n!\n!")
                        
                        # 사용 종료
                        p100.turnOff()
                        plugState = 0;  
                        
            else:
                print("State: Turn Off")
                if plugState == 1:      # 이전에 on 상태 였다면
                    plugState = 0       # change the plugState
                    start_time = time.time()    #시간 초기화


def getPacket(buffer):
    print("Start getPacket")
    # lastpacket 시간 스니퍼 실행 시점으로 초기화
    global lastpacket
    lastpacket = datetime.now()
    print("패킷 캡쳐 시작: ", lastpacket)
    
    # start sniff...
    # iface = '해당 네트워크 인터페이스 이름'
    sniff(iface='Microsoft Wi-Fi Direct Virtual Adapter #4', prn=lambda pkt: packet_callback(pkt, buffer),
          filter=f'''ip host {os.getenv('IP_p100')} 
          and not ip host {os.getenv('IP_local')}''')
    
# 패킷 캡쳐 콜백 함수
def packet_callback(packet, buffer):
    global lastpacket  # 전역 변수로 선언
    time_scope = timedelta(seconds=2)

    # 패킷이 처음 발생하고 4초가 지나지 않으면 무시
    # 한 동작 당 한꺼번에 여러개의 패킷이 발생하기 때문에...
    if datetime.fromtimestamp(packet.time) < lastpacket+time_scope:
        return
    else:
        raw_packet_time = datetime.fromtimestamp(packet.time)
        lastpacket = raw_packet_time
        
        # packet_time에 지정된 형식으로 저장
        packet_time = raw_packet_time.strftime("%Y-%m-%d %H:%M")

        print("Packet time:", packet_time)
        print(packet.summary())     # 캡처한 패킷 보여주기 
        buffer.put(packet_time)     # 버퍼에 넣기

if __name__ == "__main__":
    main()
    
    # for inter thread communication ...
    # 가장 마지막에 받은 패킷을 사용하기 위해 LIFO 이용
    buffer = queue.LifoQueue() 

    # 멀티스레드 사용
    # th0 는 패킷을 캡쳐하는 스레드
    # th1 는 가져온 패킷을 검사하는 스레드
    th0 = threading.Thread(target=getPacket, args=(buffer,))
    th0.start()
    th1 = threading.Thread(target=checkTime, args=(buffer,))
    th1.start()

    th0.join()
    th1.join()