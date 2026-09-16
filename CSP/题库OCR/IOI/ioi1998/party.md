

{0}------------------------------------------------

![IOI logo with 'PORTUGAL 1998' text below it.](2dfa6ac3edfe874f68aa0cbccaa42322_img.jpg)

IOI logo with 'PORTUGAL 1998' text below it.

![IOI logo featuring a dolphin jumping over a wave.](64662465bba247703fdec49c8f3309f9_img.jpg)

IOI logo featuring a dolphin jumping over a wave.

# Party Lamps

To brighten up the gala dinner of the IOI'98 we have a set of  $N$  coloured lamps numbered from 1 to  $N$ . The lamps are connected to four buttons:

- button 1 -- when this button is pressed, all the lamps change their state: those that are ON are turned OFF and those that are OFF are turned ON.
- button 2 -- changes the state of all the odd numbered lamps.
- button 3 -- changes the state of all the even numbered lamps.
- button 4 -- changes the state of the lamps whose number is of the form  $3K+1$  (with  $K \geq 0$ ), i.e., 1, 4, 7, ...

There is a counter  $C$  which records the total number of button presses.

When the party starts, all the lamps are ON and the counter  $C$  is set to zero.

## Task

You are given the value of counter  $C$  and information on the final state of some of the lamps. Write a program to determine all the possible final configurations of the  $N$  lamps that are consistent with the given information, without repetitions.

## Input Data

The file named PARTY.IN with four lines, describing the number  $N$  of lamps available, the number  $C$  of button presses, and the state of some of the lamps in the final configuration.

The first line contains the number  $N$  and the second line the final value of counter  $C$ . The third line lists the lamp numbers you are informed to be ON in the final configuration, separated by one space and terminated by the integer **-1**. The fourth line lists the lamp numbers you are informed to be OFF in the final configuration, separated by one space and terminated by the integer **-1**.

### Sample Input:

```
10
1
-1
7 -1
```

In this case, there are 10 lamps and only one button has been pressed. Lamp 7 is OFF in the final configuration.

## Output Data

The file PARTY.OUT must contain all the possible final configurations (without repetitions) of all the lamps. Each possible configuration must be written on a different line. Configurations may be listed in arbitrary order.

Each line has  $N$  characters, where the first character represents the state of lamp 1 and the last character represents the state of lamp  $N$ . A **0** (zero) stands for a lamp that is OFF, and a **1** (one) stands for a lamp that is ON.

### Sample Output:

```
0000000000
0110110110
0101010101
```

In this case, there are three possible final configurations:

- either all lamps are OFF;
- or lamps 1, 4, 7, 10 are OFF, and lamps 2, 3, 5, 6, 8, 9 are ON;
- or lamps 1, 3, 5, 7, 9 are OFF, and lamps 2, 4, 6, 8, 10 are ON.

## Constraints

The parameters  $N$  and  $C$  are constrained by:

$$
10 \leq N \leq 100
$$

$$
1 \leq C \leq 10000
$$

The number of lamps you are informed to be ON, in the final configuration, is less than or equal to 2.

The number of lamps you are informed to be OFF, in the final configuration, is less than or equal to 2.

There is at least one possible final configuration for each input test file.