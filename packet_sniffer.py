import os
from dotenv import load_dotenv
load_dotenv()

from scapy.all import *

# 패킷 캡쳐 콜백 함수
def packet_callback(packet):
    print(packet.summary()) #캡처한 패킷 보여주기

# 패킷 캡쳐 시작

sniff(iface='로컬 영역 연결* 2', prn=packet_callback, #핫스팟 interface이름
      filter=f'''ip host {os.getenv('IP_p100')} 
      and not ip host {os.getenv('IP_local')}''') #P100에서 발생하는 패킷만 캡처, turn on/off 확인용 패킷 전송하는 ip 제외


# iface는 캡쳐할 네트워크 인터페이스를 지정합니다.
# prn은 패킷이 캡쳐될 때마다 호출될 함수를 지정합니다.
# filter는 원하는 패킷 필터링을 위한 BPF(Berkeley Packet Filter) 식을 지정합니다.
# 예를 들어 'tcp'로 필터링하면 TCP 패킷만 캡쳐됩니다.