#include <stdio.h>
#include <stdlib.h>
#include <string.h>


// 方法一：使用malloc拷贝
char *get_text1() {
    char *text;
    text = (char *)malloc(100 * sizeof(char)); // 分配内存
    sprintf(text, "Hello, World!"); // 将字符串写入text
    return text; // 返回指向text的指针
}

// 方法二：使用指针传进入，再拿回来
char get_text2(char *text) {
    sprintf(text, "Hello, World!"); // 将字符串写入text
}

int main() {
    // 方法一
    char *result = get_text1(); // 获取字符串
    printf("%s\n", result); // 输出字符串
    free(result); // 释放内存

    // 方法二
    char buffer[100]; // 定义一个缓冲区
    get_text2(buffer); // 将字符串写入缓冲区
    printf("%s\n", buffer); // 输出字符串
    return 0;
}