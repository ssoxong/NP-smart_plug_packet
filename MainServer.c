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

#define MAX_CLIENTS 3
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
	clock_t start,end;

	//challenge값
	unsigned char challenge[24] = {"201931212021304420211806"};
	//sending buffer
	unsigned char buff[3][BUFFER_SIZE] = {
		"201931212021304420211806\n0\n1431655765\n5\n",
		"201931212021304420211806\n1431655766\n2863311530\n5\n",
		"201931212021304420211806\n2863311531\n4294967295\n5\n"
	};

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
				start = clock();
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
                memset(buffer, 0, BUFFER_SIZE);
                valread = recv(client_socket, buffer, BUFFER_SIZE, 0);
				end = clock();

                if (valread <= 0) {
                    // 클라이언트 연결 종료 처리
                    printf("클라이언트 연결이 종료되었습니다\n");
                    close(client_socket);
                    client_sockets[i] = -1;
                } else {
                    // 클라이언트로부터 메시지 수신

                    if (first_response_idx == -1) {
                        // 최초 응답을 받은 클라이언트
                        first_response_idx = i;
                    } else if (i != first_response_idx) {
                        // 최초 응답 이후 다른 클라이언트에게 응답이 온 경우 무시
                        continue;
                    }

                    // 모든 클라이언트에게 메시지 전송
                    for (int j = 0; j < MAX_CLIENTS; j++) {
                        int client = client_sockets[j];
                        if (client > 0) {
                            send(client, "nonce를 구했습니다.\n", strlen("nonce를 구했습니다.\n"), 0);
                        }
                    }
				
					//결과값 계산
					unsigned char m[sizeof(challenge)+sizeof(buffer)];
					memcpy(m, challenge, sizeof(challenge));
					memcpy(m + sizeof(challenge), buffer, sizeof(buffer));

					unsigned char hash[SHA256_DIGEST_LENGTH];
					SHA256(m, sizeof(m) - 1, hash);

					printf("nonce : %s , 소요시간 : %lf\n", buffer, (double)(end-start) / CLOCKS_PER_SEC);
					//hash 출력
					for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
                    printf("%02x", hash[i]);
					}
					printf("\n");

                }
            }
        }
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

