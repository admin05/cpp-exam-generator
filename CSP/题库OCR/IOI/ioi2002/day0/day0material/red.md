

{0}------------------------------------------------

# Red Devil

## PROBLEM

*Red Devil*, the Korean national soccer team supporters club will have a country-wide tour to  $N$  cities to celebrate the achievement in 2002 FIFA World Cup Korea/Japan.

Cities are represented by numbers  $1, 2, \dots, N$ . The Red Devil's tour starts with city 1 and visit all  $N$  cities exactly once, after which it should return to city 1, the starting position. The travel distance between two cities  $I$  and  $J$ , denoted by  $d(I, J)$  is known.

Note that the distance from city  $I$  to city  $J$  is symmetric to the distance from city  $J$  to city  $I$ , that is,  $d(I, J) = d(J, I)$ . For any three distinct cities  $I, J, K$ , it holds that  $d(I, K) \leq d(I, J) + d(J, K)$ . Furthermore it holds that  $d(I, I) = 0$  for any city  $I$ .

Given the distance between cities, you are to find a Red Devil's tour with the shortest possible length. You are given the input files describing the distances. **You must submit files describing the tours, not a program to find the tours.**

## INPUT

You are given 4 problem instances in the text files named `red1.in` to `red4.in`. Each input file is organized as follows. The first line contains one integer: the number of cities,  $N$ ,  $5 \leq N \leq 50$ . The following  $N$  lines represent the distance  $d(I, J)$ , where for each  $d(I, J)$  we have  $0 \leq d(I, J) \leq 50$ . These  $N$  lines are organized in such a way that the  $K$ -th of these  $N$  lines contains  $N$  integers: the distance  $d(K, 1), d(K, 2), \dots, d(K, N)$ . This way, the input is organized in the following form:

$$
\begin{array}{l} N \\ d(1,1) \ d(1,2) \ \dots \ d(1,N) \\ d(2,1) \ d(2,2) \ \dots \ d(2,N) \\ \dots \\ d(N,1) \ d(N,2) \ \dots \ d(N,N) \end{array}
$$

## OUTPUT

You are to submit 4 output files corresponding to the given input files. You do not need to submit your solution program source.

The first line contains the text

```
#FILE red I
```

, where integer  $I$  is the number of the respective input file. The second line contains  $N+1$  integers, which represent the cities in the order in which they are visited in the tour of your solution.

{1}------------------------------------------------

## EXAMPLE INPUTS AND OUTPUTS

Example1: red0.in

```
5
0 2 5 9 5
2 0 3 7 5
5 3 0 4 6
9 7 4 0 4
5 5 6 4 0
```

red0.out

```
#FILE red 0
1 3 2 5 4 1
```

## SCORING

If the output is not a valid tour, your score is zero. Otherwise, your score is  $5 + 20 \times \text{DistanceInBestAnswer} / \text{DistanceInYourAnswer}$ .

The score is rounded off to the first decimal place for each case. The total score is rounded off to the nearest integer.

Suppose that you submit the tour “1→3→2→5→4→1”. The length of your tour is 26. If the best of submitted solutions is a tour “1→2→3→4→5→1”, whose length is 18, your score becomes  $5 + 20 \times 18 / 26 (= 18.846\dots)$ , which will be rounded off to 18.8.