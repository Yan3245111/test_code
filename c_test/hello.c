#include <stdio.h>
#include <stdlib.h>
# include <string.h>


void get_num() {
    static int num = 0; 
    num++;
    printf("num = %d\n", num);
}

void compare_zhizhen() {
    int a = 10;
    int b = 20;
    int *p1 = &a;
    int *p2 = &b;
    printf("*p1 = %d, *p2 = %d\n", *p1, *p2);
    printf("Address of a: %p, Address of b: %p\n", (void*)&p1, (void*)&p2);
    if (p1 == p2) {
        printf("p1 and p2 point to the same address.\n");
    } else {
        printf("p1 and p2 point to different addresses.\n");
    }
}


int main() {
    // get_num();
    // get_num();
    compare_zhizhen();
    return 0;
}
