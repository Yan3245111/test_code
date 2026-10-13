
/*
cpu按字节访问内存，对齐可以提升效率
使用结构体进行字节对齐，默认未4字节，如果成员超过4字节，则按照最大成员的整数倍对齐
指定对齐使用pragma pack(1) pragma pack()回复默认对齐， 一般对齐后不会改回默认对对齐
pragma pack(pop) 是恢复上一次对齐 对应pragma pack(push, 1)
pragma pack() 恢复默认对齐
一般都是用push/pop，不会影响平衡
*/

#pragma pack(4)  // 设置4字节对齐

#pragma pack(push, 1)  // 保存4字节，设为1字节
struct pragma_pack
{
    /* data */
};

#pragma pack(push, 2)  // 保存1，设置未2字节
struct pragma_pack
{
    /* data */
};

#pragma pack(pop)  // 删除2，恢复为1字节对齐

#pragma pack(pop)  // 删除1，恢复为4字节对齐

// 如果直接使用pragma pack()，会把所有的设置都改为默认字节对齐