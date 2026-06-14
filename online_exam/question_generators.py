from __future__ import annotations

import heapq
import random
from bisect import bisect_left
from collections import Counter, deque
from dataclasses import dataclass
from math import gcd, isqrt
from typing import Callable


TestCase = dict[str, str]


@dataclass(frozen=True)
class TestGenerator:
    solve: Callable[[str], str]
    generate: Callable[[random.Random, int], str]


def build_generated_tests(task: dict, hidden_count: int = 10) -> dict[str, list[TestCase]]:
    generator = GENERATORS.get(task["id"])
    if generator is None:
        raise ValueError(f"missing programming test generator for {task['id']}")

    public_source = (task.get("public_tests") or task.get("tests") or [])[0]["input"]
    public_tests = [{"input": public_source, "output": _ensure_newline(generator.solve(public_source))}]

    rng = random.Random(task["id"])
    hidden_tests = []
    seen = {public_source}
    attempt = 0
    while len(hidden_tests) < hidden_count:
        attempt += 1
        if attempt > hidden_count * 20:
            raise ValueError(f"unable to generate enough hidden tests for {task['id']}")
        test_input = generator.generate(rng, len(hidden_tests))
        if test_input in seen:
            continue
        seen.add(test_input)
        hidden_tests.append({"input": test_input, "output": _ensure_newline(generator.solve(test_input))})

    return {"public_tests": public_tests, "hidden_tests": hidden_tests, "tests": public_tests + hidden_tests}


def missing_generator_ids(tasks: list[dict]) -> list[str]:
    return [task["id"] for task in tasks if task["id"] not in GENERATORS]


def _ensure_newline(value: str) -> str:
    return value if value.endswith("\n") else value + "\n"


def _ints(data: str) -> list[int]:
    return list(map(int, data.split()))


def _join(values) -> str:
    return " ".join(map(str, values))


