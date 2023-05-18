from PyP100 import PyP100
import json
import os
from dotenv import load_dotenv
load_dotenv()

p100 = PyP100.P100(os.getenv('IP_P100'), os.getenv('email'), os.getenv('password')) #Creates a P100 plug object 환경 변수로 설정한 이메일, 비밀번호 가져오기

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
 
#p100.turnOn() #Turns the connected plug on
#p100.turnOff() #Turns the connected plug off
##p100.toggleState() #상태 변경

#p100.turnOnWithDelay(10) #Turns the connected plug on after 10 seconds
#p100.turnOffWithDelay(10) #Turns the connected plug off after 10 seconds

info = p100.getDeviceInfo() #Returns dict with all the device info of the connected plug
if info['result']['device_on']: #info (json형태) 
    print("State: Turn On")
else:
    print("State: Turn Off")

p100.getDeviceName() #Returns the name of the connected plug set in the app