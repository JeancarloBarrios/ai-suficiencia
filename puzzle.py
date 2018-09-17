import random
import heapq
import math

class AStar(object):
    def __init__(self, start, finish, heuristic):
        self.start = start
        self.finish = finish
        self.heuristic = heuristic
        self.heap = []
        self.link = {}
        self.h = {}
        self.g = {}

    def build_path(self, start, finish, parent):
        x = finish
        xs = [x]
        while x != start:
            x = parent[x]
            xs.append(x)
        xs.reverse()
        return xs

    def solve(self):
        self.g[self.start] = 0
        self.h[self.start] = 0
        self.link[self.start] = None
        heapq.heappush(self.heap, (0, 0, self.start))
        for iteration in range(99999999):
            f, junk, current = heapq.heappop(self.heap)
            if current == self.finish:
                print("distance:", self.g[current], "steps:", iteration)
                return self.g[current], iteration, self.build_path(self.start, self.finish, self.link)

            moves = current.get_moves()
            distance = self.g[current]
            for mv in moves:
                if mv not in self.g or self.g[mv] > distance + 1:
                    self.g[mv] = distance + 1
                    if mv not in self.h:
                        self.h[mv] = self.heuristic(mv)
                    self.link[mv] = current
                    heapq.heappush(self.heap, (self.g[mv] + self.h[mv], -iteration, mv))
        else:
            raise Exception("No Solution ERROR")


class Puzzle(object):
    __slots__ = ('n', 'state', 'goal_state', 'size', 'current', 'hash', 'last_move')

    def __init__(self, n, state=None):
        self.n = n
        self.size = n * n
        goal_state = [(x + 1) % self.size for x in range(self.size)]
        if state is None:
            self.state = goal_state
        else:
            self.state = list(state)
        self.hash = None
        self.last_move = []

    def __repr__(self):
        return "(%d, %s)" % (self.n, self.state)

    def show(self):
        ys = ["%2d" % x for x in self.state]
        xs = [" ".join(ys[kk:kk+self.n]) for kk in range(0, self.size, self.n)]
        return "\n".join(xs)

    def __hash__(self):
        if self.hash is None:
            self.hash = hash(tuple(self.state))
        return self.hash

    def __eq__(self, other):
        return self.state == other.state

    def __lt__(self, other):
        return self.state < other.state

    def copy(self):
        return Puzzle(self.n, self.state)

    def shuffle(self, n):
        n_state = self
        for kk in range(n):
            xs = list(n_state.get_moves())
            n_state = random.choice(xs)
        self.state = n_state.state


    def get_moves(self):
        tile0 = self.state.index(0)

        def swap(i):
            j = tile0
            tmp = list(self.state)
            last_move = tmp[i]
            tmp[i], tmp[j] = tmp[j], tmp[i]
            result = Puzzle(self.n, tmp)
            result.last_move = last_move
            return result

        if tile0 - self.n >= 0:
            yield swap(tile0-self.n)
        if tile0 +self.n < self.size:
            yield swap(tile0+self.n)
        if tile0 % self.n > 0:
            yield swap(tile0-1)
        if tile0 % self.n < self.n-1:
            yield swap(tile0+1)