def solve_row_col(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    pos = 2
    grid = []
    for _ in range(n):
        grid.append(values[pos : pos + m])
        pos += m
    x, y = values[pos] - 1, values[pos + 1] - 1
    return str(sum(grid[x]) + sum(row[y] for row in grid) - grid[x][y])


def gen_row_col(rng, i) -> str:
    n, m = rng.randint(1, 8), rng.randint(1, 8)
    grid = [[rng.randint(0, 50) for _ in range(m)] for _ in range(n)]
    x, y = rng.randint(1, n), rng.randint(1, m)
    return f"{n} {m}\n" + "\n".join(_join(row) for row in grid) + f"\n{x} {y}\n"


def solve_prime_count(data: str) -> str:
    L, R = _ints(data)
    if R < 2:
        return "0"
    sieve = [True] * (R + 1)
    sieve[0:2] = [False, False]
    for p in range(2, isqrt(R) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : R + 1 : p] = [False] * (((R - start) // p) + 1)
    return str(sum(1 for x in range(max(2, L), R + 1) if sieve[x]))


def gen_prime_count(rng, i) -> str:
    L = rng.randint(1, 2000)
    R = L + rng.randint(0, 600)
    return f"{L} {R}\n"


def solve_tasks(data: str) -> str:
    values = _ints(data)
    n, total = values[0], values[1]
    used = count = 0
    for cost in sorted(values[2 : 2 + n]):
        if used + cost > total:
            break
        used += cost
        count += 1
    return str(count)


def gen_tasks(rng, i) -> str:
    n = rng.randint(1, 18)
    arr = [rng.randint(1, 40) for _ in range(n)]
    total = rng.randint(0, sum(arr) + 10)
    return f"{n} {total}\n{_join(arr)}\n"


def solve_longest_rise(data: str) -> str:
    values = _ints(data)
    arr = values[1:]
    best = cur = 1
    for a, b in zip(arr, arr[1:]):
        cur = cur + 1 if b > a else 1
        best = max(best, cur)
    return str(best)


def gen_array(rng, i, n_min=1, n_max=25, low=-20, high=40) -> list[int]:
    return [rng.randint(low, high) for _ in range(rng.randint(n_min, n_max))]


def gen_longest_rise(rng, i) -> str:
    arr = gen_array(rng, i)
    return f"{len(arr)}\n{_join(arr)}\n"


def solve_recurrence(data: str) -> str:
    n = _ints(data)[0]
    a, b = 1, 2
    if n == 1:
        return "1"
    for _ in range(3, n + 1):
        a, b = b, b + 2 * a
    return str(b)


def gen_single_n(rng, i, lo=1, hi=40) -> str:
    return f"{rng.randint(lo, hi)}\n"


def solve_gcd_lcm(data: str) -> str:
    a, b = _ints(data)
    g = gcd(a, b)
    return f"{g} {a // g * b}"


def gen_two_positive(rng, i, hi=100000) -> str:
    return f"{rng.randint(1, hi)} {rng.randint(1, hi)}\n"


def solve_prefix_sum(data: str) -> str:
    values = _ints(data)
    n, q = values[0], values[1]
    arr = values[2 : 2 + n]
    pref = [0]
    for x in arr:
        pref.append(pref[-1] + x)
    pos = 2 + n
    out = []
    for _ in range(q):
        l, r = values[pos], values[pos + 1]
        pos += 2
        out.append(str(pref[r] - pref[l - 1]))
    return "\n".join(out)


def gen_prefix_sum(rng, i) -> str:
    n, q = rng.randint(1, 18), rng.randint(1, 10)
    arr = [rng.randint(-20, 40) for _ in range(n)]
    queries = []
    for _ in range(q):
        l = rng.randint(1, n)
        r = rng.randint(l, n)
        queries.append(f"{l} {r}")
    return f"{n} {q}\n{_join(arr)}\n" + "\n".join(queries) + "\n"


def solve_sort_students(data: str) -> str:
    values = _ints(data)
    n = values[0]
    students = [(values[i], values[i + 1]) for i in range(1, 2 * n + 1, 2)]
    students.sort(key=lambda x: (-x[1], x[0]))
    return _join(sid for sid, _ in students)


def gen_sort_students(rng, i) -> str:
    n = rng.randint(1, 12)
    ids = rng.sample(range(1, 200), n)
    rows = [f"{sid} {rng.randint(0, 100)}" for sid in ids]
    return f"{n}\n" + "\n".join(rows) + "\n"


def solve_prime_pair(data: str) -> str:
    n = _ints(data)[0]
    if n < 3:
        return "0"
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for p in range(2, isqrt(n) + 1):
        if sieve[p]:
            sieve[p * p : n + 1 : p] = [False] * (((n - p * p) // p) + 1)
    return str(sum(1 for p in range(2, n - 1) if sieve[p] and sieve[p + 2]))


def gen_prime_pair(rng, i) -> str:
    return f"{rng.randint(1, 5000)}\n"


def solve_delete_value(data: str) -> str:
    values = _ints(data)
    n, x = values[0], values[1]
    kept = [v for v in values[2 : 2 + n] if v != x]
    return _join(kept) if kept else "EMPTY"


def gen_delete_value(rng, i) -> str:
    n = rng.randint(1, 20)
    x = rng.randint(-5, 5)
    arr = [rng.randint(-5, 5) for _ in range(n)]
    return f"{n} {x}\n{_join(arr)}\n"


def solve_brackets(data: str) -> str:
    stack = []
    pairs = {")": "(", "]": "["}
    for ch in data.strip():
        if ch in "([":
            stack.append(ch)
        elif not stack or stack.pop() != pairs[ch]:
            return "NO"
    return "YES" if not stack else "NO"


def gen_brackets(rng, i) -> str:
    samples = ["([]())", "([)]", "(([]))[]", "([[]])()", "(()", "][", "", "([][][])", "([[[[]]]])", "()[](["]
    return (samples[i % len(samples)] or "()") + "\n"


def solve_two_sum_pairs(data: str) -> str:
    values = _ints(data)
    n, target = values[0], values[1]
    arr = values[2 : 2 + n]
    left, right, ans = 0, n - 1, 0
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            if arr[left] == arr[right]:
                c = right - left + 1
                ans += c * (c - 1) // 2
                break
            lv, rv = arr[left], arr[right]
            lc = rc = 0
            while left <= right and arr[left] == lv:
                lc += 1
                left += 1
            while right >= left and arr[right] == rv:
                rc += 1
                right -= 1
            ans += lc * rc
        elif s < target:
            left += 1
        else:
            right -= 1
    return str(ans)


def gen_two_sum_pairs(rng, i) -> str:
    arr = sorted(gen_array(rng, i, 2, 25, -10, 20))
    target = rng.randint(-10, 30)
    return f"{len(arr)} {target}\n{_join(arr)}\n"


def solve_stairs(data: str) -> str:
    n = _ints(data)[0]
    a, b = 1, 2
    if n == 1:
        return "1"
    for _ in range(3, n + 1):
        a, b = b, a + b
    return str(b)


class DSU:
    def __init__(self, n):
        self.parent = list(range(n + 1))
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def solve_count_components(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    dsu = DSU(n)
    pos = 2
    for _ in range(m):
        dsu.union(values[pos], values[pos + 1])
        pos += 2
    return str(len({dsu.find(i) for i in range(1, n + 1)}))


def gen_edges(rng, i, directed=False) -> str:
    n = rng.randint(1, 15)
    m = rng.randint(0, min(35, n * (n - 1) // (1 if directed else 2)))
    edges = set()
    while len(edges) < m:
        a, b = rng.randint(1, n), rng.randint(1, n)
        if a == b:
            continue
        edge = (a, b) if directed else tuple(sorted((a, b)))
        edges.add(edge)
    return f"{n} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges)


def solve_merge_intervals(data: str) -> str:
    values = _ints(data)
    intervals = [(values[i], values[i + 1]) for i in range(1, len(values), 2)]
    intervals.sort()
    merged = []
    for l, r in intervals:
        if not merged or l > merged[-1][1]:
            merged.append([l, r])
        else:
            merged[-1][1] = max(merged[-1][1], r)
    return str(len(merged))


def gen_merge_intervals(rng, i) -> str:
    n = rng.randint(1, 18)
    rows = []
    for _ in range(n):
        l = rng.randint(0, 50)
        r = l + rng.randint(0, 15)
        rows.append(f"{l} {r}")
    return f"{n}\n" + "\n".join(rows) + "\n"


def solve_grid_bfs(data: str) -> str:
    lines = data.strip("\n").splitlines()
    n, m = map(int, lines[0].split())
    grid = lines[1 : 1 + n]
    if grid[0][0] == "#" or grid[-1][-1] == "#":
        return "-1"
    dist = [[-1] * m for _ in range(n)]
    q = deque([(0, 0)])
    dist[0][0] = 0
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == "." and dist[nx][ny] == -1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))
    return str(dist[-1][-1])


def gen_grid_bfs(rng, i) -> str:
    n, m = rng.randint(1, 8), rng.randint(1, 8)
    grid = []
    for x in range(n):
        row = []
        for y in range(m):
            row.append("#" if rng.random() < 0.25 else ".")
        grid.append(row)
    grid[0][0] = grid[-1][-1] = "."
    return f"{n} {m}\n" + "\n".join("".join(row) for row in grid) + "\n"


def solve_knapsack01(data: str) -> str:
    values = _ints(data)
    n, cap = values[0], values[1]
    dp = [0] * (cap + 1)
    pos = 2
    for _ in range(n):
        w, v = values[pos], values[pos + 1]
        pos += 2
        for c in range(cap, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return str(max(dp))


def gen_knapsack01(rng, i) -> str:
    n, cap = rng.randint(1, 12), rng.randint(1, 40)
    rows = [f"{rng.randint(1, 20)} {rng.randint(1, 60)}" for _ in range(n)]
    return f"{n} {cap}\n" + "\n".join(rows) + "\n"


def solve_lis(data: str) -> str:
    values = _ints(data)
    tails = []
    for x in values[1:]:
        idx = bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return str(len(tails))


def gen_lis(rng, i) -> str:
    arr = gen_array(rng, i, 1, 30, -20, 50)
    return f"{len(arr)}\n{_join(arr)}\n"


def solve_big_add(data: str) -> str:
    a, b = data.splitlines()[:2]
    return str(int(a) + int(b))


def gen_big_add(rng, i) -> str:
    a = "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(1, 35))).lstrip("0") or "0"
    b = "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(1, 35))).lstrip("0") or "0"
    return f"{a}\n{b}\n"


def solve_top_k(data: str) -> str:
    values = _ints(data)
    n, k = values[0], values[1]
    return str(sorted(values[2 : 2 + n], reverse=True)[k - 1])


def gen_top_k(rng, i) -> str:
    arr = gen_array(rng, i, 1, 30, -100, 100)
    k = rng.randint(1, len(arr))
    return f"{len(arr)} {k}\n{_join(arr)}\n"


def solve_quick_power(data: str) -> str:
    a, b, m = _ints(data)
    return str(pow(a, b, m))


def gen_quick_power(rng, i) -> str:
    return f"{rng.randint(0, 10**9)} {rng.randint(0, 10**6)} {rng.randint(1, 10**9)}\n"


def solve_rotate_array(data: str) -> str:
    values = _ints(data)
    n, k = values[0], values[1]
    arr = values[2 : 2 + n]
    k %= n
    return _join(arr[-k:] + arr[:-k]) if k else _join(arr)


def gen_rotate_array(rng, i) -> str:
    arr = gen_array(rng, i, 1, 25, -20, 20)
    return f"{len(arr)} {rng.randint(0, 100)}\n{_join(arr)}\n"


def solve_matrix_border(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    pos = 2
    total = 0
    for i in range(n):
        for j in range(m):
            val = values[pos]
            pos += 1
            if i in (0, n - 1) or j in (0, m - 1):
                total += val
    return str(total)


def gen_matrix(rng, i, n_max=8, m_max=8) -> str:
    n, m = rng.randint(1, n_max), rng.randint(1, m_max)
    grid = [[rng.randint(-20, 50) for _ in range(m)] for _ in range(n)]
    return f"{n} {m}\n" + "\n".join(_join(row) for row in grid) + "\n"


def solve_date_next(data: str) -> str:
    y, m, d = _ints(data)
    leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)
    days = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    d += 1
    if d > days[m]:
        d = 1
        m += 1
    if m > 12:
        m = 1
        y += 1
    return f"{y} {m} {d}"


def gen_date_next(rng, i) -> str:
    dates = [(2024, 2, 28), (2025, 2, 28), (2000, 2, 29), (2099, 12, 31)]
    if i < len(dates):
        y, m, d = dates[i]
    else:
        y, m = rng.randint(1900, 2100), rng.randint(1, 12)
        leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)
        days = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        d = rng.randint(1, days[m])
    return f"{y} {m} {d}\n"


def solve_indegree_zero(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    indeg = [0] * (n + 1)
    for i in range(2, 2 + 2 * m, 2):
        indeg[values[i + 1]] += 1
    return str(sum(1 for x in indeg[1:] if x == 0))


def gen_directed_edges(rng, i) -> str:
    return gen_edges(rng, i, directed=True)


def solve_dijkstra(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    graph = [[] for _ in range(n + 1)]
    pos = 2
    for _ in range(m):
        u, v, w = values[pos], values[pos + 1], values[pos + 2]
        pos += 3
        graph[u].append((v, w))
        graph[v].append((u, w))
    dist = [10**30] * (n + 1)
    dist[1] = 0
    heap = [(0, 1)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return str(-1 if dist[n] == 10**30 else dist[n])


def gen_weighted_graph(rng, i) -> str:
    n = rng.randint(2, 12)
    edges = {(j, j + 1): rng.randint(1, 20) for j in range(1, n)}
    for _ in range(rng.randint(0, 20)):
        a, b = sorted((rng.randint(1, n), rng.randint(1, n)))
        if a != b:
            edges[(a, b)] = rng.randint(1, 50)
    return f"{n} {len(edges)}\n" + "".join(f"{a} {b} {w}\n" for (a, b), w in edges.items())


def solve_binary_answer(data: str) -> str:
    values = _ints(data)
    n, k = values[0], values[1]
    pos = sorted(values[2 : 2 + n])
    lo, hi = 0, pos[-1] - pos[0]
    def ok(d):
        count, last = 1, pos[0]
        for x in pos[1:]:
            if x - last >= d:
                count += 1
                last = x
        return count >= k
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return str(lo)


def gen_binary_answer(rng, i) -> str:
    n = rng.randint(2, 25)
    arr = sorted(rng.sample(range(0, 200), n))
    k = rng.randint(2, n)
    return f"{n} {k}\n{_join(arr)}\n"


def solve_edit_distance(data: str) -> str:
    a, b = data.strip("\n").splitlines()[:2]
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        ndp = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            ndp[j] = min(dp[j] + 1, ndp[j - 1] + 1, dp[j - 1] + (ca != cb))
        dp = ndp
    return str(dp[-1])


def gen_two_strings(rng, i) -> str:
    alphabet = "abcd"
    a = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 12)))
    b = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 12)))
    return f"{a}\n{b}\n"


def solve_min_coins(data: str) -> str:
    values = _ints(data)
    n, amount = values[0], values[1]
    coins = values[2 : 2 + n]
    inf = 10**9
    dp = [0] + [inf] * amount
    for coin in coins:
        for s in range(coin, amount + 1):
            dp[s] = min(dp[s], dp[s - coin] + 1)
    return str(-1 if dp[amount] == inf else dp[amount])


def gen_min_coins(rng, i) -> str:
    n = rng.randint(1, 8)
    coins = rng.sample(range(1, 30), n)
    amount = rng.randint(0, 120)
    return f"{n} {amount}\n{_join(coins)}\n"


def solve_sliding_window(data: str) -> str:
    values = _ints(data)
    n, target = values[0], values[1]
    arr = values[2 : 2 + n]
    left = total = 0
    best = n + 1
    for right, val in enumerate(arr):
        total += val
        while total >= target:
            best = min(best, right - left + 1)
            total -= arr[left]
            left += 1
    return str(0 if best == n + 1 else best)


def gen_sliding_window(rng, i) -> str:
    arr = [rng.randint(1, 30) for _ in range(rng.randint(1, 25))]
    target = rng.randint(1, sum(arr) + 30)
    return f"{len(arr)} {target}\n{_join(arr)}\n"


def solve_kmp_count(data: str) -> str:
    s, p = data.strip("\n").splitlines()[:2]
    return str(sum(1 for i in range(0, len(s) - len(p) + 1) if s.startswith(p, i)))


def gen_kmp(rng, i) -> str:
    alphabet = "abca"
    s = "".join(rng.choice(alphabet) for _ in range(rng.randint(5, 30)))
    start = rng.randint(0, max(0, len(s) - 3))
    p = s[start : start + rng.randint(1, min(5, len(s) - start))]
    return f"{s}\n{p}\n"


def solve_interval_diff(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    diff = [0] * (n + 2)
    pos = 2
    for _ in range(m):
        l, r, x = values[pos], values[pos + 1], values[pos + 2]
        pos += 3
        diff[l] += x
        diff[r + 1] -= x
    cur = best = diff[1]
    for i in range(2, n + 1):
        cur += diff[i]
        best = max(best, cur)
    return str(best)


def gen_interval_diff(rng, i) -> str:
    n, m = rng.randint(1, 25), rng.randint(1, 20)
    rows = []
    for _ in range(m):
        l = rng.randint(1, n)
        r = rng.randint(l, n)
        rows.append(f"{l} {r} {rng.randint(-20, 50)}")
    return f"{n} {m}\n" + "\n".join(rows) + "\n"


def solve_2d_prefix(data: str) -> str:
    values = _ints(data)
    n, m, q = values[0], values[1], values[2]
    pos = 3
    pref = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            pref[i][j] = values[pos] + pref[i - 1][j] + pref[i][j - 1] - pref[i - 1][j - 1]
            pos += 1
    out = []
    for _ in range(q):
        x1, y1, x2, y2 = values[pos : pos + 4]
        pos += 4
        out.append(str(pref[x2][y2] - pref[x1 - 1][y2] - pref[x2][y1 - 1] + pref[x1 - 1][y1 - 1]))
    return "\n".join(out)


def gen_2d_prefix(rng, i) -> str:
    n, m, q = rng.randint(1, 8), rng.randint(1, 8), rng.randint(1, 8)
    grid = [[rng.randint(-10, 20) for _ in range(m)] for _ in range(n)]
    queries = []
    for _ in range(q):
        x1, x2 = sorted((rng.randint(1, n), rng.randint(1, n)))
        y1, y2 = sorted((rng.randint(1, m), rng.randint(1, m)))
        queries.append(f"{x1} {y1} {x2} {y2}")
    return f"{n} {m} {q}\n" + "\n".join(_join(row) for row in grid) + "\n" + "\n".join(queries) + "\n"


def solve_toposort(data: str) -> str:
    values = _ints(data)
    n, m = values[0], values[1]
    graph = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    pos = 2
    for _ in range(m):
        a, b = values[pos], values[pos + 1]
        pos += 2
        graph[a].append(b)
        indeg[b] += 1
    q = deque(i for i in range(1, n + 1) if indeg[i] == 0)
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return "YES" if seen == n else "NO"


def solve_median_stream(data: str) -> str:
    values = _ints(data)
    low, high, out = [], [], []
    for idx, x in enumerate(values[1:], 1):
        heapq.heappush(low, -x)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if idx % 2 == 1:
            out.append(str(-low[0]))
    return _join(out)


def gen_median_stream(rng, i) -> str:
    arr = gen_array(rng, i, 1, 25, -50, 50)
    return f"{len(arr)}\n{_join(arr)}\n"


def solve_tree_depth(data: str) -> str:
    values = _ints(data)
    n = values[0]
    graph = [[] for _ in range(n + 1)]
    for i in range(1, len(values), 2):
        a, b = values[i], values[i + 1]
        graph[a].append(b)
        graph[b].append(a)
    q = deque([(1, 1, 0)])
    best = 1
    while q:
        u, depth, parent = q.popleft()
        best = max(best, depth)
        for v in graph[u]:
            if v != parent:
                q.append((v, depth + 1, u))
    return str(best)


def gen_tree(rng, i) -> str:
    n = rng.randint(1, 25)
    rows = [f"{rng.randint(1, v - 1)} {v}" for v in range(2, n + 1)]
    return f"{n}\n" + "\n".join(rows) + ("\n" if rows else "")


def solve_shortest_window(data: str) -> str:
    s, t = data.strip("\n").splitlines()[:2]
    need = Counter(t)
    missing = len(t)
    left = 0
    best = len(s) + 1
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            best = min(best, right - left + 1)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return str(0 if best == len(s) + 1 else best)


def gen_shortest_window(rng, i) -> str:
    alphabet = "abcde"
    s = "".join(rng.choice(alphabet) for _ in range(rng.randint(5, 30)))
    t = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 5)))
    return f"{s}\n{t}\n"


def solve_magic_duel(data: str) -> str:
    values = _ints(data)
    n = values[0]
    scores = [0, 0]
    last_hit = {}
    pos = 1
    for _ in range(n):
        t, a, _b = values[pos], values[pos + 1], values[pos + 2]
        pos += 3
        team = 0 if a <= 4 else 1
        scores[team] += 100
        if a in last_hit and 1 <= t - last_hit[a] <= 10:
            scores[team] += 50
        last_hit[a] = t
    return f"{scores[0]} {scores[1]}"


def gen_magic_duel(rng, i) -> str:
    n = rng.randint(1, 20)
    t = rng.randint(0, 5)
    rows = []
    for _ in range(n):
        t += rng.randint(1, 15)
        a = rng.randint(1, 8)
        b = rng.randint(5, 8) if a <= 4 else rng.randint(1, 4)
        rows.append(f"{t} {a} {b}")
    return f"{n}\n" + "\n".join(rows) + "\n"


def solve_bookshelf(data: str) -> str:
    values = _ints(data)
    t = values[0]
    pos = 1
    out = []
    for _ in range(t):
        n = values[pos]
        pos += 1
        books = sorted(values[pos : pos + n])
        pos += n
        shelves = sorted(values[pos : pos + n])
        pos += n
        out.append("YES" if all(a <= b for a, b in zip(books, shelves)) else "NO")
    return "\n".join(out)


def gen_bookshelf(rng, i) -> str:
    cases = rng.randint(1, 5)
    rows = [str(cases)]
    for _ in range(cases):
        n = rng.randint(1, 10)
        books = [rng.randint(1, 100) for _ in range(n)]
        shelves = [rng.randint(1, 100) for _ in range(n)]
        rows.extend([str(n), _join(books), _join(shelves)])
    return "\n".join(rows) + "\n"


def solve_palindrome(data: str) -> str:
    s = data.strip()
    best = 0
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                best = max(best, right - left + 1)
                left -= 1
                right += 1
    return str(best)


def gen_palindrome(rng, i) -> str:
    alphabet = "abcde"
    s = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 40)))
    return s + "\n"


