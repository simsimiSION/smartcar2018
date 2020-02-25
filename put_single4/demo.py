import numpy as np

from math import *
import random


class OthelloState:

    def __init__(self, sz=8):
        self.playerJustMoved = 2  # At the root pretend the player just moved is p2 - p1 has the first move
        self.board = []  # 0 = empty, 1 = player 1, 2 = player 2
        self.size = sz
        assert sz == int(sz) and sz % 2 == 0  # size must be integral and even
        for y in range(sz):
            self.board.append([0] * sz)
        self.board[int(sz/2)][int(sz/2)] = self.board[int(sz/2-1)][int(sz/2-1)] = 1
        self.board[int(sz/2)][int(sz/2-1)] = self.board[int(sz/2-1)][int(sz/2)] = 2

    def Clone(self):
        st = OthelloState()
        st.playerJustMoved = self.playerJustMoved
        st.board = [self.board[i][:] for i in range(self.size)]
        st.size = self.size
        return st

    def DoMove(self, move):
        (x, y) = (move[0], move[1])
        assert x == int(x) and y == int(y) and self.IsOnBoard(x, y) and self.board[x][y] == 0
        m = self.GetAllSandwichedCounters(x, y)
        self.playerJustMoved = 3 - self.playerJustMoved
        self.board[x][y] = self.playerJustMoved
        for (a, b) in m:
            self.board[a][b] = self.playerJustMoved

    def GetMoves(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if
                self.board[x][y] == 0 and self.ExistsSandwichedCounter(x, y)]

    def AdjacentToEnemy(self, x, y):
        for (dx, dy) in [(0, +1), (+1, +1), (+1, 0), (+1, -1), (0, -1), (-1, -1), (-1, 0), (-1, +1)]:
            if self.IsOnBoard(x + dx, y + dy) and self.board[x + dx][y + dy] == self.playerJustMoved:
                return True
        return False

    def AdjacentEnemyDirections(self, x, y):
        es = []
        for (dx, dy) in [(0, +1), (+1, +1), (+1, 0), (+1, -1), (0, -1), (-1, -1), (-1, 0), (-1, +1)]:
            if self.IsOnBoard(x + dx, y + dy) and self.board[x + dx][y + dy] == self.playerJustMoved:
                es.append((dx, dy))
        return es

    def ExistsSandwichedCounter(self, x, y):
        for (dx, dy) in self.AdjacentEnemyDirections(x, y):
            if len(self.SandwichedCounters(x, y, dx, dy)) > 0:
                return True
        return False

    def GetAllSandwichedCounters(self, x, y):
        sandwiched = []
        for (dx, dy) in self.AdjacentEnemyDirections(x, y):
            sandwiched.extend(self.SandwichedCounters(x, y, dx, dy))
        return sandwiched

    def SandwichedCounters(self, x, y, dx, dy):
        x += dx
        y += dy
        sandwiched = []
        while self.IsOnBoard(x, y) and self.board[x][y] == self.playerJustMoved:
            sandwiched.append((x, y))
            x += dx
            y += dy
        if self.IsOnBoard(x, y) and self.board[x][y] == 3 - self.playerJustMoved:
            return sandwiched
        else:
            return []  # nothing sandwiched

    def IsOnBoard(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def GetResult(self, playerjm):
        jmcount = len([(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == playerjm])
        notjmcount = len(
            [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 3 - playerjm])
        if jmcount > notjmcount:
            return 1.0
        elif notjmcount > jmcount:
            return 0.0
        else:
            return 0.5  # draw

    def __repr__(self):
        s = ""
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                s += ".XO"[self.board[x][y]]
            s += "\n"
        return s


class Node:
    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves()  # future child nodes
        self.playerJustMoved = state.playerJustMoved  # the only part of the state that the Node needs later

    def UCTSelectChild(self):
        s = sorted(self.childNodes, key=lambda c: c.wins / c.visits + sqrt(2 * log(self.visits) / c.visits))[-1]
        return s

    def AddChild(self, m, s):
        n = Node(move=m, parent=self, state=s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose=False):
    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []:  # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.DoMove(m)
            node = node.AddChild(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []:  # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(
                node.playerJustMoved))  # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose): print (rootnode.TreeToString(0))
    else: print (rootnode.ChildrenToString())

    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def UCTPlayGame():
    state = OthelloState(8) # uncomment to play Othello on a squa

    while (state.GetMoves() != []):
        print (str(state))
        if state.playerJustMoved == 1:
            m = UCT(rootstate=state, itermax=1000, verbose=False)  # play with values for itermax and verbose = True
        else:
            m = UCT(rootstate=state, itermax=100, verbose=False)
        print ("Best Move: " + str(m) + "\n")
        state.DoMove(m)
    if state.GetResult(state.playerJustMoved) == 1.0:
        print ("Player " + str(state.playerJustMoved) + " wins!")
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print ("Player " + str(3 - state.playerJustMoved) + " wins!")
    else:
        print ("Nobody wins!")


if __name__ == "__main__":

    UCTPlayGame()