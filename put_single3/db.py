import sqlite3


def dec2bin(num):
    """十进制数字转化成二进制数字
    """
    assert num >= 0 and num <= 255

    l = []
    for i in range(8):
        num, remainder = divmod(num, 2)
        l.append(int(remainder))

    return l

def bin2dec(num_list):
    """二进制数字列表转化成十进制数字
    """
    assert len(num_list) == 8

    result = 0
    for i in range(8):
        result += num_list[i] * (2**(7-i))

    return result


"""创建数据库
"""
def createDb(c, conn):

    c.execute('''CREATE TABLE CHESS
                (ID INT PRIMARY KEY  NOT NULL,
                  BOARD_1 INT NOT NULL,
                  BOARD_2 INT NOT NULL,
                  BOARD_3 INT NOT NULL,
                  BOARD_4 INT NOT NULL,
                  BOARD_5 INT NOT NULL,
                  BOARD_6 INT NOT NULL,
                  BOARD_7 INT NOT NULL,
                  BOARD_8 INT NOT NULL,
                  HEAD    INT         ,
                  TAIL    INT         ,
                  OWNER   INT NOT NULL,
                  X_POS   INT NOT NULL,
                  Y_POS   INT NOT NULL)''')

    conn.commit()


"""将相关文件插入数据库
"""
def insertDB(c, conn, id, board, owner, x, y, head=None, tail=None, ):
    dec_board = []

    for subboard in board:
        dec_board.append(bin2dec(subboard))

    c.execute("INSERT INTO CHESS(ID,BOARD_1,BOARD_2,BOARD_3,BOARD_4,BOARD_5,BOARD_6,BOARD_7,BOARD_8,HEAD,TAIL,OWNER,X_POS,Y_POS) \
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (id,dec_board[0],dec_board[1],dec_board[2],dec_board[3],dec_board[4],dec_board[5],dec_board[6],dec_board[7],head,tail,owner,x,y))

    conn.commit()


"""从数据库中选择基于id的相关文件
"""
def selectDB(c, id):
    db_file = {}

    cursor = c.execute("SELECT * from CHESS where ID=? ",(id,))

    content = cursor.fetchall()[0]

    board = []
    for i in range(8):
        board.append(dec2bin(content[i + 1]))

    db_file['id'] = content[0]
    db_file['board'] = board
    db_file['head'] = content[9]
    db_file['tail'] = content[10]
    db_file['owner'] = content[11]

    pos = []
    pos.append(content[12])
    pos.append(content[13])
    db_file['pos'] = pos

    return db_file

"""从数据库中删除基于id的相关文件
"""
def delectDB(c, conn, id):
    c.execute("DELETE from CHESS where ID=? ", (id,))

    conn.commit()

"""获得整个数据库的内容
"""
def getDB(c):
    DB_file = []

    cursor = c.execute("SELECT * from CHESS")
    content = cursor.fetchall()

    for row in content:
        DB_subfile = {}

        board = []
        for i in range(8):
            board.append(dec2bin(row[i+1]))

        DB_subfile['id'] = row[0]
        DB_subfile['board'] = board
        DB_subfile['head'] = row[9]
        DB_subfile['tail'] = row[10]
        DB_subfile['owner'] = row[11]
        DB_subfile['pos'] = tuple(row[12],row[13])

        DB_file.append(DB_subfile)


    return DB_file


##=====================================================
##       test
##=====================================================
# array = []
# for i in range(8):
#     subarray = []
#     for j in range(8):
#         subarray.append(j)
#     array.append(subarray)
#
#
# conn = sqlite3.connect('chess.db')
# c = conn.cursor()
#
# createDb(c, conn)
# insertDB(c, conn, 0, array, 0, 0, 0)
# delectDB(c, conn, 0)
# print(getDB(c))
#
# conn.close()