def solve_matrix_match(data: str) -> str:
    lines = data.strip("\n").splitlines()
    t = int(lines[0])
    idx = 1
    out = []
    for _ in range(t):
        n, k = map(int, lines[idx].split())
        idx += 1
        grid = lines[idx : idx + n]
        idx += n
        ok = False
        for start in range(0, n - k + 1):
            seen = set()
            for row in grid:
                sig = "".join(sorted(row[start : start + k]))
                if sig in seen:
                    ok = True
                    break
                seen.add(sig)
            if ok:
                break
        out.append("YES" if ok else "NO")
    return "\n".join(out)


def gen_matrix_match(rng, i) -> str:
    cases = rng.randint(1, 4)
    rows = [str(cases)]
    for _ in range(cases):
        n = rng.randint(2, 8)
        k = rng.randint(2, n)
        grid = ["".join(rng.choice("abcd") for _ in range(n)) for _ in range(n)]
        rows.append(f"{n} {k}")
        rows.extend(grid)
    return "\n".join(rows) + "\n"


def solve_cat_fish(data: str) -> str:
    values = _ints(data)
    t = values[0]
    pos = 1
    out = []
    for _ in range(t):
        n, x = values[pos], values[pos + 1]
        pos += 2
        out.append(chr(ord("A") + (x - 1) % n))
    return "\n".join(out)


