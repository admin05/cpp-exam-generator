

{0}------------------------------------------------

![IOI 2018 logo featuring a red circle with a white stylized flower and two blue vertical bars.](2dfa6ac3edfe874f68aa0cbccaa42322_img.jpg)

IOI 2018 logo featuring a red circle with a white stylized flower and two blue vertical bars.

# 注意事项（第1试）

你可以从CMS为每道题目下载一个压缩附件包。对于实现细节和评测程序示例，请查看zip包中的文件。

- 对每道题目，你只能提交恰好一个文件。
- 对每道题目，你最多可以提交50次。
- 你提交的程序不允许从标准输入读入、打印到标准输出，或者与其他任何文件进行交互。但是，可以输出到标准错误流。
- 你提交的文件需要实现在题面中列出的过程和/或函数，其签名应与实现示例一致。
- 你可以任意实现其他过程和/或函数。
- 当你在本地机器上测试你的代码时，我们推荐你使用附件包中的脚本。否则，特别是对C++来说，要确保在编译时加上-std=gnu++14选项。

# 约定

对于所支持的各种编程语言，下面列出了对应的数据类型。对于数据类型等的细节，参见实现示例。

| 语言     | <b>int</b> | <b>int64</b> | <b>int[]</b>     | 数组a的长度    | <b>string</b> |
|--------|------------|--------------|------------------|-----------|---------------|
| C++    | int        | long long    | std::vector<int> | a.size()  | std::string   |
| Pascal | longint    | int64        | array of longint | length(a) | ansistring    |
| Java   | int        | long         | int[]            | a.length  | String        |

## 限制

| 题目       | 标题   | 时间限制 | 内存限制   |
|----------|------|------|--------|
| combo    | 组合动作 | 1.0秒 | 268 MB |
| seats    | 排座位  | 3.0秒 | 268 MB |
| werewolf | 狼人   | 4.0秒 | 537 MB |