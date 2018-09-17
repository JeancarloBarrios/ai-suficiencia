from puzzle import Puzzle, AStar


def h_1(position):
    n = position.n
    def row(a): return a / n
    def col(a): return a % n
    score = 0
    for i, j in enumerate(position.state):
        if j == 0: continue
        ir, ic = row(i), col(i)
        xr, xc = row(j-1), col(j-1)
        score += abs(ir-xr) + abs(ic-xc)
    return score


def h_2(puz):
    """Returns the number of tiles out of place."""
    n2 = puz.size
    r = 0
    for i in range(n2):
        if puz.state[i] != i+1:
            r += 1
    return r


p = Puzzle(4)
p.shuffle(20)
a_star = AStar(p, Puzzle(4), h_1)

print(p.show())
a, y, b_p = a_star.solve()
print(b_p)

p = Puzzle(4)
p.shuffle(20)
a_star = AStar(p, Puzzle(4), h_2)

print(p.show())
a, y, b_p = a_star.solve()
print(b_p)


