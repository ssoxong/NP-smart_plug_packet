import datetime as dt
import time

class user():

    #,tuetime,wedtime,thutime,fritime,sattime,suntime

    #user 요일별 pattern 저장
    def __init__(self,montime,limittime):
        self.montime = montime
        # self.tuetime = 
        # self.montime = 
        # self.montime = 
        # self.montime = 
        # self.montime = 
        # self.montime = 
        self.limitime = limittime
    
    
    #사용하지 않는 시각에 사용한경우 return1
    def matchpattern(self,day,time):
        if day == 0:
            if time == self.montime:
                return 1
        # elif day == 1:
        #     if time == tuetime:
        #         return 1
        # elif day == 2:
        #     if time == tuetime:
        #         return 1
        # elif day == 3:
        #     if time == tuetime:
        #         return 1
        # elif day == 4:
        #     if time == tuetime:
        #         return 1
        # elif day == 5:
        #     if time == tuetime:
        #         return 1
        # elif day == 6:
        #     if time == tuetime:
        #         return 1
        
        else : return 0
            