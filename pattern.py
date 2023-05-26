import datetime as dt
import time

class plug():

    def __init__(self):
        print(f"-------------사용자가 사용하는 시간 입력-----------------")

    def getPattern(self):
        days_of_week = ["월", "화", "수", "목", "금", "토", "일"]

        # Receive usage patterns by day of the week
        for day in days_of_week :
            usage_time = input(f"{day}요일의 사용하는 시작 시간, 끝시간을 입력하세요. ".format(day))
            str_list = usage_time.split()
            str1 = str_list[0]
            str2 = str_list[1]
            
            if(day=="월") :
                self.monstime = int(str1)
                self.monetime = int(str2)  
            if(day =="화"):
                self.tuestime = int(str1)
                self.tueetime = int(str2) 
            if(day =="수"):
                self.wedstime = int(str1)
                self.wedetime = int(str2) 
            if(day =="목"):
                self.thrstime = int(str1)
                self.thretime = int(str2)
            if(day =="금"):
                self.fristime = int(str1)
                self.frietime = int(str2)  
            if(day =="토"):
                self.satstime = int(str1)
                self.satetime = int(str2) 
            if(day =="일"):
                self.sunstime = int(str1)
                self.sunetime = int(str2)                    
                
    def printPattern(self):
        print(f"월요일 start time: {self.monstime}, end time: {self.monetime}")
        print(f"화요일 start time: {self.tuestime}, end time: {self.tueetime}")
        print(f"수요일 start time: {self.wedstime}, end time: {self.wedetime}")
        print(f"목요일 start time: {self.thrstime}, end time: {self.thretime}")
        print(f"금요일 start time: {self.fristime}, end time: {self.frietime}")
        print(f"토요일 start time: {self.satstime}, end time: {self.satetime}")
        print(f"일요일 start time: {self.sunstime}, end time: {self.sunetime}")

    #텍스트 파일로 부터 패턴 받기
    def getPattern_file(self):

        file = open("usagetime.txt", "r")

        line = file.readline()

        linecnt = 1

        while line:
            str_list = line.split()
            str1 = str_list[0]
            str2 = str_list[1]
            
            if(linecnt == 1) :
                self.monstime = str1
                self.monetime = str2 
            if(linecnt == 2):
                self.tuestime = str1
                self.tueetime = str2 
            if(linecnt == 3):
                self.wedstime = str1
                self.wedetime = str2
            if(linecnt == 4):
                self.thrstime = str1
                self.thretime = str2 
            if(linecnt == 5):
                self.fristime = str1
                self.frietime = str2   
            if(linecnt == 6):
                self.satstime = str1
                self.satetime = str2 
            if(linecnt == 7):
                self.sunstime = str1
                self.sunetime = str2  

            linecnt += 1
            line = file.readline()
            
        file.close()

    #패턴의 시각과 비교하여 올바른지 탐지
    def matchPattern(self,day,time):
        if day == 0:
            if self.monstime>time or time>self.monetime:
                return True
        elif day == 1:
            if self.tuestime>time or time>self.tueetime:
                return True
        elif day == 2:
            if self.wedstime>time or time>self.wedetime:
                return True
        elif day == 3:
            if self.thrstime>time or time>self.thretime:
                return True
        elif day == 4:
           if self.fristime>time or time>self.frietime:
                return True
        elif day == 5:
            if self.satstime>time or time>self.satetime:
                return True
        elif day == 6:
            if self.sunstime>time or time>self.sunetime:
                return True
        
        else : return False
