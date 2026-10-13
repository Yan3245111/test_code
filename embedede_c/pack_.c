#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>


void is_little_endian() {
    union  // 成员是共享内存
    {
        /* data */
        int i;
        char c;
    } u;
    u.i = 1;
    printf("%d\n", u.c == 1);  // 1小端 0大端 
}


int main() {
    is_little_endian();
    return 0;
}