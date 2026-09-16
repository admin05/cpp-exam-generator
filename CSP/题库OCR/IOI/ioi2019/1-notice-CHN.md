

{0}------------------------------------------------

![Logo of the 31st International Olympiad in Informatics (IOI 2019) featuring two green towers with torches and a central red circle with a flame.](2dfa6ac3edfe874f68aa0cbccaa42322_img.jpg)

Logo of the 31st International Olympiad in Informatics (IOI 2019) featuring two green towers with torches and a central red circle with a flame.

# 注意事项

对于每道题目：

- 你可以从比赛系统里下载一个附件包。
- 附件包里面有评测程序示例、实现示例、测试样例示例和编译脚本。
- 每道题目最多可以提交50次，每次只能提交一个文件。
- 要提交的文件名在题面的页眉中给出（右上角）。题面要求实现的函数必须按照实现示例所给出的函数签名来实现。
- 你可以根据需要而实现其他函数。
- 你提交的程序不能读取标准输入，不能写入标准输出，也不能和其他任何文件做交互。但是，可以向标准错误流输出。
- 在使用评测程序示例来评测你的程序时，你的输入数据应当符合题面所要求的格式和限制条件，否则可能会引发不确定的行为。
- 除非明确指定了其他格式，否则在评测程序示例的输入中，每一行里连续两项之间用一个空格进行分隔。
- 在本地机器测试你的代码时，建议使用附件包中的脚本。否则，特别是对 C++ 来说，编译时一定要加上 `-std=gnu++14` 选项。

## 约定

题面在给出函数签名时，会使用一般性的类型名称 `int`、`int64`、`int[]`（数组）和`int[][]`（二维数组）。

对于所支持的每种编程语言，评测程序会采用适当的数据类型和适当的实现，如下表所示：

| 语言   | <code>int</code> | <code>int64</code>     | <code>int[]</code>                  | 数组 <b>a</b> 的长度       |
|------|------------------|------------------------|-------------------------------------|-----------------------|
| C++  | <code>int</code> | <code>long long</code> | <code>std::vector&lt;int&gt;</code> | <code>a.size()</code> |
| Java | <code>int</code> | <code>long</code>      | <code>int[]</code>                  | <code>a.length</code> |

二维数组是长度相同的（一维）数组的非空数组。

| 语言   | <code>int[][]</code>                                   | 二维数组 <b>a</b> 的行数     | 二维数组 <b>a</b> 的列数        |
|------|--------------------------------------------------------|-----------------------|--------------------------|
| C++  | <code>std::vector&lt;std::vector&lt;int&gt;&gt;</code> | <code>a.size()</code> | <code>a[0].size()</code> |
| Java | <code>int[][]</code>                                   | <code>a.length</code> | <code>a[0].length</code> |

{1}------------------------------------------------

## 限制

| 题目    | 时间限制 | 内存限制    |
|-------|------|---------|
| shoes | 1 秒  | 1024 MB |
| split | 2 秒  | 1024 MB |
| rect  | 5 秒  | 1024 MB |