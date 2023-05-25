import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

from scapy.all import *

# 패킷 캡처 시작
# sniff(iface='로컬 영역 연결* 2', prn=packet_callback,
#       filter=f'''ip host {os.getenv('IP_p100')} 
#       and not ip host {os.getenv('IP_local')}''')

def getPacket(pipe):
    # lastpacket 시간 스니퍼 실행 시점으로 초기화
    global lastpacket
    lastpacket = datetime.now()
    print("패킷 캡쳐 시작: ", lastpacket)

    sniff(iface='로컬 영역 연결* 4', prn=lambda pkt: packet_callback(pkt, pipe),
          filter=f'''ip host {os.getenv('IP_p100')} 
          and not ip host {os.getenv('IP_local')}''')
    
# 패킷 캡쳐 콜백 함수
def packet_callback(packet,pipe):
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
    