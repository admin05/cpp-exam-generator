

{0}------------------------------------------------

# 捷径

Pavel有一个非常简单的铁路玩具。它有一条含有  $n$  个车站的主干线并且连续编号为  $0$  到  $n-1$ 。车站  $0$  和车站  $n-1$  就在这条主干线的两端。其中车站  $i$  和车站  $i+1$  之间的距离为  $l_i$  厘米 ( $0 \leq i < n-1$ )。

除了这条主干线之外，这个铁路也许会有些支线。每条支线都是由主干线中的一个车站和主干线外的一个新车站之间的一条新铁路构成（这些新的车站不会被编号）。在主干线中的一个车站最多只能有一条支线。以主干线中的车站  $i$  为起点的支线的长度为  $d_i$  厘米。我们用  $d_i = 0$  来表示车站  $i$  没有支线。

![Diagram of a railway network. A main line connects stations 0, 1, 2, and 3. The distances between stations on the main line are labeled: 10 between 0 and 1, 20 between 1 and 2, and 30 between 2 and 3. There are three branches: one from station 1 with length 40, one from station 2 with length 20, and one from station 3 with length 30. Each station and branch end is marked with a small house icon.](8642df2e3828b25d27362bec6d5a0eae_img.jpg)

Diagram of a railway network. A main line connects stations 0, 1, 2, and 3. The distances between stations on the main line are labeled: 10 between 0 and 1, 20 between 1 and 2, and 30 between 2 and 3. There are three branches: one from station 1 with length 40, one from station 2 with length 20, and one from station 3 with length 30. Each station and branch end is marked with a small house icon.

Pavel现正规划一条快捷方式：一条在主干线中两个不相同的车站之间（它们可能相邻）的快速干线。这条快速干线无论是连接哪两个车站，它的长度都将会恰好是  $c$  厘米。

铁路中的每一段，包括那条新的快速干线，都能够双向行驶。任意两个车站的距离就是它们之间沿着铁路由一个车站到另一个车站之间最短路径的长度。所有车站组合中最大的距离就叫做整个铁路网络的直径。换句话说，存在一个最小值  $t$  使任意两个车站之间的距离都不会超过  $t$ 。

Pavel 就是想建造一条快速干线，使得有了这条快速干线后新的铁路网络的直径能达到最小值。

## 程序实现细节

你应该实现如下函数：

```
int64 find_shortcut(int n, int[] l, int[] d, int c)
```

- $n$ : 主干线中的车站数目，
- $l$ : 主干线中车站之间的距离（数组的长度为  $n-1$ ），

{1}------------------------------------------------

- $d$ : 支线的长度 (数组的长度为  $n$  ),
- $c$ : 新快速干线的长度.
- 函数应该返回加入新快速干线后铁路网络直径的最小可能值。

请使用提供的模板文件，参考关于你所使用的编程语言实现细节。

## 例子

### 例 1

对于上图所示的铁路网络，样例评分程序会调用以下函数：

```
find_shortcut(4, [10, 20, 20], [0, 40, 0, 30], 10)
```

最优解是在车站1和车站3之间建造一条快速干线，如下图所示。

![A diagram of a railway network with four stations represented by house icons. Station 0 is connected to Station 1 with a distance of 10. Station 1 is connected to Station 2 with a distance of 20, and to an unlabeled station below with a distance of 40. Station 2 is connected to Station 3 with a distance of 20. Station 3 is connected to an unlabeled station to its right with a distance of 30. A new shortcut line is shown connecting Station 1 and Station 3 with a distance of 10.](715219db84ec2a5622d09f9d822b4550_img.jpg)

A diagram of a railway network with four stations represented by house icons. Station 0 is connected to Station 1 with a distance of 10. Station 1 is connected to Station 2 with a distance of 20, and to an unlabeled station below with a distance of 40. Station 2 is connected to Station 3 with a distance of 20. Station 3 is connected to an unlabeled station to its right with a distance of 30. A new shortcut line is shown connecting Station 1 and Station 3 with a distance of 10.

这个新铁路网络的直径是 80 厘米，所以函数应该返回数值 80。

### 例 2

样例评分程序会调用以下函数：

```
find_shortcut(9, [10, 10, 10, 10, 10, 10, 10, 10, 10],  
[20, 0, 30, 0, 0, 40, 0, 40, 0], 30)
```

最优解是连接车站 2 和车站 7，这个解的直径是 110。

### 例 3

样例评分程序会调用以下函数：

```
find_shortcut(4, [2, 2, 2],  
[1, 10, 10, 1], 1)
```

最优解是连接车站 1 和车站 2，这样直径将被缩短到 21。

### 例 4

{2}------------------------------------------------

样例评分程序会调用以下函数：

```
find_shortcut(3, [1, 1],  
              [1, 1, 1], 3)
```

在任意两个车站中建立长度为 3 的快速干线都不会改进整个铁路网络的直径，因此其直径仍为初始值 4。

## 子任务

在所有子任务中  $2 \leq n \leq 1\,000\,000$ ,  $1 \leq l_i \leq 10^9$ ,  $0 \leq d_i \leq 10^9$ ,  $1 \leq c \leq 10^9$ .

1. (9 分)  $2 \leq n \leq 10$ ,
2. (14 分)  $2 \leq n \leq 100$ ,
3. (8 分)  $2 \leq n \leq 250$ ,
4. (7 分)  $2 \leq n \leq 500$ ,
5. (33 分)  $2 \leq n \leq 3000$ ,
6. (22 分)  $2 \leq n \leq 100\,000$ ,
7. (4 分)  $2 \leq n \leq 300\,000$ .
8. (3 分)  $2 \leq n \leq 1\,000\,000$ .

## 样例评测程序

样例评测程序按照以下格式读入输入：

- 第1行: 整数  $n$  和  $c$ ,
- 第2行: 整数  $l_0, l_1, \dots, l_{n-2}$ ,
- 第3行: 整数  $d_0, d_1, \dots, d_{n-1}$ .