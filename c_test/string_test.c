#include <stdio.h>
#include <string.h>


// 字符串拼接，讲字符串追加到字符串末尾
void strcat_test() {
    printf("Testing strcat...\n");
    char buf[100] = "Hello, ";
    char *text = "World!";
    memset(buf, 0, sizeof(buf));
    strcat(buf, text);
    printf("Concatenated string: %s\n", buf);
}


// 字符串查找，查找字符串在另一个字符串中的位置
void strstr_test() {
    printf("Testing strstr...\n");
    char *buf = "Hello, World!";
    char *substr = "World";
    char *res = strstr(buf, substr);
    if (res) {
        printf("Substring found at position: %s %d\n", res, res - buf);
    } else {
        printf("Substring not found\n");
    }
}

// 字符串复制，将一个字符串复制到另一个字符串，会覆盖原有内容
void strcpy_test() {
    printf("Testing strcpy...\n");
    char buf[20] = "Hello";
    char *text = "World!";
    strcpy(buf, text);
    printf("Copied string: %s\n", buf);
}

// 分隔符分割字符串，将字符串按照指定的分隔符进行分割，返回分割后的字符串
void strtok_test() {
    char buf[20] = "123-456-789";
    
} 

int main() {
    strcat_test();
    strstr_test();
    strcpy_test();
    return 0;
}