

{0}------------------------------------------------

# 《逃学的小孩》

## 【问题描述】

Chris 家的电话铃响起了，里面传出了 Chris 的老师焦急的声音：“喂，是 Chris 的家长吗？你们的孩子又没来上课，不想参加考试了吗？”一听说要考试，Chris 的父母就心急如焚，他们决定在尽量短的时间内找到 Chris。他们告诉 Chris 的老师：“根据以往的经验，Chris 现在必然躲在朋友 Shermie 或 Yashiro 家里偷玩《拳皇》游戏。现在，我们就从家出发去找 Chris，一但找到，我们立刻给您打电话。”说完砰的一声把电话挂了。

Chris 居住的城市由  $N$  个居住点和若干条连接居住点的双向街道组成，经过街道  $x$  需花费  $T_x$  分钟。可以保证，任两个居住点间有且仅有一条通路。Chris 家在点 C，Shermie 和 Yashiro 分别住在点 A 和点 B。Chris 的老师和 Chris 的父母都有城市地图，但 Chris 的父母知道点 A、B、C 的具体位置而 Chris 的老师不知。

为了尽快找到 Chris，Chris 的父母会遵守以下两条规则：

- 如果 A 距离 C 比 B 距离 C 近，那么 Chris 的父母先去 Shermie 家寻找 Chris，如果找不到，Chris 的父母再去 Yashiro 家；反之亦然。
- Chris 的父母总沿着两点间唯一的通路行走。

显然，Chris 的老师知道 Chris 的父母在寻找 Chris 的过程中会遵守以上两条规则，但由于他并不知道 A，B，C 的具体位置，所以现在他希望你告诉他，最坏情况下 Chris 的父母要耗费多长时间才能找到 Chris？

![A diagram showing a path of four nodes connected by three edges. The nodes are labeled A, C, and B from left to right. There is an unlabeled node between A and C. Each edge is labeled with the number 1. Above node A is a cloud labeled 'Shermie'. Above node B is a cloud labeled 'Yashiro'. Below node C is a cloud labeled 'Chris'.](868ef3e0abb37916a7af1e923995f329_img.jpg)

A diagram showing a path of four nodes connected by three edges. The nodes are labeled A, C, and B from left to right. There is an unlabeled node between A and C. Each edge is labeled with the number 1. Above node A is a cloud labeled 'Shermie'. Above node B is a cloud labeled 'Yashiro'. Below node C is a cloud labeled 'Chris'.

例如上图，这座城市由 4 个居住点和 3 条街道组成，经过每条街道均需花费 1 分钟时间。假设 Chris 住在点 C，Shermie 住在点 A，Yashiro 住在点 B，因为 C 到 B 的距离小于 C 到 A 的距离，所以 Chris 的父母会先去 Yashiro 家寻找 Chris，一旦找不到，再去 Shermie 家寻找。这样，最坏情况下 Chris 的父母需要花费 4 分钟的时间才能找到 Chris。

{1}------------------------------------------------

## **【输入文件】**

输入文件 hookey.in 第一行是两个整数  $N$  ( $3 \leq N \leq 200000$ ) 和  $M$ ，分别表示居住点总数和街道总数。以下  $M$  行，每行给出一条街道的信息。第  $i+1$  行包含整数  $U_i$ 、 $V_i$ 、 $T_i$  ( $1 \leq U_i, V_i \leq N$ ,  $1 \leq T_i \leq 1000000000$ )，表示街道  $i$  连接居住点  $U_i$  和  $V_i$ ，并且经过街道  $i$  需花费  $T_i$  分钟。街道信息不会重复给出。

## **【输出文件】**

输出文件 hookey.out 仅包含整数  $T$ ，即最坏情况下 Chris 的父母需要花费  $T$  分钟才能找到 Chris。

## **【样例输入】**

```
4 3
1 2 1
2 3 1
3 4 1
```

## **【样例输出】**

```
4
```