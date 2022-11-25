import sys

from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QHeaderView, QTableWidgetItem, QFileDialog, QInputDialog
from stockfish import Stockfish
from PyQt5 import uic
import csv

NAME = "Вы"
DIRECTORY = ""

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

NUMTOLET = "ABCDEFGH"


# Удобная функция для вычисления цвета противника
def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE


def correct_coords(row, col):  # Функция проверяет, что координаты (row, col) лежат внутри доски
    return 0 <= row < 8 and 0 <= col < 8


def print_board(board):  # Распечатать доску в текстовом виде (для отладки)
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


def save_image(board, track):  # сохранение доски картинкой
    im = Image.open("images/desk.png")
    for row in range(8):
        for col in range(8):
            im2 = IMAGES.get(board.cell(row, col), False)
            if im2:
                im2 = Image.open(im2)
                x, y = im2.size
                im2.thumbnail((x, y))
                im.paste(im2, (71 + 86 * col, 85 * row - 50), mask=im2)
    im.save(track)


def return_cell(x, y):  # функция, возвращающая номер клетки в формате (буква, цифра)
    letters = "abcdefgh"
    nums = "12345678"
    x, y = (x - 90) // 86, (y - 120) // 85
    if 0 <= x <= 7 and 0 <= y <= 7:
        return letters[x], nums[y]
    return letters[0], nums[0]


def return_cell_num(x, y):  # функция, возвращающая номер клетки в формате (цифра, цифра)
    x, y = (x - 90) // 86, (y - 120) // 85
    if 0 <= x <= 7 and 0 <= y <= 7:
        return x, y
    return None


class Board:  # логический класс игры
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
        if piece is None:
            return False
        if self.king_is_under_attack(WHITE, row, col, row1, col1) and piece.get_color() == WHITE:
            return False
        if piece.get_color() != self.color:
            return False
        if self.field[row1][col1] is None:
            if not piece.can_move(self, row, col, row1, col1):
                if piece.get_color() == BLACK:
                    return self.castling_0() if col == 3 else self.castling_7
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

    def king_is_under_attack(self, color, row, col, row1, col1):
        for r in range(8):
            for c in range(8):
                if type(self.field[r][c]) == King:
                    piece = self.field[row2 := r][col2 := c]
                    if type(self.field[row][col]) == King:
                        if self.is_under_attack(row1, col1, opponent(color)):
                            return True
                        return False
                    if self.is_under_attack(row2, col2, opponent(piece.get_color())):
                        return piece.get_color() == color

    def is_under_attack(self, row, col, color):
        for r in range(8):
            for c in range(8):
                piece = self.field[r][c]
                if piece is None:
                    continue
                if piece.get_color() == color and piece.can_move(self, r, c, row, col):
                    return True
        return False


class Rook:  # класс фигуры - ладья
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


class Pawn:  # класс фигуры - пешка#
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        # Пешка может ходить только по вертикали
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
        direction = -1 if (self.color == WHITE) else 1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight:  # класс фигуры - конь
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'N'  # kNight, буква 'K' уже занята королём

    def can_move(self, board, row, col, row1, col1):
        delta_row = abs(row1 - row)
        delta_col = abs(col1 - col)
        return max(delta_col, delta_row) == 2 and min(delta_col, delta_row) == 1

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class King:  # класс фигуры - Король
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
        if correct_coords(row1, col1):
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Queen:  # класс фигуры - Ферзь
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
        print(self.can_move(board, row, col, row1, col1))
        return self.can_move(board, row, col, row1, col1)


