#include <stdio.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include <openssl/sha.h>
#include <signal.h>

void err_proc();
int main(int argc, char** argv)
{
	int clntSd;
	struct sockaddr_in clntAddr;
	int clntAddrLen, readLen, recvByte, maxBuff;
	char rBuff[BUFSIZ];
	if(argc != 3) {
		printf("Usage: %s [IP Address] [Port]\n", argv[0]);
	
	}

	//연결할 소켓 할당
	clntSd = socket(AF_INET, SOCK_STREAM, 0);
	if(clntSd == -1) err_proc();
	printf("==== client program =====\n");

	memset(&clntAddr, 0, sizeof(clntAddr));
	clntAddr.sin_family = AF_INET;
	clntAddr.sin_addr.s_addr = inet_addr(argv[1]);
	clntAddr.sin_port = htons(atoi(argv[2]));

	//서버에 연결
	if(connect(clntSd, (struct sockaddr *) &clntAddr,
			    sizeof(clntAddr)) == -1)
	{
		close(clntSd);
		err_proc();	
	}

	
	read(clntSd, rBuff, BUFSIZ-1);
	/*임의 data
	unsigned char challenge[] = "201931212021304420211806";
	int startcount = 1000000;
	int maxcount = 2147483647; 
	int difficulty = 8;*/

	//unsigned char rBuff[] = "201931212021304420211806\n1000000\n2147483647\n5\n";
	
	//read 받자마자 fork -> child process에서 hash 계산
	int c_pid=fork();
	if(c_pid==0){
		unsigned char challenge[24];
		int startcount;
		int maxcount;
		int difficulty;

		//받은 값을 \n단위로 분리해서 할당
		char *token = strtok(rBuff, "\n");

		strcpy(challenge, token);

		token = strtok(NULL, "\n");
		startcount = atoi(token);

		token = strtok(NULL, "\n");
		maxcount = atoi(token);

		token = strtok(NULL, "\n");
		difficulty = atoi(token);

		for(;startcount<=maxcount;startcount++){
			//nonce to char*
			unsigned char nonce[10];
			sprintf(nonce, "%d",startcount);
			//concal challenge||nonce -> m
			unsigned char m[sizeof(challenge)+sizeof(nonce)];
			memcpy(m, challenge, sizeof(challenge));
			memcpy(m+sizeof(challenge), nonce, sizeof(nonce));

			unsigned char hash[SHA256_DIGEST_LENGTH];
			SHA256(m, sizeof(m)-1, hash);

			//pow검증 변수
			int pow = 1;
			//byte단위로 hash 부분 포인팅할 변수
			int hcnt = 0;

			//hash값 상위 difficulty bit 0여부 확인
			for(int i=0;i<difficulty;hcnt++){
				//hash[i]에 두개의 bit가 나옴 
				//-> difficulty가 홀수일때는 마지막 비트까지 확인하기 위해 파싱 필요
				char byte = hash[hcnt];

				if(i+1==difficulty){
					//홀수일때 확인하기 위해 bit shift
					int firstbit = (byte >> 4) & 0x0F;
					if(firstbit!=0){
						pow=0;
						break;
					}
				}
				
				else if(byte!=0x00){
					pow=0;
					break;
				}
				i+=2;
			}

			//difficulty 조건을 만족하는 해시값 존재시
			if(pow){
				//해시값 찾으면 서버에게 전송
				write(clntSd,nonce,sizeof(nonce));
				/*nonce, hash 출력코드*/
				printf("nonce: %s ", nonce);

				for(int i=0;i<SHA256_DIGEST_LENGTH;i++){
					printf("%02x", hash[i]);
				}
				printf("\n");
				exit(startcount);
			}	
		}		
	}
	//부모 프로세스에서는 자식에서 해시값 찾기 전에 부모에서 연락오면 자식종료
	else{
		int status;

		waitpid(c_pid, &status, 0);
		printf("%d", WEXITSTATUS(status));

		char rBuff[BUFSIZ];
		read(clntSd, rBuff, BUFSIZ);

		printf("Another Server find...\n");
		kill(c_pid, SIGINT);
	}
	
	printf("Working Server Close...\n");
	close(clntSd);

	return 0;
}

void err_proc()
{
	fprintf(stderr,"Error: %s\n", strerror(errno));
	exit(errno);
} 
