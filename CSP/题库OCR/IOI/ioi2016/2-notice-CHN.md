

{0}------------------------------------------------

![IOI 2016 Russia-Kazan logo](2dfa6ac3edfe874f68aa0cbccaa42322_img.jpg)

IOI 2016 Russia-Kazan logo

# 实现注意事项

- 你**必须**提交一个文件且只能提交一个文件（文件名在**问题说明**中**已经给出**）。
- 该文件利用了**样例实现**中**给出**的参数，**实现**了任务说明中描述的子程序。
- 这些子程序**必须**和任务说明中描述的一致。
- 你可以自由**实现**其他子程序（函数、过程、方法）。
- 你的提交**一定不能**以任何方式和**标准输入输出流**交互，也不能和其他任何文件交互。特别地，如果你的程序**输出**任何信息**给标准输出流**，那么**在这个测试**上的**评分结果**将是**SV**（安全违规）。你可以**输出**任何信息**给标准错误流**。

## 规定

任务说明和实现细节部分使用一些一般的**类型**名字，特别的：

- 名字 *array* 和**对应**的**类型** `int[]`
- **类型** `int64`
- **类型** `string`
- **类型** `boolean`

在每一个被支持的**编程语言**中，评测程序使用**相应**的**数据类型**，如下所示：

| 语言     | array                               | int64                  | string                   | boolean              |
|--------|-------------------------------------|------------------------|--------------------------|----------------------|
| C++    | <code>std::vector&lt;int&gt;</code> | <code>long long</code> | <code>std::string</code> | <code>bool</code>    |
| C      | <code>int*</code>                   | <code>long long</code> | <code>char*</code>       | <code>int</code>     |
| Pascal | <code>array of longint</code>       | <code>int64</code>     | <code>string</code>      | <code>boolean</code> |
| Java   | <code>int[]</code>                  | <code>long</code>      | <code>String</code>      | <code>boolean</code> |

## 限制

| 问题    | 时间限制 | 内存限制 |
|-------|------|------|
| 按数目填色 | 2 秒  | 2 GB |
| 解读Bug | 2 秒  | 2 GB |
| 外星人   | 2 秒  | 2 GB |