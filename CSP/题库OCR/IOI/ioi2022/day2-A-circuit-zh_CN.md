

{0}------------------------------------------------

![IOI 2022 logo](2dfa6ac3edfe874f68aa0cbccaa42322_img.jpg)

IOI 2022 logo

# 数字电路 (circuit)

有一个数字电路，由编号为从 0 到  $N + M - 1$  的  $N + M$  个门组成。其中，0 到  $N - 1$  号门是**阈值门**，而  $N$  到  $N + M - 1$  号门是**输入门**。

除 0 号门之外的每个门都是恰好一个某阈值门的**输入**。具体来说，对于每个满足  $1 \leq i \leq N + M - 1$  的  $i$ ，门  $i$  是门  $P[i]$  的一个输入，其中  $0 \leq P[i] \leq N - 1$ 。重要的是，我们保证  $P[i] < i$  成立。此外，我们假设有  $P[0] = -1$ 。每个阈值门有一个或多个的输入。输入门没有任何输入。

每个门都有一个**状态**，取 0 或 1。输入门的初始状态由一个包含  $M$  个整数的数组  $A$  给定。也就是说，对于每个满足  $0 \leq j \leq M - 1$  的  $j$ ，输入门  $N + j$  的初始状态为  $A[j]$ 。

每个阈值门的状态取决于它的输入的状态，具体如下。首先，每个阈值门会被指定一个**阈值参数**。对于一个有  $c$  个输入的阈值门，其所指定的参数必须是 1 到  $c$  之间的某个整数（包括 1 和  $c$ ）。随后，对于一个参数为  $p$  的阈值门，如果它的输入中至少有  $p$  个门的状态为 1，则当前阈值门的状态为 1，否则状态为 0。

例如，假设有  $N = 3$  个阈值门和  $M = 4$  个输入门。其中，门 0 的输入为门 1 和门 6，门 1 的输入为门 2、4 和 5，门 2 仅有的输入为门 3。

上述例子的说明可见下图。

![Diagram of a digital circuit with 7 gates (0-6). Gate 0 is a threshold gate with inputs 1 and 6. Gate 1 is a threshold gate with inputs 2, 4, and 5. Gate 2 is a threshold gate with input 3. Gates 3, 4, 5, and 6 are input gates. Arrows show the flow of signals from input gates to threshold gates.](17b9d89b91e10c3efc38193baedee268_img.jpg)

```
graph BT; 3((3)) --> 2((2)); 4((4)) --> 1((1)); 5((5)) --> 1((1)); 2((2)) --> 1((1)); 1((1)) --> 0((0)); 6((6)) --> 0((0));
```

Diagram of a digital circuit with 7 gates (0-6). Gate 0 is a threshold gate with inputs 1 and 6. Gate 1 is a threshold gate with inputs 2, 4, and 5. Gate 2 is a threshold gate with input 3. Gates 3, 4, 5, and 6 are input gates. Arrows show the flow of signals from input gates to threshold gates.

假设输入门 3 和 5 的状态为 1，而门 4 和 6 的状态为 0。假设阈值门 2、1、0 被指定的参数分别为 1、2、2。在这种情况下，门 2 的状态为 1，门 1 的状态为 1，门 0 的状态为 0。下面给出了参数赋值以及状态的示意图。状态为 1 的门被标记为黑色。

{1}------------------------------------------------

![A directed graph representing a circuit. Nodes are numbered 0 to 6. Node 0 is a white circle at the top. Node 1 is a black circle below it. Node 2 is a black circle to the left of node 1. Node 3 is a black circle below node 2. Node 4 is a white circle below node 1. Node 5 is a black circle to the right of node 1. Node 6 is a white circle to the right of node 0. Edges: 3 -> 2, 2 -> 1, 4 -> 1, 5 -> 1, 1 -> 0, 6 -> 0. Weights: edge 2->1 is 2, edge 1->0 is 2, edge 6->0 is 1.](68ac34ff111db52afaa786afcb8346c3_img.jpg)

A directed graph representing a circuit. Nodes are numbered 0 to 6. Node 0 is a white circle at the top. Node 1 is a black circle below it. Node 2 is a black circle to the left of node 1. Node 3 is a black circle below node 2. Node 4 is a white circle below node 1. Node 5 is a black circle to the right of node 1. Node 6 is a white circle to the right of node 0. Edges: 3 -> 2, 2 -> 1, 4 -> 1, 5 -> 1, 1 -> 0, 6 -> 0. Weights: edge 2->1 is 2, edge 1->0 is 2, edge 6->0 is 1.

输入门的状态将会经历  $Q$  次更新。每次更新用两个整数  $L$  和  $R$  来描述 ( $N \leq L \leq R \leq N + M - 1$ )，表示翻转所有编号在  $L$  和  $R$  之间（包括  $L$  和  $R$ ）的输入门的状态。这就是说，对于所有满足  $L \leq i \leq R$  的  $i$ ，输入门  $i$  的状态如果为 0，则会被翻转为 1；如果状态为 1，则会被翻转为 0。每个门被翻转后将会一直保持在新状态，直到在后续某次更新中被翻转。

你的目标是，计算每次更新后有多少种阈值门参数的赋值方案，使得门 0 的状态为 1。当有至少一个阈值门的参数不同时，两种参数赋值方案被认为是不同的。由于方案数可能较大，你需要计算它对 1 000 002 022 取模的结果。

注意，在上面的例子中，共有 6 种不同的对阈值门参数进行赋值的方案，因为门 0、1、2 分别有 2、3、1 个输入。在这 6 种方案里面，有 2 种参数赋值方案使得门 0 的状态为 1。

## 实现细节

你的任务是实现下述两个函数。

```
void init(int N, int M, int[] P, int[] A)
```

