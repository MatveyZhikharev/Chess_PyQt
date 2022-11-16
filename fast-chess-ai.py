import sys

from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from stockfish import Stockfish
from PyQt5 import uic

WHITE = 1
BLACK = 2
SIGNS = {"bR": "♜",
         "bN": "♞",
         "bB": "♝",
         "bK": "♛",
         "bQ": "♚",
         "bP": "♟",
         "wR": "♖",
         "wN": "♘",
         "wB": "♗",
         "wK": "♕",
         "wQ": "♔",
         "wP": "♙"}

MOVES = {"a": 0,
         "b": 1,
         "c": 2,
         "d": 3,
         "e": 4,
         "f": 5,
         "g": 6,
         "h": 7}

IMAGES = {"♜": "images/BlackRook.png",
          "♞": "images/BlackKnight.png",
          "♝": "images/BlackBishop.png",
          "♛": "images/BlackKing.png",
          "♚": "images/BlackQueen.png",
          "♟": "images/BlackPawn.png",
          "♖": "images/WhiteRook.png",
          "♘": "images/WhiteKnight.png",
          "♗": "images/WhiteBishop.png",
          "♕": "images/WhiteKing.png",
          "♔": "images/WhiteQueen.png",
          "♙": "images/WhitePawn.png"}


# Удобная функция для вычисления цвета противника
def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE


def correct_coords(row, col):
    """Функция проверяет, что координаты (row, col) лежат
    внутри доски"""
    return 0 <= row < 8 and 0 <= col < 8


def print_board(board):  # Распечатать доску в текстовом виде (см. скриншот)
    print('     +––––+–––––+––––+–––––+––––+–––––+––––+–––––+')
    for row in range(8):
        print(' ', row, end='  ')
        for col in range(8):
            print('|', board.cell(row, col), end=' ')
            if col != 7:
                print("|", end="")
        print('|')
        print('     +––––+–––––+––––+–––––+––––+–––––+––––+–––––+')
    print(end='  　    ')
    for letter in "ABCDEFGH":
        print(letter, end='　   ')
    print()


