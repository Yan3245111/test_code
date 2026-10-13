#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>


/*
指针未初始化，变成野指针
指针赋值Null 空指针 明确指向0
*/

// 野指针错误示例
int *p;  //野指针，未赋值
*p = 10;  //写入随机地址

// 正确示例
int a = 10;
int *p = &a;


// 访问已经释放的内存
void test() {
    int *p = (int*)malloc(sizeof(int));
    free(p);
    *p = 10;  // 已经释放掉了 还去赋值 正确应该直接赋值Null
    p = NULL;
}
