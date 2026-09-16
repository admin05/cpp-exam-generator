

{0}------------------------------------------------

![Logo of the 31st International Olympiad in Informatics (IOI 2019) featuring two green towers with red flames and a central red circle with a white flame.](2dfa6ac3edfe874f68aa0cbccaa42322_img.jpg)

Logo of the 31st International Olympiad in Informatics (IOI 2019) featuring two green towers with red flames and a central red circle with a white flame.

## 折线

阿塞拜疆因地毯而闻名。作为一位地毯设计大师，你在做新设计时想画一条折线。一条折线是二维平面上包含  $t$  条线段的线段序列，而这些线段由包含  $t + 1$  个点  $p_0, \dots, p_t$  的点序列按照下述规则定义给出：对所有的  $0 \leq j \leq t - 1$ ，都有一条线段连接点  $p_j$  和  $p_{j+1}$ 。

为完成这个新设计，你已经标出了二维平面中的  $n$  个小圆点。小圆点  $i$  ( $1 \leq i \leq n$ ) 的坐标为  $(x[i], y[i])$ 。不存在  $x$  坐标或  $y$  坐标相同的两个小圆点。

现在你想要找到一个点序列  $(sx[0], sy[0]), (sx[1], sy[1]), \dots, (sx[k], sy[k])$ ，由该点序列定义给出的折线需满足

- 该折线从  $(0, 0)$  开始（即  $sx[0] = 0$  且  $sy[0] = 0$ ），
- 该折线经过所有的小圆点（它们不必是线段的端点），以及
- 该折线仅包括水平线段和竖直线段（对于定义该折线的连续两个点，其  $x$  坐标或  $y$  坐标相等）。

折线可以以任意的方式自相交或自重叠。正式地来说，平面上的每个点可以属于折线中任意数量的线段。

本题是一个有部分分的提交答案型题目。将会给你 10 个输入文件，这些文件给出了小圆点的位置。对每个输入文件，你需要提交一个答案文件，描述满足要求的折线。对每个给出合法折线的输出文件，你的得分将依赖于折线中的线段数量（参见下面的计分方式一节）。

你不需要为本题提交任何源代码。

## 输入格式

每个输入文件的格式如下：

- 第 1 行：  $n$
- 第  $1 + i$  行（这里  $1 \leq i \leq n$ ）：  $x[i] \ y[i]$

## 输出格式

每个输出文件必须按照如下格式：

- 第 1 行：  $k$
- 第  $1 + j$  行（这里  $1 \leq j \leq k$ ）：  $sx[j] \ sy[j]$

注意，第二行应包含  $sx[1]$  和  $sy[1]$ （也就是说，输出不应当包含  $sx[0]$  和  $sy[0]$ ）。所有的  $sx[j]$  和  $sy[j]$  均应为整数。

{1}------------------------------------------------

## 例子

对于示例性的输入数据:

```
4
2 1
3 3
4 4
5 2
```

一个可能的合法输出为:

```
6
2 0
2 3
5 3
5 2
4 2
4 4
```

![A 2D grid plot showing a path connecting points (2,1), (3,3), (4,4), and (5,2). The path starts at (0,0), goes to (2,0), then up to (2,1), then right to (3,3), then up to (4,4), then left to (5,2), and finally down to (5,0). The points are marked with black dots.](258c1507ae7e731f704a016f660cd469_img.jpg)

A 2D grid plot with x and y axes ranging from 0 to 5. A path is shown starting at (0,0), moving horizontally to (2,0), then vertically to (2,1), then horizontally to (3,3), then vertically to (4,4), then horizontally to (5,2), and finally vertically to (5,0). The points (2,1), (3,3), (4,4), and (5,2) are marked with black dots.

A 2D grid plot showing a path connecting points (2,1), (3,3), (4,4), and (5,2). The path starts at (0,0), goes to (2,0), then up to (2,1), then right to (3,3), then up to (4,4), then left to (5,2), and finally down to (5,0). The points are marked with black dots.

请注意, 这个例子并不是本题真正的输入数据。

## 限制条件

- $1 \leq n \leq 100\,000$
- $1 \leq x[i], y[i] \leq 10^9$
- 所有  $x[i]$  和  $y[i]$  的值都是整数。
- 不存在  $x$  坐标或  $y$  坐标相同的两个小圆点, 也就是说, 对于所有的  $i_1 \neq i_2$ , 都有  $x[i_1] \neq x[i_2]$  且  $y[i_1] \neq y[i_2]$ 。
- $-2 \cdot 10^9 \leq sx[j], sy[j] \leq 2 \cdot 10^9$

{2}------------------------------------------------

- 提交的每个文件（无论是输出文件还是压缩文件）的大小均不能超过 15MB。

## 计分方式

对每个测试点，你最多能够得到 10 分。如果没有给出一条满足要求的折线，你在这个测试点上的输出将被判为 0 分。否则，得分将根据一个递减序列  $c_1, \dots, c_{10}$  来计算，各个测试点的递减序列是不同的。

假设你的解答是一条包含  $k$  条线段的合法折线。那么，你将得到

- $i$  分，如果  $k = c_i$ （这里  $1 \leq i \leq 10$ ），
- $i + \frac{c_i - k}{c_i - c_{i+1}}$  分，如果  $c_{i+1} < k < c_i$ （这里  $1 \leq i \leq 9$ ），
- 0 分，如果  $k > c_1$ ，
- 10 分，如果  $k < c_{10}$ 。

下面对每个测试点给出对应的序列  $c_1, \dots, c_{10}$ 。

| 测试点      | 01 | 02    | 03     | 04      | 05      | 06      | 07-10   |
|----------|----|-------|--------|---------|---------|---------|---------|
| $n$      | 20 | 600   | 5 000  | 50 000  | 72 018  | 91 891  | 100 000 |
| $c_1$    | 50 | 1 200 | 10 000 | 100 000 | 144 036 | 183 782 | 200 000 |
| $c_2$    | 45 | 937   | 7 607  | 75 336  | 108 430 | 138 292 | 150 475 |
| $c_3$    | 40 | 674   | 5 213  | 50 671  | 72 824  | 92 801  | 100 949 |
| $c_4$    | 37 | 651   | 5 125  | 50 359  | 72 446  | 92 371  | 100 500 |
| $c_5$    | 35 | 640   | 5 081  | 50 203  | 72 257  | 92 156  | 100 275 |
| $c_6$    | 33 | 628   | 5 037  | 50 047  | 72 067  | 91 941  | 100 050 |
| $c_7$    | 28 | 616   | 5 020  | 50 025  | 72 044  | 91 918  | 100 027 |
| $c_8$    | 26 | 610   | 5 012  | 50 014  | 72 033  | 91 906  | 100 015 |
| $c_9$    | 25 | 607   | 5 008  | 50 009  | 72 027  | 91 900  | 100 009 |
| $c_{10}$ | 23 | 603   | 5 003  | 50 003  | 72 021  | 91 894  | 100 003 |

## 可视化工具

在本题的附件中有一个脚本，能让你对输入文件和输出文件进行可视化。

在对输入文件做可视化时，使用如下命令：

```
python vis.py [input file]
```

对于某个输入数据，你还可以使用下面的命令对你的解答进行可视化。由于技术方面的限制，所提供的可视化工具仅显示输出文件中的前 1000 条线段。

{3}------------------------------------------------

```
python vis.py [input file] --solution [output file]
```

例如：

```
python vis.py examples/00.in --solution examples/00.out
```