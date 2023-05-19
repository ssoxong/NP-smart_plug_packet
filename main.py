from userpattern import user
import time
import datetime as dt
from dateutil.parser import parse
from multiprocessing import Process, Pipe
from os import system

   
#userpattern 생성 
#패턴시간을 어떤형식으로 받지? 범위?   
    


#structor
user1 = user(0,10)   
 
def getpacket(pipe):
    #패킷 캡쳐
    while True:
        #if on 패킷이라면 다음 실행
        #if(off -> on && user1.matchpattern(day,time)):
        #day요일,time 형식 맞춰서
        
        #test
        pktime = dt.datetime.strptime("2023-05-14 14:44", "%Y-%m-%d %H:%M")
        #월 0 ~ 일 6    
        day = pktime.weekday()
        time = pktime.time()
        print(day)
        print(time)
        #test
        
        if(user1.matchpattern(day, time)):
            print("in pattern, wrong using time")
            #사용불가시간에 사용, 클라이언트에게 알림
        
        #on->off, off->on되었을때
        #if
        msg = "change"
        pipe.send(msg)
    
        
        
def checktime(pipe,desired_time):
    start_time = time.time()
    
    while True:
        elapsed_time = time.time() - start_time
        #시간 경과한 경우 알림
        if elapsed_time >= desired_time:
            print("user over limit time.")
            
            # 시간을 초기화
            start_time = time.time()
        
        # 파이프 값을 받으면 시간을 초기화
        if pipe.poll():
            data = pipe.recv()
            print(data)
            start_time = time.time()
            
            
if __name__ == '__main__' :
    a_pipe, b_pipe = Pipe()
    p0 = Process(target = getpacket, args = (a_pipe,))
    p0.start()
    
    p1 = Process(target = checktime, args = (b_pipe.recv(),user1.limitime))
    p1.start()
    
    p0.join()
    p1.join()