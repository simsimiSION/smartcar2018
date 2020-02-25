import numpy as np


class Quoridor:
    player1_blockCount = 0
    player2_blockCount = 0

    def __init__(self, sz):
        assert sz == int(sz) and sz % 2 == 0

        self.POS_NONE = 0
        self.POS_PLAYER_1 = 1
        self.POS_PLAYER_2 = 2
        self.POS_BLOCK = -1

        self.MOVE_CHESS = 0
        self.MOVE_BLOCK = 1

        self.playerMoved = 2
        self.board = []  # 0 empty ,1 player1 , 2 player2, -1 block
        self.size = sz
        self.block_limit = sz

        #init board
        for i in range(sz):
            self.board.append([0] * sz)
        self.board[0][int(sz/2)] = self.POS_PLAYER_1
        self.board[sz-1][int(sz/2)] = self.POS_PLAYER_2

    """clone the whole chess
    """
    def Clone(self):
        st = Quoridor()
        st.playerMoved = self.playerMoved
        st.board = [self.board[i][:] for i in range(self.size)]
        st.size = self.size
        return st

    """move the chess
    """
    def DoMove(self, move):
        x, y = move[1], move[2]

        if move[0] == -1:   #bolck
            self.board[x][y] = self.POS_BLOCK
            player1_blockCount += 1
        elif move[0] == -2: #block
            self.board[x][y] = self.POS_BLOCK
            player2_blockCount += 1
        elif move[0] == 1: #player1
            self.board[x][y] = self.POS_PLAYER_1
        elif move[0] == 2: #player1
            self.board[x][y] = self.POS_PLAYER_2

        self.playerMoved = 3 - self.playerMoved


    """get the position to place chess
    """
    def GetMove(self, index=[4,2,2,1]):
        #get itself position
        x, y = self.GetPostion(self.playerMoved)

        array = []
        if self.playerMoved == self.POS_PLAYER_1:
            if self.IsOnBoard(x,y-1) and self.board[x][y-1] == self.POS_NONE:
                for i in range(index[3]):array.append([1,x,y-1])
            if self.IsOnBoard(x,y+1) and self.board[x][y+1] == self.POS_NONE:
                for i in range(index[0]):array.append([1,x,y+1])
            if self.IsOnBoard(x-1,y) and self.board[x-1][y] == self.POS_NONE:
                for i in range(index[1]):array.append([1,x-1,y])
            if self.IsOnBoard(x+1,y) and self.board[x+1][y] == self.POS_NONE:
                for i in range(index[2]):array.append([1,x+1,y-1])
        else:
            if self.IsOnBoard(x,y-1) and self.board[x][y-1] == self.POS_NONE:
                for i in range(index[0]):array.append([2,x,y-1])
            if self.IsOnBoard(x,y+1) and self.board[x][y+1] == self.POS_NONE:
                for i in range(index[3]):array.append([2,x,y+1])
            if self.IsOnBoard(x-1,y) and self.board[x-1][y] == self.POS_NONE:
                for i in range(index[1]):array.append([2,x-1,y])
            if self.IsOnBoard(x+1,y) and self.board[x+1][y] == self.POS_NONE:
                for i in range(index[2]):array.append([2,x+1,y-1])

        return array

    """get the position to place block
    """
    def GetBlock(self, limit=int(self.size/2)):
        #get other position
        x, y = self.GetPostion(self.playerMoved,2)

        bolck_list = []

        if self.playerMoved == self.POS_PLAYER_2:
            for i in range(int(limit/2)):
                for j in range(limit):
                    if self.IsOnBoard(x+i, y+i-int(limit/2)) == 1 and \
                            self.IsGetOver(player) == True and \
                            self.board[x+i][y+i-int(limit/2)] == self.POS_NONE:
                        bolck_list.append([-2, x+i, y+i-int(limit/2)])

        else:
            for i in range(int(limit / 2)):
                for j in range(limit):
                    if self.IsOnBoard(x-i, y+i-int(limit/2)) == 1 and \
                            self.IsGetOver(player) == True and \
                            self.board[x-i][y+i-int(limit/2)] == self.POS_NONE:
                        bolck_list.append([-1,x-i,y+i-int(limit/2)])

        return bolck_list

    """detect the person whether it can win
    """
    def IsGetOver(self):
        x, y = self.GetPostion(self.playerMoved)
        book = np.zeros((self.size, self.size), dtype=np.int)

        def dfs(x, y, step, finish_condition):
            next_step = np.array([[0,1], [1,0], [0,-1], [0,1]])

            if x == finish_condition:
                return True
            for i in range(4):
                tx = x + next_step[i][0]
                ty = y + next_step[i][1]
                if self.IsOnBoard(tx, ty):
                    continue
                if self.board[tx][ty] == self.POS_NONE and book[tx][ty] == 0:
                    book[tx][ty] = 1
                    dfs(tx, ty, step+1)
                    book[tx][ty] = 0
            return False

        if self.playerMoved == self.POS_PLAYER_1:
            condition = self.size-1
        else:
            condition = 0

        return dfs(x, y, 0, condition)

    """get the queen position
    """
    def GetPostion(self, status=1):
        if status == 1:
            for i in range(self.size):
                for j in range(self.size):
                    if self.playerMoved == self.POS_PLAYER_1:
                        if self.board[i][j] == self.POS_PLAYER_1:
                            x, y = i, j
                    if self.playerMoved == self.POS_PLAYER_2:
                        if self.board[i][j] == self.POS_PLAYER_2:
                            x, y = i, j
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if self.playerMoved == self.POS_PLAYER_1:
                        if self.board[i][j] == self.POS_PLAYER_2:
                            x, y = i, j
                    if self.playerMoved == self.POS_PLAYER_2:
                        if self.board[i][j] == self.POS_PLAYER_1:
                            x, y = i, j
        return x,y

    """detect the chess is condition?
    """
    def IsOnBoard(self, x, y):
        return x>=0 and x<self.size and y>=0 and y<self.size

    """detect who is win
    """
    def GetResult(self):
        for i in range(self.size):
            if self.board[0][i] == self.POS_PLAYER_2:
                return 2
            if self.board[self.size-1][i] == self.POS_PLAYER_1:
                return 1
        return 0





class Node:
    def __init__(self, move=None, parent=None, state=None):
        self.move = move
        self.parentNode = parent
        self.childNodes = []
        self.wins = 0
        self.visits = 0

        self.untriedMoves = []
        self.chessUntriedMoves = state.GetMove()
        self.untriedMoves.extend(self.chessUntriedMoves)
        self.blockUntriedMoves = state.GetBlock()
        self.untriedMoves.extend(self.blockUntriedMOves)

        self.playerJustMoved = state.playerJustMoved

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
        state = rootnode.clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []:
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []:
            m = random.choice(node.untriedMoves)
            state.DoMove(m)
            node = node.AddChild(m, state)

        # Rollout
        while state.GetMoves() != []:
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None:
            node.Update( state.GetResult(node.playerMoved))
            node = node.parentNode








        