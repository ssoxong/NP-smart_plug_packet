from PyP100 import PyP100
import json
import os
from dotenv import load_dotenv
from pattern import plug
import time
import datetime as dt
from dateutil.parser import parse
from multiprocessing import Process, Pipe
from os import system
from packetSniffer import getPacket

load_dotenv()

p100 = PyP100.P100(os.getenv('IP_P100'), os.getenv('email'), os.getenv('password')) #Creates a P100 plug object 환경 변수로 설정한 이메일, 비밀번호 가져오기

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
 
p100.turnOn() #Turns the connected plug on
#p100.turnOff() #Turns the connected plug off
##p100.toggleState() #상태 변경

#p100.turnOnWithDelay(10) #Turns the connected plug on after 10 seconds
#p100.turnOffWithDelay(10) #Turns the connected plug off after 10 seconds

info = p100.getDeviceInfo() #Returns dict with all the device info of the connected plug
# print(info)
if info['result']['device_on']: #info (json형태) 
    print("State: Turn On")
    plugState = 1
else:
    print("State: Turn Off")
    plugState = 0

pluginfo = p100.getDeviceName() #Returns the name of the connected plug set in the app
print(pluginfo)

#user limit time
limit_time = 3

# myPlug pattern 생성
myPlug = plug()
myPlug.getPattern()  
myPlug.printTime()

def checkTime(pipe):
    start_time = time.time()
    
    while True:
        elapsed_time = time.time() - start_time
        #시간 경과한 경우 알림
        if elapsed_time >= limit_time:
            print("user over limit time!!")
            
            # 시간을 초기화
            start_time = time.time()
        
        # 파이프 값을 받았을때 실행
        if pipe.poll():
            data = pipe.recv()
            # print(data)
            # 받은 데이터에서 day, time 추출
            getDay = data.weekday()      #월 0 ~ 일 6   
            getTime = data.time()
            
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

            
            
if __name__ == '__main__' :
    a_pipe, b_pipe = Pipe()
    p0 = Process(target = getPacket, args = (a_pipe,))
    p0.start()
    
    p1 = Process(target = checkTime, args = (b_pipe.recv()))
    p1.start()
    
    p0.join()
    p1.join()