#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>


 /*
运算符	名称	示例	说明
&	按位与	a & b	两个位都为1时结果为1
|	按位或	a | b	两个位有一个为1时结果为1
^	按位异或	a ^ b	两个位不同为1，相同为0
~	按位取反	~a	0变1，1变0
<<	左移	a << n	左移n位，低位补0
>>	右移	a >> n	右移n位，高位补0（无符号）或符号位（有符号）
*/

// 判断奇偶 看最后一位是1还是0，1则是基数，0是偶数，比 x % 2快很多
int is_even_odd(int x) {
    return (x & 1);
}


int mul_by_pow2(int x, int n) {
    int a = x << n;  // 相当于x * (2^n)
    int b = x >> n;  // 相当于x / (2^n)
    printf(" %d 左移 %d 结果 %d\n", x, n, a);
    printf(" %d 右移 %d 结果 %d\n", x, n, b);
}


// 两个数值交换 原理：三次异或实现交换
void swap(int *a, int *b) {
    printf("交换前 a=%d, b=%d\n", *a, *b);
    if (a != b) {  // 避免自己与自己交换
        *a ^= *b;
        *b ^= *a;
        *a ^= *b;
    }
    printf("交换后 a=%d, b=%d\n", *a, *b);
}


int main() {
    int a = is_even_odd(10);
    mul_by_pow2(3, 2);
    int x = 3, y = 4;
    swap(&x, &y);                                                                                                                                                                                                                                                                                                                                                                                                                                                    
}
