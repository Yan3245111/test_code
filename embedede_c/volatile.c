#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>


/* volatile的作用和场景 */
/*
作用：告诉编译器该变量的值可能在程序控制流之外被改变，禁止编译器对其进行优化
    每次访问强制从内存读取/写入

应用场景：硬件寄存器映射，中断共享变量，DMA缓冲区，多线程共享数据
尽量少使用，线程还是使用线程锁更安全，会阻止编译器优化
*/ 

// 中断
volatile int flag = 0;

void interrupt_handle() {
    flag = 1;  // 中断中修改变量
}


int main() {
    while (flag) {  // 主循环必须每次从内存中读取

    }
}


// 多线程无锁情况下
volatile bool stop = false;


void worker_thread() {
    while (!stop) {  // 从内存读

    }
}

void set_thread() {
    stop = !stop;
}


// 内存映射的硬件寄存器
#define STATUS_REG (*(volatile uint32_t*)0x40021000)
#define CONTROL_REG (*(volatile uint32_t*)0x40021004)

void init_hardware() {
    CONTROL_REG = 0x01;
    while ((STATUS_REG & 0x01) == 0) {

    }
}