def print_image(board):
    im = Image.open("images/desk.png")
    for row in range(8):
        for col in range(8):
            im2 = IMAGES.get(board.cell(row, col), False)
            if im2:
                im2 = Image.open(im2)
                x, y = im2.size
                im2.thumbnail((x // 5 * 3, y // 5 * 3))
                im.paste(im2, (170 + col * 192, row * 190 - 50), mask=im2)
    im.save("images/res.png")


def return_cell(x, y):
    letters = "abcdefgh"
    nums = "12345678"
    print((x - 90) // 86, (y - 120) // 85)
    x, y = (x - 90) // 86, (y - 120) // 85
    if 0 <= x <= 7 and 0 <= y <= 7:
        return letters[x], nums[y]
    return letters[0], nums[0]


class Board:
    def __init__(self):
        self.color = WHITE
        self.field = []
        self.castling_0 = set()
        self.castling_7 = set()
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
            King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
        ]
        self.field[1] = [
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
        ]
        self.field[6] = [
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
        ]
        self.field[7] = [
            Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
            King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
        ]

    def castling0(self):
        if self.color in self.castling_0:
            return False
        if self.color == WHITE:
            for i in range(1, 4):
                if not (self.get_piece(0, i) is None):
                    return False
            if type(self.field[0][0]) != Rook or type(self.field[0][4]) != King:
                return False
            self.field[0][0] = None
            self.field[0][4] = None
            self.field[0][3] = Rook(WHITE)
            self.field[0][2] = King(WHITE)
        else:
            for i in range(1, 4):
                if not (self.get_piece(7, i) is None):
                    return False
            if type(self.field[7][0]) != Rook or type(self.field[7][4]) != King:
                return False
            self.field[7][0] = None
            self.field[7][4] = None
            self.field[7][3] = Rook(BLACK)
            self.field[7][2] = King(BLACK)
        self.color = opponent(self.color)
        return True

    def castling7(self):
        if self.color in self.castling_7:
            return False
        if self.color == WHITE:
            for i in range(5, 7):
                if not (self.get_piece(7, i) is None):
                    return False
            if type(self.field[0][7]) != Rook or type(self.field[0][4]) != King:
                return False
            self.field[0][7] = None
            self.field[0][4] = None
            self.field[0][5] = Rook(WHITE)
            self.field[0][6] = King(WHITE)
        else:
            for i in range(5, 7):
                if not (self.get_piece(7, i) is None):
                    return False
            if type(self.field[7][7]) != Rook or type(self.field[7][4]) != King:
                return False
            self.field[7][7] = None
            self.field[7][4] = None
            self.field[7][5] = Rook(BLACK)
            self.field[7][6] = King(BLACK)
        self.color = opponent(self.color)
        return True

    def current_player_color(self):
        return self.color

    def cell(self, row, col):
        '''Возвращает строку из двух символов. Если в клетке (row, col)
        находится фигура, символы цвета и фигуры. Если клетка пуста,
        то два пробела.'''
        piece = self.field[row][col]
        if piece is None:
            return '　'
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return SIGNS[c + piece.char()]

    def move_piece(self, row, col, row1, col1):
        '''Переместить фигуру из точки (row, col) в точку (row1, col1).
        Если перемещение возможно, метод выполнит его и вернёт True.
        Если нет --- вернёт False'''

        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False  # нельзя пойти в ту же клетку
        piece = self.field[row][col]
        # print(piece.get_color(), self.color)
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        if self.field[row1][col1] is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False
        elif self.field[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row, col, row1, col1):
                return False
        else:
            return False
        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.
        self.color = opponent(self.color)
        return True

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_and_promote_pawn(self, row, col, row1, col1, new_char):
        if new_char not in ('Q', 'R', 'N', 'B'):
            return False
        piece = self.field[row][col]
        if (piece is None) or (piece.char() != 'P'):
            return False
        if piece.get_color() == WHITE and row1 != 7:
            return False
        if piece.get_color() == BLACK and row1 != 0:
            return False
        if self.move_piece(row, col, row1, col1):
            if new_char == 'Q':
                self.field[row1][col1] = Queen(piece.get_color())
            elif new_char == 'R':
                self.field[row1][col1] = Rook(piece.get_color())
            elif new_char == 'N':
                self.field[row1][col1] = Knight(piece.get_color())
            elif new_char == 'B':
                self.field[row1][col1] = Bishop(piece.get_color())
            return True
        return False

    def is_under_attack(self, row, col, color):
        for r in range(8):
            for c in range(8):
                piece = self.field[r][c]
                if piece is None:
                    continue
                if piece.get_color() == color and piece.can_move(row, col):
                    return True
        return False


class Rook:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        # Невозможно сделать ход в клетку,
        # которая не лежит в том же ряду или столбце клеток.
        if row != row1 and col != col1:
            return False

        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            # Если на пути по вертикали есть фигура
            if not (board.get_piece(r, col) is None):
                return False

        step = 1 if (col1 >= col) else -1
        for c in range(col + step, col1, step):
            # Если на пути по горизонтали есть фигура
            if not (board.get_piece(row, c) is None):
                return False
        if col == 0 and self.color not in board.castling_0:
            board.castling_0.add(self.color)
        elif col == 7 and self.color not in board.castling_7:
            board.castling_7.add(self.color)
        return True

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Pawn:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        # Пешка может ходить только по вертикали
        # "взятие на проходе" не реализовано
        if col != col1:
            return False

        # Пешка может сделать из начального положения ход на 2 клетки
        # вперёд, поэтому поместим индекс начального ряда в start_row.
        if self.color == WHITE:
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1

        # ход на 1 клетку
        if row + direction == row1:
            return True

        # ход на 2 клетки из начального положения
        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None):
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'N'  # kNight, буква 'K' уже занята королём

    def can_move(self, board, row, col, row1, col1):
        return (row - 2 == row1 and col - 1 == row1) or (row + 2 == row1 and col + 1 == row1) or \
               (row - 1 == row1 and col - 2 == row1) or (row + 1 == row1 and col + 2 == row1)

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(self, board, row, col, row1, col1)


class King:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'K'

    def get_moves(self, board, x, y):
        moves = []
        y += -1 if self.color == WHITE else 1
        piece = board.get_piece
        if y == -1 or y == 8:
            return moves
        if x > 0 and board.get_color(x - 1, y) == opponent(self.color):
            moves.append([x - 1, y])
        if x < 7 and board.get_piece.color(x + 1, y) == opponent(self.color):
            moves.append([x + 1, y])
        if not board.get_piece(x, y):
            moves.append([x, y])
            if self.color == WHITE and y == 5 and not board.get_piece(x, y - 1):
                moves.append([x, y - 1])
            if self.color == BLACK and y == 2 and not board.get_piece(x, y - 1):
                moves.append([x, y + 1])
        return moves

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) > 1 or abs(col - col1) > 1 or row1 > 8 or col1 > 8:
            return False
        if board.field[row1][col1] is None and correct_coords(row1, col1):
            board.castling_0.add(self.color)
            board.castling_7.add(self.color)
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(self, board, row, col, row1, col1)