def gen_cat_fish(rng, i) -> str:
    cases = rng.randint(1, 5)
    rows = [str(cases)]
    for _ in range(cases):
        rows.append(f"{rng.randint(1, 26)} {rng.randint(1, 10**6)}")
    return "\n".join(rows) + "\n"


def solve_transport(data: str) -> str:
    values = _ints(data)
    t = values[0]
    pos = 1
    out = []
    for _ in range(t):
        a, b, c = values[pos], values[pos + 1], values[pos + 2]
        pos += 3
        out.append("Yes" if any((c - a * x) >= 0 and (c - a * x) % b == 0 for x in range(c // a + 1)) else "No")
    return "\n".join(out)


def gen_transport(rng, i) -> str:
    cases = rng.randint(1, 5)
    rows = [str(cases)]
    for _ in range(cases):
        rows.append(f"{rng.randint(1, 100)} {rng.randint(1, 100)} {rng.randint(1, 1000)}")
    return "\n".join(rows) + "\n"


def solve_travel(data: str) -> str:
    values = _ints(data)
    n = values[0]
    arr = values[1 : 1 + n]
    nums = set(arr)
    count = 0
    for x in arr:
        found = False
        for a in arr:
            b = x - a
            if b != a and b in nums:
                found = True
                break
        count += found
    return str(count)


def gen_travel(rng, i) -> str:
    n = rng.randint(3, 20)
    arr = rng.sample(range(1, 200), n)
    return f"{n}\n{_join(arr)}\n"


def solve_surrounded(data: str) -> str:
    lines = data.strip("\n").splitlines()
    n, m = map(int, lines[0].split())
    grid = [list(row) for row in lines[1 : 1 + n]]
    seen = [[False] * m for _ in range(n)]
    total = 0
    for i in range(n):
        for j in range(m):
            if grid[i][j] != "." or seen[i][j]:
                continue
            q = deque([(i, j)])
            seen[i][j] = True
            cells = 0
            touches_border = False
            while q:
                x, y = q.popleft()
                cells += 1
                touches_border |= x in (0, n - 1) or y in (0, m - 1)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == "." and not seen[nx][ny]:
                        seen[nx][ny] = True
                        q.append((nx, ny))
            if not touches_border:
                total += cells
    return str(total)


def gen_surrounded(rng, i) -> str:
    n, m = rng.randint(3, 10), rng.randint(3, 10)
    grid = []
    for _ in range(n):
        grid.append("".join("." if rng.random() < 0.35 else "#" for _ in range(m)))
    return f"{n} {m}\n" + "\n".join(grid) + "\n"


def solve_resource_score_summary(data: str) -> str:
    values = _ints(data)
    n = values[0]
    scores = values[1 : 1 + n]
    return f"{sum(score >= 60 for score in scores)} {max(scores)}"


def gen_resource_score_summary(rng, i) -> str:
    n = rng.randint(1, 30)
    scores = [rng.randint(0, 100) for _ in range(n)]
    return f"{n}\n{_join(scores)}\n"


def solve_resource_topic_count(data: str) -> str:
    lines = data.strip("\n").splitlines()
    n = int(lines[0])
    return str(len({line.strip().lower() for line in lines[1 : 1 + n]}))


def gen_resource_topic_count(rng, i) -> str:
    base = ["cpp", "python", "graph", "array", "string", "dp", "bfs", "sort", "loop"]
    n = rng.randint(1, 25)
    rows = []
    for _ in range(n):
        word = rng.choice(base)
        rows.append("".join(ch.upper() if rng.random() < 0.5 else ch for ch in word))
    return f"{n}\n" + "\n".join(rows) + "\n"


def solve_resource_route_energy(data: str) -> str:
    values = _ints(data)
    n = values[0]
    scores = values[1 : 1 + n]
    if n == 1:
        return str(scores[0])
    dp0 = scores[0]
    dp1 = scores[0] + scores[1]
    for score in scores[2:]:
        dp0, dp1 = dp1, max(dp0, dp1) + score
    return str(dp1)


def gen_resource_route_energy(rng, i) -> str:
    n = rng.randint(1, 25)
    scores = [rng.randint(-20, 50) for _ in range(n)]
    return f"{n}\n{_join(scores)}\n"


def solve_resource_practice_streak(data: str) -> str:
    values = _ints(data)
    n, target = values[0], values[1]
    arr = values[2 : 2 + n]
    left = total = 0
    best = n + 1
    for right, value in enumerate(arr):
        total += value
        while total >= target:
            best = min(best, right - left + 1)
            total -= arr[left]
            left += 1
    return str(0 if best == n + 1 else best)


def gen_resource_practice_streak(rng, i) -> str:
    n = rng.randint(1, 30)
    arr = [rng.randint(1, 20) for _ in range(n)]
    target = rng.randint(1, sum(arr) + 20)
    return f"{n} {target}\n{_join(arr)}\n"


def solve_resource_rank_list(data: str) -> str:
    values = _ints(data)
    n = values[0]
    players = []
    pos = 1
    for _ in range(n):
        sid, a, b = values[pos], values[pos + 1], values[pos + 2]
        pos += 3
        players.append((sid, a + b))
    players.sort(key=lambda item: (-item[1], item[0]))
    return _join(sid for sid, _score in players)


def gen_resource_rank_list(rng, i) -> str:
    n = rng.randint(1, 20)
    ids = rng.sample(range(1, 1000), n)
    rows = [str(n)]
    for sid in ids:
        rows.append(f"{sid} {rng.randint(0, 100)} {rng.randint(0, 100)}")
    return "\n".join(rows) + "\n"


def solve_resource_safe_area(data: str) -> str:
    lines = data.strip("\n").splitlines()
    n, m = map(int, lines[0].split())
    grid = lines[1 : 1 + n]
    if grid[0][0] == "#" or grid[n - 1][m - 1] == "#":
        return "-1"
    dist = [[-1] * m for _ in range(n)]
    dist[0][0] = 0
    q = deque([(0, 0)])
    while q:
        x, y = q.popleft()
        if x == n - 1 and y == m - 1:
            return str(dist[x][y])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == "." and dist[nx][ny] == -1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))
    return "-1"


def gen_resource_safe_area(rng, i) -> str:
    n, m = rng.randint(1, 10), rng.randint(1, 10)
    grid = []
    for x in range(n):
        row = []
        for y in range(m):
            if (x, y) in ((0, 0), (n - 1, m - 1)):
                row.append(".")
            else:
                row.append("#" if rng.random() < 0.28 else ".")
        grid.append("".join(row))
    return f"{n} {m}\n" + "\n".join(grid) + "\n"


def solve_silk_double_order(data: str) -> str:
    return str(_ints(data)[0] * 2)


def gen_silk_double_order(rng, i) -> str:
    return f"{rng.randint(1, 10**9)}\n"


def solve_silk_country_code(data: str) -> str:
    s = data.strip()
    return s[0] + s[-1]


def gen_silk_country_code(rng, i) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    n = rng.randint(3, 16)
    s = "".join(rng.choice(alphabet) for _ in range(n))
    if rng.random() < 0.3:
        s = s.capitalize()
    return s + "\n"


def _split_csv_ints(line: str) -> list[int]:
    return [int(part) for part in line.strip().split(",") if part]


def _is_prime_value(x: int) -> bool:
    if x < 2:
        return False
    for d in range(2, isqrt(x) + 1):
        if x % d == 0:
            return False
    return True


def solve_silk_profit_combos(data: str) -> str:
    lines = data.strip("\n").splitlines()
    n = int(lines[0])
    values = _split_csv_ints(lines[1])[:n]
    k = int(lines[2])
    sums = set()

    def dfs(index: int, count: int, total: int) -> None:
        if count == k:
            sums.add(total)
            return
        if index == n or count + (n - index) < k:
            return
        dfs(index + 1, count + 1, total + values[index])
        dfs(index + 1, count, total)

    dfs(0, 0, 0)
    composite = sum(value > 1 and not _is_prime_value(value) for value in sums)
    return f"{len(sums)},{composite}"


def gen_silk_profit_combos(rng, i) -> str:
    n = rng.randint(2, 12)
    values = [rng.randint(1, 30) for _ in range(n)]
    k = rng.randint(2, n)
    return f"{n}\n{','.join(map(str, values))}\n{k}\n"


def solve_silk_yanghui_column(data: str) -> str:
    lines = data.strip("\n").splitlines()
    n = int(lines[0])
    x, y = _split_csv_ints(lines[1])
    tri = [[0] * (n + 2) for _ in range(n + 2)]
    for i in range(1, n + 1):
        tri[i][1] = tri[i][i] = 1
        for j in range(2, i):
            tri[i][j] = tri[i - 1][j - 1] + tri[i - 1][j]
    return f"{tri[x][y]},{sum(tri[row][y] for row in range(1, n + 1))}"


def gen_silk_yanghui_column(rng, i) -> str:
    n = rng.randint(2, 30)
    x = rng.randint(1, n)
    y = rng.randint(1, x)
    return f"{n}\n{x},{y}\n"


GENERATORS = {
    "p-row-col": TestGenerator(solve_row_col, gen_row_col),
    "p-prime-count": TestGenerator(solve_prime_count, gen_prime_count),
    "p-tasks": TestGenerator(solve_tasks, gen_tasks),
    "p-longest-rise": TestGenerator(solve_longest_rise, gen_longest_rise),
    "p-recurrence": TestGenerator(solve_recurrence, lambda r, i: gen_single_n(r, i, 1, 40)),
    "p-official-gcd-lcm": TestGenerator(solve_gcd_lcm, gen_two_positive),
    "p-official-prefix-sum": TestGenerator(solve_prefix_sum, gen_prefix_sum),
    "p-official-sort-students": TestGenerator(solve_sort_students, gen_sort_students),
    "p-official-prime-pair": TestGenerator(solve_prime_pair, gen_prime_pair),
    "p-official-delete-value": TestGenerator(solve_delete_value, gen_delete_value),
    "p-official-brackets": TestGenerator(solve_brackets, gen_brackets),
    "p-official-two-sum-pairs": TestGenerator(solve_two_sum_pairs, gen_two_sum_pairs),
    "p-official-stairs": TestGenerator(solve_stairs, lambda r, i: gen_single_n(r, i, 1, 45)),
    "p-official-count-components": TestGenerator(solve_count_components, gen_edges),
    "p-official-merge-intervals": TestGenerator(solve_merge_intervals, gen_merge_intervals),
    "p-official-grid-bfs": TestGenerator(solve_grid_bfs, gen_grid_bfs),
    "p-official-knapsack01": TestGenerator(solve_knapsack01, gen_knapsack01),
    "p-official-lis": TestGenerator(solve_lis, gen_lis),
    "p-official-big-add": TestGenerator(solve_big_add, gen_big_add),
    "p-official-top-k": TestGenerator(solve_top_k, gen_top_k),
    "p-official-quick-power": TestGenerator(solve_quick_power, gen_quick_power),
    "p-official-rotate-array": TestGenerator(solve_rotate_array, gen_rotate_array),
    "p-official-matrix-border": TestGenerator(solve_matrix_border, gen_matrix),
    "p-official-date-next": TestGenerator(solve_date_next, gen_date_next),
    "p-official-topological": TestGenerator(solve_indegree_zero, gen_directed_edges),
    "p-advanced-dijkstra": TestGenerator(solve_dijkstra, gen_weighted_graph),
    "p-advanced-binary-answer": TestGenerator(solve_binary_answer, gen_binary_answer),
    "p-advanced-edit-distance": TestGenerator(solve_edit_distance, gen_two_strings),
    "p-advanced-min-coins": TestGenerator(solve_min_coins, gen_min_coins),
    "p-advanced-sliding-window": TestGenerator(solve_sliding_window, gen_sliding_window),
    "p-advanced-kmp": TestGenerator(solve_kmp_count, gen_kmp),
    "p-advanced-interval-diff": TestGenerator(solve_interval_diff, gen_interval_diff),
    "p-advanced-two-dimensional-prefix": TestGenerator(solve_2d_prefix, gen_2d_prefix),
    "p-advanced-toposort": TestGenerator(solve_toposort, gen_directed_edges),
    "p-advanced-median-stream": TestGenerator(solve_median_stream, gen_median_stream),
    "p-advanced-tree-depth": TestGenerator(solve_tree_depth, gen_tree),
    "p-advanced-shortest-window": TestGenerator(solve_shortest_window, gen_shortest_window),
    "fz-program-2060253670649495554": TestGenerator(solve_magic_duel, gen_magic_duel),
    "fz-program-2060254151874576386": TestGenerator(solve_bookshelf, gen_bookshelf),
    "fz-program-2060254980601937921": TestGenerator(solve_palindrome, gen_palindrome),
    "fz-program-2060255418978009089": TestGenerator(solve_matrix_match, gen_matrix_match),
    "fz-program-1981616592085245954": TestGenerator(solve_cat_fish, gen_cat_fish),
    "fz-program-1981616870851272705": TestGenerator(solve_transport, gen_transport),
    "fz-program-1981617147746639874": TestGenerator(solve_travel, gen_travel),
    "fz-program-1981617328273678337": TestGenerator(solve_surrounded, gen_surrounded),
    "p-resource-score-summary": TestGenerator(solve_resource_score_summary, gen_resource_score_summary),
    "p-resource-topic-count": TestGenerator(solve_resource_topic_count, gen_resource_topic_count),
    "p-resource-route-energy": TestGenerator(solve_resource_route_energy, gen_resource_route_energy),
    "p-resource-practice-streak": TestGenerator(solve_resource_practice_streak, gen_resource_practice_streak),
    "p-resource-rank-list": TestGenerator(solve_resource_rank_list, gen_resource_rank_list),
    "p-resource-safe-area": TestGenerator(solve_resource_safe_area, gen_resource_safe_area),
    "p-2026-silk-primary7-double-order": TestGenerator(solve_silk_double_order, gen_silk_double_order),
    "p-2026-silk-primary7-country-code": TestGenerator(solve_silk_country_code, gen_silk_country_code),
    "p-2026-silk-primary7-profit-combos": TestGenerator(solve_silk_profit_combos, gen_silk_profit_combos),
    "p-2026-silk-primary7-yanghui-column": TestGenerator(solve_silk_yanghui_column, gen_silk_yanghui_column),
}
