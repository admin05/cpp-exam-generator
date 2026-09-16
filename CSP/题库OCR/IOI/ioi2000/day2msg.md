

{0}------------------------------------------------

# IOI 2000 Beijing China Messages from Output Format Checkers 输出格式检查器信息 DAY 2

### Help

#### 使用帮助

IOI 2000 - Beijing China

Output checker for problem XXXX (XXXX = BLOCK / POST / WALLS)

题目 XXXX(BLOCK / POST / WALLS)的输出检查

#### USAGE:

使用方法:

XXXX\_F [-h] <filename>

#### ARGUMENTS:

参数:

|            |                                           |
|------------|-------------------------------------------|
| -h         | Display this help and exit<br>显示本帮助信息然后退出 |
| <filename> | Output file to check<br>需要检查的输出文件名        |

### Message when no error found

### 格式正确时的信息

PASSED ..

REMEMBER : THIS DOES NOT MEAN THAT YOUR SOLUTION IS CORRECT!

通过..

注意:这并不表示你的答案是正确的!

### Common Message

#### 一般错误信息

Output filename required

缺少输出文件名

Cannot open file XXXX

文件 XXXX 不能打开

Unexpected end-of-file at line XXXX

{1}------------------------------------------------

文件在 XXXX 行非正常结束

Extra character found in line XXXX

第 XXXX 行有多余字符

Extra lines found

找到多余的行

In line XXXX, non-digital character is found before No.YYYY integer

在第 XXXX 行，在第 YYYY 个整数前发现非数字字符

In line XXXX, the No.YYYY integer is missing

在第 XXXX 行，第 YYYY 个整数丢失

In line XXXX, space before the No.YYYY integer is missing

在第 XXXX 行，第 YYYY 个整数前的空格丢失

In line XXXX, extra space is found before the No.YYYY integer

在第 XXXX 行，第 YYYY 个整数前发现多余空格

In line XXXX, the No.YYYY integer is overflow

在第 XXXX 行，第 YYYY 个整数溢出

#### POST Message

#### POST 错误信息

The sum of distances is missing

距离和未输出

The sum of distances is larger than maximum possible value, XXXX

距离和超过了最大可能值 XXXX

The sum of distances is smaller than 0

距离和小于 0

The position of No.XXXX post office is larger than maximum possible value, 10000

第 XXXX 个邮局建立位置大于最大可能值 10000

The position of No.XXXX post office is smaller than 1

第 XXXX 个邮局建立位置小于最小可能值 1

The number of post offices is smaller than 1

邮局数小于 1

The number of post offices is larger than max possible, 30

邮局数大于最大可能值 30

Sequence of post office positions is not increasing

邮局位置没有升序排列

{2}------------------------------------------------

#### **WALLS Message**

#### **WALLS 错误信息**

The number of walls is missing

翻越的长城数未输出

The number of walls is larger than maximum possible value, XXXX

翻越的长城数大于最大可能值 XXXX

The number of walls is smaller than 0

翻越的长城数小于 0

Optimal area label is missing

最优聚会地编号未知

Optimal area label is larger than maximum possible value, 200

最优聚会地编号大于最大可能编号 200

Optimal area label is smaller than 1

最优集合地编号小于 1

#### **BLOCK Message**

#### **BLOCK 错误信息**

The number of blocks is missing

积木数未找到

The number of blocks is larger than maximum possible value, 50

积木数大于最大可能值 50

The number of blocks is smaller than 1

积木数小于 1

Less blocks in the sequence

列出的积木数目少于积木数

More blocks in the sequence

列出的积木数目多于积木数

The type of No.XXXX block in the sequence is larger than 12

第 XXXX 块积木种类号大于 12

The type of No.XXXX block in the sequence is smaller than 1

第 XXXX 块积木种类号小于 1