- $N$ ：阈值门的数量。
- $M$ ：输入门的数量。
- $P$ ：一个长度为  $N + M$  的数组，给出阈值门的输入。
- $A$ ：一个长度为  $M$  的数组，给出输入门的初始状态。
- 这个函数被调用恰好一次，且发生在函数 `count_ways` 的所有调用之前。

```
int count_ways(int L, int R)
```

- $L, R$ ：编号在  $L$  和  $R$  之间的输入门的状态将会被翻转。
- 这个函数应首先执行所规定的更新，然后返回使得门 0 的状态为 1 的参数赋值方案的方案数对 1 000 002 022 取模的结果。
- 这个函数会被调用恰好  $Q$  次。

{2}------------------------------------------------

## 例子

考虑如下的函数调用序列：

```
init(3, 4, [-1, 0, 1, 2, 1, 1, 0], [1, 0, 1, 0])
```

题面描述中已经给出了对这个例子的解释。

```
count_ways(3, 4)
```

这次调用翻转了门 3 和 4 的状态，也就是说，门 3 的状态变成 0，门 4 的状态变成 1。下面给出了两种可行的参数赋值方案，可以使得门 0 的状态为 1。

![Diagram of a logic circuit for Scheme 1. Gate 0 (black) is the output. Gate 1 (black) is an AND gate with inputs from Gate 2 (white) and Gate 5 (black). Gate 2 (white) has input from Gate 3 (white). Gate 6 (white) is an input to Gate 0. Gate 4 (black) is an input to Gate 1. The number 1 is written above each gate. Diagram of a logic circuit for Scheme 2. Gate 0 (black) is the output. Gate 1 (black) is an AND gate with inputs from Gate 2 (white) and Gate 5 (black). Gate 2 (white) has input from Gate 3 (white). Gate 6 (white) is an input to Gate 0. Gate 4 (black) is an input to Gate 1. The number 2 is written above Gate 1, and the number 1 is written above the other gates.](2df09d249c38abee55dbf0526dd6da0a_img.jpg)

| 方案 1 | 方案 2 |
|------|------|
|      |      |

Diagram of a logic circuit for Scheme 1. Gate 0 (black) is the output. Gate 1 (black) is an AND gate with inputs from Gate 2 (white) and Gate 5 (black). Gate 2 (white) has input from Gate 3 (white). Gate 6 (white) is an input to Gate 0. Gate 4 (black) is an input to Gate 1. The number 1 is written above each gate. Diagram of a logic circuit for Scheme 2. Gate 0 (black) is the output. Gate 1 (black) is an AND gate with inputs from Gate 2 (white) and Gate 5 (black). Gate 2 (white) has input from Gate 3 (white). Gate 6 (white) is an input to Gate 0. Gate 4 (black) is an input to Gate 1. The number 2 is written above Gate 1, and the number 1 is written above the other gates.

在所有其他的参数赋值方案中，门 0 的状态为 0。因此，函数应返回 2。

```
count_ways(4, 5)
```

这次调用翻转了门 4 和 5 的状态。其结果是，所有输入门的状态均为 0，而且对于所有的参数赋值方案，门 0 的状态均为 0。因此，函数应返回 0。

```
count_ways(3, 6)
```

这次调用将所有输入门的状态置为 1。其结果是，对于所有参数赋值方案，门 0 的状态均为 1。因此，函数应返回 6。

## 约束条件

- $1 \leq N, M \leq 100\,000$

{3}------------------------------------------------

- $1 \leq Q \leq 100\,000$
- $P[0] = -1$
- $0 \leq P[i] < i$  且  $P[i] \leq N - 1$  (对于所有满足  $1 \leq i \leq N + M - 1$  的  $i$ )
- 每个阈值门至少有一个输入 (对于所有满足  $0 \leq i \leq N - 1$  的  $i$ , 存在某个下标  $x$  满足  $i < x \leq N + M - 1$  且  $P[x] = i$ )
- $0 \leq A[j] \leq 1$  (对于所有满足  $0 \leq j \leq M - 1$  的  $j$ )
- $N \leq L \leq R \leq N + M - 1$

## 子任务

1. (2 分)  $N = 1$ ,  $M \leq 1000$ ,  $Q \leq 5$
2. (7 分)  $N, M \leq 1000$ ,  $Q \leq 5$ , 每个阈值门都有恰好两个输入
3. (9 分)  $N, M \leq 1000$ ,  $Q \leq 5$
4. (4 分)  $M = N + 1$ ,  $M = 2^z$  (对于某个正整数  $z$ ),  $P[i] = \lfloor \frac{i-1}{2} \rfloor$  (对于所有满足  $1 \leq i \leq N + M - 1$  的  $i$ ),  $L = R$
5. (12 分)  $M = N + 1$ ,  $M = 2^z$  (对于某个正整数  $z$ ),  $P[i] = \lfloor \frac{i-1}{2} \rfloor$  (对于所有满足  $1 \leq i \leq N + M - 1$  的  $i$ )
6. (27 分) 每个阈值门都恰好有两个输入
7. (28 分)  $N, M \leq 5000$
8. (11 分) 没有额外的约束条件

## 评测程序示例

评测程序示例读取如下格式的输入:

- 第 1 行:  $N\ M\ Q$
- 第 2 行:  $P[0]\ P[1]\ \dots\ P[N + M - 1]$
- 第 3 行:  $A[0]\ A[1]\ \dots\ A[M - 1]$
- 第  $4 + k$  行 ( $0 \leq k \leq Q - 1$ ): 第  $k$  次更新对应的  $L\ R$

评测程序示例按照如下格式打印你的答案:

- 第  $1 + k$  行 ( $0 \leq k \leq Q - 1$ ): `count_ways` 函数对第  $k$  次更新的返回值