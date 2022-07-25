from random import randint

'''Внутренняя логика игры'''


# 1) классы исключений:
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


# 2) класс Dot — класс точек на поле. Каждая точка описывается параметрами:
# Координата по оси x .
# Координата по оси y
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


# 3) корабль на игровом поле
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    # метод dots,который возвращает список всех точек корабля.
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    # проверка на попадание
    def shooten(self, shot):
        return shot in self.dots


# 4) Игровое поле
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    # Вывод корабля на доску
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        # Замена символов корабля на пустое значение
        if self.hid:
            res = res.replace("■", "O")
        return res

    # Проверка не выходит ли точка за пределы доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Метод contour, который обводит корабль по контуру.
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    # Метод add_ship, который ставит корабль на доску (если ставить не получается, выбрасываем исключения).
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Метод shot, который делает выстрел по доске (если есть попытка выстрелить за пределы и в использованную точку, нужно выбрасывать исключения).
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Уничтожен ;) !")
                    return False
                else:
                    print("Ранен!")
                    return True

        self.field[d.x][d.y] = "•"
        print("Промах ) ! ")
        return False

    def begin(self):
        self.busy = []


'''Внешняя логика игры'''
# 1) класс Player — класс игрока в игру (и AI, и пользователь).
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# Игрок компьютер
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# Игрок пользователь
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# 2) наш главный класс — класс Game. Генерация досок
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # random_board — метод генерирует случайную доску.
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    # greet — метод, который в консоли приветствует пользователя и рассказывает о формате ввода.
    def greet(self):
        print("  Добро пожаловать в игру !Морской бой!  ")
        print(" Ввод осуществляется по осям: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    # loop — метод с самим игровым циклом.
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Вы победили!")
                break

            if self.us.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Компьютер победил!")
                break
            num += 1

    # start — запуск игры. Сначала вызываем greet, а потом loop.
    def start(self):
        self.greet()
        self.loop()


# ЗАПУСК ИГРЫ
g = Game()
g.start()

