#include <stdio.h>
#include <stdint.h>


const int *p;  // 指向常量的指针，*p不可更改（值），p可以（地址）
int const *p1;  // 同上
int *const p2;  // 指向常量的指针，p可更改，*p不可以
const int *const p3;  // 值和地址都不可更改


// static
/*
1.局部静态变量：生命周期延长至程序结束，仅初始化一次
2.全局静态变量/函数：仅限制在当前文件，避免命名冲突
3.静态函数：仅当前文件可用，外部不可调用
*/

void counter() {
    static int count = 0;  // 只初始化一次
    count++;
    printf("count 调用 %d\n", count);
}


static int global_static = 100;  // 全局变量，整个文件可以访问，无法使用extern


void func1() {
    global_static++;
    printf("global static = %d", global_static);
}


static int add(int a, int b) {  // 只有本文件可见，无法使用extern
    return a + b;
}

int public_add(int a, int b) {
    return add(a, b);
}

int main() {
    counter();
    counter();
    func1();
    return 0;
}