class Bishop:  # класс фигуры - слон
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        return abs(row - row1) == abs(col - col1)

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Chess(QMainWindow):  # класс интерсфейса игры
    def __init__(self):
        super(Chess, self).__init__()
        self.stockfish = Stockfish(path="stockfish_15_win_x64_avx2\stockfish_15_x64_avx2.exe")  # шахматный ИИ
        uic.loadUi("design.ui", self)
        self.setWindowTitle("Шахматы PyQt с ИИ")
        self.figure_chosed = 0
        self.figure = 0
        self.lab = QLabel(self)
        self.lab.move(10, 33)
        self.lab.resize(150, 25)
        self.pixmap = QPixmap("images/desk.png")
        self.desk.setPixmap(self.pixmap)
        self.board = Board()
        self.field = []
        self.place_figures()
        self.steps = []
        for elem in (self.level, self.take_hint, self.save):  # стили CSS к кнопкам
            elem.setStyleSheet("""background-color: 'white';
                                    border-radius: 15px; 
                                    outline: 2px solid #CCC;
                                    """)
        with open("steps.csv", "w", encoding="utf8") as csv_file:  # создание файла с ходами
            writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(title := ["Игрок", "Откуда", "Куда"])
            self.steps_table.setColumnCount(len(title))
            self.steps_table.setHorizontalHeaderLabels(title)
            self.steps_table.setRowCount(0)
            self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.steps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.take_hint.clicked.connect(self.hint)  # подключение всех кнопок на экране
        self.save.clicked.connect(self.save_file)
        self.save_file_1.triggered.connect(self.save_file)
        self.save_photo.triggered.connect(self.save_photo_)
        self.correct_name.triggered.connect(self.cor_name)
        self.direct.triggered.connect(self.cor_dir)
        self.chose_level.triggered.connect(self.cor_level)
        self.level.clicked.connect(self.cor_level)

    def cor_level(self):  # выбор уровня сложности
        try:
            num, ok_pressed = QInputDialog.getText(self, "Введите число",
                                                   "Введите число от 1 до 25")
            if ok_pressed:
                self.stockfish.set_skill_level(int(num))
        except Exception as e:
            print(e)

    def cor_dir(self):  # сохранение папки по умолчанию
        global DIRECTORY
        try:
            fname = QFileDialog.getExistingDirectory(self, 'Выбрать папку', f'{DIRECTORY}')
            DIRECTORY = fname[0]
        except Exception as e:
            print(e)

    def cor_name(self):  # изменение имени
        global NAME
        name, ok_pressed = QInputDialog.getText(self, "Введите имя",
                                                "Как к вам обращаться?")
        if ok_pressed:
            NAME = name

    def save_photo_(self):  # сохранение поля, как картинки
        try:
            fname = QFileDialog.getSaveFileName(self, 'Создать картинку', f'{DIRECTORY}\\res', 'Картинка (*.png);;'
                                                                                               'Картинка (*.jpeg);;'
                                                                                               'Картинка (*.jpg);;'
                                                                                               'Все файлы (*)')
            save_image(self.board, fname[0])
        except Exception as e:
            print(e)

    def hint(self):  # подсказка
        self.condition.setText(self.stockfish.get_best_move())

    def save_file(self):  # сохранение ходов в файл
        try:
            fname = QFileDialog.getSaveFileName(self, 'Создать файл', f'{DIRECTORY}\\file',
                                                'Таблица (*.csv);;Все файлы (*)')
            with open("steps.csv", "r", encoding="utf-8") as csv_input:
                with open(fname[0], "w", encoding="utf-8") as csv_output:
                    for line in csv_input:
                        csv_output.write(line)
        except Exception as e:
            print(e)

    def steps_checker(self, step, ai):  # заполнитель поля и файла с ходами
        with open("steps.csv", encoding="utf8") as csv_file:
            reader = csv.reader(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            rows = list(reader)
            with open("steps.csv", "w", encoding="utf8") as csv_file:
                writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                rows.append([("Компьютер" if ai else NAME), step[:2], step[2:]])
                rows = [row for row in rows if row]
                for i, row in enumerate(rows[1:]):
                    self.steps_table.setRowCount(
                        len(rows[1:]) + 1)
                    for j, elem in enumerate(row):
                        self.steps_table.setItem(
                            i, j, QTableWidgetItem(elem))
                self.steps_table.resizeColumnToContents(0)
                writer.writerows(rows)

    def place_figures(self):  # помещение фигур на экран и заполнение списка фигур
        self.field = []
        print_board(self.board)
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

    def replace_figures(self):  # удаление несуществующих фигур с экрана, добавление перемещённых на экран
        print_board(self.board)
        for i in range(len(self.board.field)):
            for j in range(len(self.board.field[i])):
                figure = self.board.field[i][j]
                if figure is not None:
                    label = self.field[i][j]
                    if not label:
                        pixmap = QPixmap(IMAGES[self.board.cell(i, j)])
                        label = QLabel(self)
                        label.resize(116, 268)
                        label.setPixmap(pixmap)
                        self.field[i][j] = label
                        label = self.field[i][j]
                    label.move(90 + 86 * j, 85 * i)
                    label.raise_()
                elif self.field[i][j] is not None:
                    self.field[i][j].hide()
                    self.field[i][j] = None

    def move_piece(self, row, col, row1, col1):  # перемещение фигур по доске
        figure = self.field[row][col]
        self.steps.append("".join((NUMTOLET[col], str(8 - row), NUMTOLET[col1], str(8 - row1))).lower())
        self.steps_checker("".join((NUMTOLET[col], str(8 - row), NUMTOLET[col1], str(8 - row1))).lower(), 0)
        self.stockfish.set_position([*self.steps])
        self.field[row][col] = None
        if self.field[row1][col1]:
            self.field[row1][col1].hide()
        self.field[row1][col1] = figure
        if self.board.king_is_under_attack(WHITE, row, col, row1, col1):
            self.condition.setText("Вам шах!")

        self.steps.append(move := self.stockfish.get_best_move())
        self.stockfish.set_position([*self.steps])

        col, row, col1, row1 = list(move)
        row, col, row1, col1 = int(row) - 1, MOVES[col], int(row1) - 1, MOVES[col1]
        self.steps_checker(move, 1)
        figure = self.field[7 - row][col]
        if self.field[7 - row1][col1]:
            self.field[7 - row1][col1].hide()
        self.field[7 - row1][col1] = figure
        self.field[7 - row][col] = None
        self.board.move_piece(7 - row, col, 7 - row1, col1)
        if self.board.king_is_under_attack(BLACK, row, col, row1, col1):
            self.condition.setText("Шах!")

    def mouseReleaseEvent(self, event):  # выбор клетки, где остановился курсор
        try:
            if self.board.move_piece(*self.figure_chosed[::-1], *self.coords):
                self.move_piece(*self.figure_chosed[::-1], *self.coords)
                self.condition.setText("Ход успешен")
            self.replace_figures()
            self.figure_chosed, self.figure = None, None
        except Exception as e:
            print(e)
            self.replace_figures()
            self.figure_chosed, self.figure = None, None

    def mouseMoveEvent(self, event):  # функция handler (обработчик действий)
        if return_cell_num(event.x(), event.y()):
            letter, num = return_cell_num(event.x(), event.y())
            if not self.figure_chosed:
                self.figure_chosed = (letter, num)
                self.figure = self.field[num][letter]
            if self.figure:
                self.figure.move(86 * (event.x() // 86) + 90, event.y() - 150)
            if self.figure_chosed and self.figure is not None:
                self.figure.move(event.x(), event.y())
                self.coords = return_cell_num(event.x(), event.y())[::-1]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chess = Chess()
    chess.show()
    sys.exit(app.exec())
