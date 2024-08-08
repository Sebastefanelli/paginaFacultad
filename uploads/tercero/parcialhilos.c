#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include <signal.h>

void * hilom(void * p);
void * hiloma(void * p);

typedef struct datoshilos{
    int fd;
    char letra;
}datoshilos;

int main(void){
    int fd= open("abcmin.txt", O_CREAT|O_TRUNC|O_RDWR,0777);
    int fd1= open("abcmay.txt", O_CREAT|O_TRUNC|O_RDWR,0777);

    datoshilos data1={fd1,'A'};
    datoshilos data2={fd,'a'};

    pthread_t hilo1,hilo2;

    pthread_create(&hilo1,NULL,hiloma,&data1);
    pthread_create(&hilo2,NULL,hilom,&data2);

    pthread_join(hilo1,NULL);
    pthread_join(hilo2,NULL);

    raise(SIGUSR1);

    return 0;
}
void * hilom(void * p){
    datoshilos * midh=(datoshilos *)p;
    while (midh->letra<='z'){
        write(midh->fd,&(midh->letra),1);
        midh->letra +=1;
    }
}

void * hiloma(void * p){
    datoshilos * midh=(datoshilos *)p;
    while (midh->letra<='Z'){
        write(midh->fd,&(midh->letra),1);
        midh->letra +=1;
    }
}