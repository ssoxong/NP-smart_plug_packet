#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <openssl/sha.h>
#include <limits.h>

#define MAX_CLIENTS 2
#define BUFFER_SIZE 1024

int main() {
    int server_fd, client_sockets[MAX_CLIENTS];
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_size = sizeof(client_addr);
    unsigned char buffer[BUFFER_SIZE];
    fd_set readfds;
    int max_fd, activity, i, valread;
    int client_count = 0;
    int first_response_idx = -1;
    time_t start_time, end_time;

	//challenge값
	char challenge[1024];
    printf("challenge: ");
    scanf("%s",challenge);

    //difficulty
    int difficulty;
    printf("difficulty: ");
    scanf("%d",&difficulty);

    //challenge + startcount + endcount + difficulty

    //전처리
    int startcnt=0;
    
    int endcnt = INT_MAX/MAX_CLIENTS; //intmax/2

    char m[2048];
    char buff[MAX_CLIENTS][2048];

    for(int i=0;i<MAX_CLIENTS;i++){

        //초기화
        memset(m, 0, sizeof(m));

        sprintf(m, "%s\n%d\n%d\n%d", challenge, startcnt, endcnt, difficulty);

        startcnt = endcnt+1;
        endcnt = endcnt+INT_MAX/MAX_CLIENTS;
        if(endcnt>INT_MAX)
            endcnt = INT_MAX;

        strcpy(buff[i],m);
    }

    // 서버 소켓 생성
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("소켓 생성 실패");
        exit(1);
    }

    // 서버 주소 설정
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8000);

    // 서버에 바인딩
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("바인딩 실패");
        exit(1);
    }

    // 연결 대기
    if (listen(server_fd, MAX_CLIENTS) < 0) {
        perror("연결 대기 실패");
        exit(1);
    }

    printf("서버 시작\n");

    // 연결된 클라이언트들 초기화
    for (i = 0; i < MAX_CLIENTS; i++) {
        client_sockets[i] = -1;
    }

    while (1) {
        // 파일 디스크립터 집합 초기화
        FD_ZERO(&readfds);
        FD_SET(server_fd, &readfds);
        max_fd = server_fd;

        // 연결된 클라이언트들을 파일 디스크립터 집합에 추가
        for (i = 0; i < MAX_CLIENTS; i++) {
            int client_socket = client_sockets[i];
            if (client_socket > 0) {
                FD_SET(client_socket, &readfds);
                if (client_socket > max_fd) {
                    max_fd = client_socket;
                }
            }
        }

        // 파일 디스크립터 감시 및 I/O 대기
        activity = select(max_fd + 1, &readfds, NULL, NULL, NULL);
        if (activity < 0) {
            perror("select 에러");
            exit(1);
        }

        // 새로운 클라이언트 연결 처리
        if (FD_ISSET(server_fd, &readfds)) {
            client_sockets[client_count] = accept(server_fd, (struct sockaddr *)&client_addr, &addr_size);
            if (client_sockets[client_count] < 0) {
                perror("클라이언트 연결 실패");
                exit(1);
            }

            printf("클라이언트가 연결되었습니다\n");

            client_count++;

            //모두 연결되면 일괄 전송
            if (client_count >= MAX_CLIENTS) {
                printf("all connected... sending challenge\n");
				start_time = time(NULL);
				for (int j = 0; j < MAX_CLIENTS; j++) {
					send(client_sockets[j], buff[j], sizeof(buff[j]),0);
				}
				continue;
            }
        }

        // 클라이언트로부터 메시지 수신 및 처리
        for (i = 0; i < MAX_CLIENTS; i++) {
            int client_socket = client_sockets[i];
            if (FD_ISSET(client_socket, &readfds)) {
                char nonce[11];

                valread = recv(client_socket, nonce, sizeof(nonce), 0);
                //printf("recv nonce: %s\n", nonce);
				end_time = time(NULL);

                if (valread <= 0) {
                    // 클라이언트 연결 종료 처리
                    printf("클라이언트 연결이 종료되었습니다\n");
                    close(client_socket);
                    client_sockets[i] = -1;
                    client_count--;
                    
                } else {
                    // 클라이언트로부터 메시지 수신

                    if (first_response_idx == -1) {
                        // 최초 응답을 받은 클라이언트
                        first_response_idx = i;
                    } else if (i != first_response_idx) {
                        // 최초 응답 이후 다른 클라이언트에게 응답이 온 경우 무시
                        continue;
                    }

                    
					//결과값 계산
					char m[2048]={0,};
                    strcat(m,challenge);
                    strcat(m,nonce);

					unsigned char hash[SHA256_DIGEST_LENGTH];
					SHA256(m, sizeof(m)-1, hash);

                    double totaltime = difftime(end_time, start_time);

					printf("nonce : %s, 소요시간 : %.2f초\n", nonce, totaltime);
					//hash 출력
					for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
                        printf("%02x", hash[i]);
					}
					printf("\n");

                    int hcnt=0;
                    int pow=1;
                    
                    //client가 계산한 nonce 확인
                    for (int k = 0; k < difficulty; hcnt++) {
                        //hash[i]에 두개의 bit가 나옴
                        //-> difficulty가 홀수일때는 마지막 비트까지 확인하기 위해 파싱 필요
                        char byte = hash[hcnt];

                        if (k + 1 == difficulty) {
                            //홀수일때 확인하기 위해 bit shift
                            int firstbit = (byte >> 4) & 0x0F;
                            if (firstbit != 0) {
                                pow = 0;
                                break;
                            }
                        } else if (byte != 0x00) {
                            pow = 0;
                            break;
                        }
                        k += 2;
                    }

                    if(pow){
                        printf("적절한 nonce입니다.\n");
                        // 모든 클라이언트에게 메시지 전송
                        for (int j = 0; j < MAX_CLIENTS; j++) {
                            int client = client_sockets[j];
                            if(i==j){
                                send(client, "적절한 nonce입니다.", strlen("적절한 nonce입니다."),0);
                            }
                            if (client > 0) {
                                send(client, "다른 working server가 nonce를 구했습니다.", strlen("다른 working server가 nonce를 구했습니다."), 0);
                            }
                        }
                    
                    }
                    else{
                        printf("잘못된 nonce입니다.\n");
                        continue;
                    }

                }
            }
        }
        if(client_count==0) break;
    }

    // 연결 종료
    for (i = 0; i < MAX_CLIENTS; i++) {
        int client_socket = client_sockets[i];
        if (client_socket > 0) {
            close(client_socket);
        }
    }
    close(server_fd);

    return 0;
}
