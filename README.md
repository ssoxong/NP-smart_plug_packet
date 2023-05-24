# NP-Project
---
### Smart plug packet
- [x] scapy 로 패킷 끌어오기
- [x] scapy 에서 발생하는 패킷 분석하기
- [x] dotenv 오류 해결하기
- [ ] 보고서 작성

### ver. Modify MutiThread && datetime cmp error
멀티 프로세스 + 파이프 -> 공유자원 (p100, myPlug, plugState) 이용 불가
--> 멀티 스레드 + LIFO 큐 (파이썬에는 스택 없음)
파일로 나뉜 함수 하나로 합치기 (이거는 오류때문에 그랬는데 대충 해결한 것 같아서 분리해도 상관 없을듯
- 전역변수만 잘 선언해주면 됨

되는 것 같은데... patten 코드에서 matchpattern 에서 비교 에러남
이거 고치면 될듯
...

while not buffer.empty()
-> 패킷 분석하면서 check 스레드도 돌고 있으니까 스레드에서 처리하는 도중에 패킷 쌓이면 가장 최신거 패턴매치 + 초기화
