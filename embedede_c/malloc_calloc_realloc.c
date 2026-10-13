#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

/*
malloc 不初始化，里面是垃圾值，速度最快，一般用于分配内存
calloc 初始化为0，速度比较慢，需要清0，一般用于数组分配
realloc 保留原数据，一般用于调整内存大小
*/


// malloc
void malloc_test() {
    int *arr = (int*)malloc(10 * sizeof(int));
    if (arr == NULL) {

    }

    for (int i = 0; i < 10; i++) {
        arr[i] = i;
    }
    free(arr);  // 必须释放，不然内存泄漏
}


// calloc 分配并清零
void calloc_test() {
    int *arr = (int*)calloc(10, sizeof(int));
    if (arr == NULL) {

    }
    printf("%d\n", arr[0]);
}


// realloc 调整内存使用
void realloc_test() {
    int *arr = (int*)malloc(5 * sizeof(int));
    if (arr == NULL) {
        return;
    };
    // 扩大/缩小内存
    arr = (int*)realloc(arr, 18 * sizeof(int));
    arr = (int*)realloc(arr, 1 * sizeof(int));
}