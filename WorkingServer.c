#include <stdio.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include <openssl/sha.h>
#include <signal.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/select.h>

void err_proc();

int main(int argc, char** argv)
{
    int clntSd;
    struct sockaddr_in clntAddr;
    int clntAddrLen, readLen, recvByte, maxBuff;
    char rBuff[2048];
    if(argc != 3) {
        printf("Usage: %s [IP Address] [Port]\n", argv[0]);
        exit(1);
    }

    //연결할 소켓 할당
    clntSd = socket(AF_INET, SOCK_STREAM, 0);
    if(clntSd == -1) err_proc();
    printf("==== client program =====\n");

    memset(&clntAddr, 0, sizeof(clntAddr));
    clntAddr.sin_family = AF_INET;
    clntAddr.sin_addr.s_addr = inet_addr(argv[1]);
    clntAddr.sin_port = htons(atoi(argv[2]));

    int flags = fcntl(clntSd, F_GETFL, 0);
    fcntl(clntSd, F_SETFL, flags | O_NONBLOCK);

    //서버에 연결
    if (connect(clntSd, (struct sockaddr *) &clntAddr, sizeof(clntAddr)) == -1) {
        if (errno != EINPROGRESS) {
            close(clntSd);
            err_proc();
        }

        fd_set writeSet;
        FD_ZERO(&writeSet);
        FD_SET(clntSd, &writeSet);

        int result = select(clntSd + 1, NULL, &writeSet, NULL, NULL);
        if (result < 0) {
            perror("select");
            exit(1);
        } else if (result == 0) {
            fprintf(stderr, "Connection timeout\n");
            exit(1);
        }
    }

    printf("Connected..\n");

    while (1) {
        int nbytes = read(clntSd, rBuff, BUFSIZ - 1);

        if(nbytes > 0) {
            printf("Data Accepted..\n");
            break;
        } else if (nbytes == 0) {
            fprintf(stderr, "Connection closed by the server\n");
            exit(1);
        }
    }

    /*임의 data
    unsigned char challenge[] = "201931212021304420211806";
    int startcount = 1000000;
    int maxcount = 2147483647;
    int difficulty = 8;*/

    //unsigned char rBuff[] = "201931212021304420211806\n1000000\n2147483647\n5\n";

    //read 받자마자 fork -> child process에서 hash 계산
    int c_pid = fork();
    if (c_pid == 0) {
        unsigned char challenge[24];
        unsigned int startcount;
        unsigned int maxcount;
        int difficulty;

        //받은 값을 \n단위로 분리해서 할당
        char *token = strtok(rBuff, "\n");

        strcpy(challenge, token);

        token = strtok(NULL, "\n");
        startcount = atol(token);

        token = strtok(NULL, "\n");
        maxcount = atol(token);

        token = strtok(NULL, "\n");
        difficulty = atoi(token);

        for (; startcount <= maxcount; startcount++) {
            //nonce to char*
            char nonce[11];
            sprintf(nonce, "%d", startcount);

            //concal challenge||nonce -> m
            char m[2048]={0,};
            strcat(m,challenge);
            strcat(m,nonce);

            unsigned char hash[SHA256_DIGEST_LENGTH];
            SHA256(m, sizeof(m) - 1, hash);

            // for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
            //         printf("%02x", hash[i]);
            //     }
            //     printf("\n");

            //pow검증 변수
            int pow = 1;
            //byte단위로 hash 부분 포인팅할 변수
            int hcnt = 0;

            //hash값 상위 difficulty bit 0여부 확인
            for (int i = 0; i < difficulty; hcnt++) {
                //hash[i]에 두개의 bit가 나옴
                //-> difficulty가 홀수일때는 마지막 비트까지 확인하기 위해 파싱 필요
                char byte = hash[hcnt];

                if (i + 1 == difficulty) {
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
                i += 2;
            }

            //difficulty 조건을 만족하는 해시값 존재시
            if (pow) {
                //해시값 찾으면 서버에게 전송
                printf("m: %s\n",m);
                write(clntSd, nonce, sizeof(nonce));
                /*nonce, hash 출력코드*/
                printf("nonce: %s\n", nonce);

                for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
                    printf("%02x", hash[i]);
                }
                printf("\n");
                exit(startcount);
            }
        }
    } else {
        //논블로킹으로 server의 read 기다림
        char rBuff[BUFSIZ];

        while (1) {
            int nbytes = read(clntSd, rBuff, BUFSIZ - 1);

            if(nbytes > 0) {
                printf("%s", rBuff);
                kill(c_pid, SIGINT);
                break;
            } else if (nbytes == 0) {
                fprintf(stderr, "Connection closed by the server\n");
                exit(1);
            }
        }
    }

    printf("Working Server Close...\n");
    close(clntSd);

    return 0;
}

void err_proc()
{
    fprintf(stderr, "Error: %s\n", strerror(errno));
    exit(errno);
}
