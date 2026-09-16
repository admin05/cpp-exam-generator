

{0}------------------------------------------------

# 木棒游戏

这是一个很古老的游戏。用木棒在桌上拼出一个不成立的等式，移动且只移动一根木棒使得等式成立。现在轮到你了。

![Figure 1: A matchstick equation 1 + 1 = 3 is shown on the left. An arrow points to the right, where the same equation is shown with the digit '3' changed to '2' by moving one matchstick from the top to the bottom, resulting in the correct equation 1 + 1 = 2.](5fb340ad68b0c71df0b56698b137e35b_img.jpg)

Figure 1: A matchstick equation 1 + 1 = 3 is shown on the left. An arrow points to the right, where the same equation is shown with the digit '3' changed to '2' by moving one matchstick from the top to the bottom, resulting in the correct equation 1 + 1 = 2.

图 1

## 【任务】

从文件读入一个式子。

如果移动一根木棒可以使等式成立，则输出新的等式，否则输出 No。

## 【说明和限制】

1. 式子中只会出现在加号和减号（包括负号），并且有且仅有一个等号，不会出现括号、乘号或除号，也不会有  $++$ ,  $--$ ,  $+-$  或  $-+$  出现。
2. 式子中不会出现 8 个或 8 个以上的连续数字。
3. 你只能移动用来构成数字的木棒，不能移动构成运算符（ $+$   $-$   $=$ ）的木棒，所以加号、减号、等号是不会改变的。移动前后，木棒构成的数字必须严格与图 2 中的 0~9 相符。
4. 修改前的等式中的数不会以 0 开头，但允许修改后的等式中的数以数字 0 开头。

![Figure 2: A row of matchstick representations for digits 0 through 9. Digit 0 is a rectangle. Digit 1 is a single vertical line. Digit 2 has a horizontal top, two vertical sides, and a horizontal bottom on the right. Digit 3 has a horizontal top, two vertical sides, and a horizontal bottom. Digit 4 has a horizontal top, a vertical line on the left, and two vertical lines on the right. Digit 5 has a horizontal top, a vertical line on the left, and a horizontal bottom. Digit 6 has a horizontal top, a vertical line on the left, and a horizontal bottom, with a horizontal line in the middle. Digit 7 has a horizontal top and two vertical lines on the right. Digit 8 has a horizontal top, two vertical sides, and a horizontal bottom, with a horizontal line in the middle. Digit 9 has a horizontal top, two vertical sides, and a horizontal bottom, with a horizontal line in the middle.](d3294dc879b451b369c0b06f42e9b39f_img.jpg)

Figure 2: A row of matchstick representations for digits 0 through 9. Digit 0 is a rectangle. Digit 1 is a single vertical line. Digit 2 has a horizontal top, two vertical sides, and a horizontal bottom on the right. Digit 3 has a horizontal top, two vertical sides, and a horizontal bottom. Digit 4 has a horizontal top, a vertical line on the left, and two vertical lines on the right. Digit 5 has a horizontal top, a vertical line on the left, and a horizontal bottom. Digit 6 has a horizontal top, a vertical line on the left, and a horizontal bottom, with a horizontal line in the middle. Digit 7 has a horizontal top and two vertical lines on the right. Digit 8 has a horizontal top, two vertical sides, and a horizontal bottom, with a horizontal line in the middle. Digit 9 has a horizontal top, two vertical sides, and a horizontal bottom, with a horizontal line in the middle.

图 2 用木棒表示的 0~9

## 【输入数据】

从文件 game.in 中读入一行字符串。该串中包括一个以 “#” 字符结尾的式子（ASCII 码 35），式子中没有空格或其他分隔符。输入数据严格符合逻辑。字符串的长度小于等于 1000。

{1}------------------------------------------------

**注意：“#”字符后面可能会有一些与题目无关的字符。**

## **【输出数据】**

输出结果到文件 game.out，输出仅一行。

如果有解，则输出正确的等式，格式与输入的格式相同（以“#”结尾，中间不能有分隔符，也不要加入多余字符）。

如果无解，则输出“No”（N 大写，o 小写）。

## **【输入样例 1】**

1+1=3#

### **【输出样例 1】**

1+1=2#

## **【输入样例 2】**

1+1=3+5#

### **【输出样例 2】**

No

## **【输入样例 3】**

11+77=34#

### **【输出样例 3】**

17+17=34#