class Queen:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1):
        if not correct_coords(row1, col1):
            return False
        piece1 = board.get_piece(row1, col1)
        if not (piece1 is None) and piece1.get_color() == self.color:
            return False
        if row == row1 or col == col1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                if not (board.get_piece(r, col) is None):
                    return False
            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                if not (board.get_piece(row, c) is None):
                    return False
            return True
        if row - col == row1 - col1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                c = col - row + r
                if not (board.get_piece(r, c) is None):
                    return False
            return True
        if row + col == row1 + col1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                c = row + col - r
                if not (board.get_piece(r, c) is None):
                    return False
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(self, board, row, col, row1, col1)


class Bishop:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        return abs(row - row1) == abs(col - col1)

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(self, board, row, col, row1, col1)


class Chess(QMainWindow):
    def __init__(self):
        super(Chess, self).__init__()
        self.stockfish = Stockfish(path="stockfish1\stockfish1.exe")
        uic.loadUi("design.ui", self)
        self.figure_chosed = 0
        self.lab = QLabel(self)
        self.lab.move(10, 33)
        self.lab.resize(150, 25)
        self.setMouseTracking(True)
        self.pixmap = QPixmap("images/desk.png")
        self.desk.setPixmap(self.pixmap)  # 88 121     175 204     87 83    85
        self.board = Board()
        self.field = []
        self.place_figures()

    def game(self):
        while True:
            if self.board.current_player_color() == WHITE:
                print('Ваш ход:')
                command = input()
                cast = 0
                if command == 'exit':
                    break
                elif command == "castling0":
                    cast = self.board.castling0()
                elif command == "castling7":
                    cast = self.board.castling7()
                move_type, rowcol, row1col1 = command.split()
                row, col, row1, col1 = 8 - int(rowcol[1]), MOVES[rowcol[0]], 8 - int(row1col1[1]), MOVES[row1col1[0]]
                if self.board.move_piece(row, col, row1, col1) or cast:
                    print([rowcol + row1col1])
                    self.stockfish.set_position([rowcol + row1col1])
                    print('Ход успешен')
                else:
                    print('Ход некорректен')
            else:
                move = self.stockfish.get_best_move()
                print(move)
                self.stockfish.set_position([move])
                row, col, row1, col1 = 8 - int(move[1]), MOVES[move[0]], 8 - int(move[3]), MOVES[move[2]]
                print(row, col, row1, col1)
                self.board.move_piece(row, col, row1, col1)

    def place_figures(self):
        for i in range(len(self.board.field)):
            row = []
            for j in range(len(self.board.field[i])):
                figure = self.board.field[i][j]
                if figure is not None:
                    pixmap = QPixmap(IMAGES[self.board.cell(i, j)])
                    label = QLabel(self)
                    label.resize(116, 268)
                    label.setPixmap(pixmap)
                    label.move(90 + 86 * j, 85 * i)
                    row.append(label)
                else:
                    row.append(None)
            self.field.append(row)

    def mouseMoveEvent(self, event):
        letter, num = return_cell(event.x(), event.y())
        print(letter, int(num))
        figure = self.field[int(num) - 1][MOVES[letter]]
        if figure:
            figure.move(event.x(), event.y() - 150)
        print(self.field)
        if not self.figure_chosed:
            self.figure_chosed = 1
            figure = self.field[MOVES[letter]][int(num) - 1]
        if self.figure_chosed:
            if figure is not None:
                figure.move(event.x(), event.y())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chess = Chess()
    chess.show()
    sys.exit(app.exec())
