import random

from typing import List


class Pos:
    """Класс для хранения координат объектов"""
    def __init__(self, y: int, x: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    """Класс отвечающий за создание корабля"""
    def __init__(self, *coords: Pos):
        self.__coords = list(coords)

    @property
    def coords(self) -> list:
        return self.__coords


class Fleet:
    """Класс отвечающий за создание флота"""
    def __init__(self) -> None:
        self.__fleet = []

    # Функция для проверки, можно ли разместить корабль на этой позиции
    def _can_place(self, matrix, coords):
        for pos in coords:
            if matrix[pos.y][pos.x] != 0: # Проверка на свободность клетки
                return False
            for i in range(-1, 2): # Вертикаль
                for j in range(-1, 2): # Горизонталь
                    if 0 <= pos.y + i < 6 and 0 <= pos.x + j < 6:
                        if matrix[pos.y + i][pos.x + j] != 0 and Pos(pos.y + i, pos.x + j) not in coords:
                            return False
        return True

    def _generate_ship(self, matrix, length, max_attempts):
        attempts = 0
        while attempts < max_attempts:
            # Генерируем случайное положение и ориентацию корабля
            pos1 = Pos(random.randint(0, 6 - length), random.randint(0, 6 - length))
            orientation = random.choice(['horizontal', 'vertical'])

            # Создаем корабль на основе сгенерированных данных
            ship_coords = [pos1]
            for i in range(1, length):
                if orientation == 'horizontal':
                    new_pos = Pos(pos1.y, pos1.x + i)
                else:
                    new_pos = Pos(pos1.y + i, pos1.x)
                ship_coords.append(new_pos)

            new_ship = Ship(*ship_coords)

            # Проверяем возможность размещения корабля и размещаем его, если возможно
            if self._can_place(matrix, new_ship.coords):
                for pos in new_ship.coords:
                    matrix[pos.y][pos.x] = '■'
                return new_ship
            else:
                attempts += 1
        return None # Если количество попыток превысило предел, возвращаем None

    def generate_fleet(self):
        matrix = Board.matrix()
        max_attempts = 100  # Максимальное количество попыток размещения корабля

        # Размещение корабля длинной в 3 клетки
        large_ship = self._generate_ship(matrix, 3, max_attempts)
        if large_ship:
            self.__fleet.append(large_ship)
        else:
            self.__fleet = []
            self.generate_fleet() # Если не удалось разместить корабль, начинаем сначала

        # Размещение кораблей длинной в 2 клетки
        for i in range(2):
            medium_ship = self._generate_ship(matrix, 2, max_attempts)
            if medium_ship:
                self.__fleet.append(medium_ship)
            else:
                self.__fleet = []
                self.generate_fleet() # Если не удалось разместить корабль, начинаем сначала

        # Размещение кораблей размером с 1 клетку
        for i in range(4):
            small_ship = self._generate_ship(matrix, 1, max_attempts)
            if small_ship:
                self.__fleet.append(small_ship)
            else:
                self.__fleet = []
                self.generate_fleet() # Если не удалось разместить корабль, начинаем сначала

    @property
    def fleet(self):
        return self.__fleet


class Board:
    """Класс игрового поля"""
    def __init__(self, fleet: List[Ship]) -> None:
        # Создаем матрицу 6x6
        self.__matrix = self.matrix()
        self._place_fleet(fleet)

    # Внутренняя функция для размещения кораблей на поле
    def _place_fleet(self, fleet: List[Ship]) -> None:
        if fleet:
            for ship in fleet:
                for pos in ship.coords:
                    self.__matrix[pos.y][pos.x] = '■'

    # Служебный метод для генерации матрицы
    @staticmethod
    def matrix():
        return [[0 for x in range(6)] for y in range(6)]

    @property
    def board(self):
        return self.__matrix


class Player:
    """Класс игрока"""
    def __init__(self):
        self.fleet = Fleet()
        self.fleet.generate_fleet()
        self.fleet = self.fleet.fleet
        self.board = Board(self.fleet).board

    @classmethod
    def create_target_board(cls):       # Пустая доска для целей игрока
        cls.target_board = Board(False).board


# Класс для компьютера
class Ai(Player):
    """Класс компьютера"""
    def __init__(self):
        super().__init__()
        
    def generate_move(self):
        return GameEvent(GameEvent.Event_Hit, Pos(random.randint(0, 5), random.randint(0, 5)), Ai)


class HitError(Exception):
    """Вызывается тогда, когда задана неверная цель"""
    def __str__(self):
        return 'Неверно введены координаты'


class GameExit(Exception):
    """Вызывается тогда, когда происходит выход из игры"""
    def __str__(self):
        return 'Выход из игры'


class GameEvent:
    """Класс ответственный за передачу сообщений между логикой и интерфейсом"""
    # Пустое событие
    Event_None = 0
    # Событие "выстрела" по цели
    Event_Hit = 1
    # Событие выхода из игры
    Event_Exit = 2

    def __init__(self, type, data, caller):
        self.type = type
        self.data = data
        self.caller = caller


class GameLogic:
    """Клас ответственный за логику игры"""
    def __init__(self):
        # Инициализировать игру
        self.initialize_logic()

    # Метод обработки сообщений которые приходят к игровой логике
    def process_event(self, event):
        # Если сообщение "выстрел", то обрабатываем это событие
        if event.type == GameEvent.Event_Hit:
            # Если выстрел от игрока, обрабатываем от игрока
            if event.caller == Player:
                if self.ai.board[event.data.y][event.data.x] == '■':
                    for ship in self.ai.fleet:
                        for pos in ship.coords:
                            if event.data == pos:
                                ship.coords.remove(pos)
                                break
                        if not ship.coords:
                            self.ai.fleet.remove(ship)
                    self.ai.board[event.data.y][event.data.x] = 'X'
                    self.player.target_board[event.data.y][event.data.x] = 'X'
                elif self.ai.board[event.data.y][event.data.x] == 0:
                    self.ai.board[event.data.y][event.data.x] = 'T'
                    self.player.target_board[event.data.y][event.data.x] = 'T'
                else:
                    raise HitError
            # Если выстрел от компьютера, обрабатываем от компьютера
            elif event.caller == Ai:
                if self.player.board[event.data.y][event.data.x] == '■':
                    for ship in self.player.fleet:
                        for pos in ship.coords:
                            if event.data == pos:
                                ship.coords.remove(pos)
                                break
                        if not ship.coords:
                            self.player.fleet.remove(ship)
                    self.player.board[event.data.y][event.data.x] = 'X'
                elif self.player.board[event.data.y][event.data.x] == 0:
                    self.player.board[event.data.y][event.data.x] = 'T'
                else:
                    raise HitError
        # Если событие "Выход", то вызвать исключение выхода
        if event.type == GameEvent.Event_Exit:
            raise GameExit

    def initialize_logic(self):
        # Создание игроков
        self.player = Player()
        self.player.create_target_board()
        self.ai = Ai()


class ConsoleGameGui:
    """Класс отвечающий за запуск игры и вывод в консоль"""
    def __init__(self, game_logic):
        self._logic = game_logic
        self.show_ai_board = False

    def run(self):
        print('-' * 15, 'Морской бой', '-' * 15, '\n\n',
              'Правила ввода:\n', '\t\tПервая координата по горизонтали\n', '\t\tВторая координата по вертикали\n',
              '\t\tКоманда "stop" - Выход из игры\n\n',
              '-' * 42, '\n')
        # Начало игры
        self._start()

        while True:
            choice = input('\nХотите сыграть ещё раз?').lower()
            if choice == 'да':
                self._logic.initialize_logic()
                self._start()
            else:
                break

    # Старт игры
    def _start(self):
        while True:
            self._draw()

            try:
                event = self._player_event()
                self._logic.process_event(event)
                # Проверка на выигрыш игрока
                if not self._logic.ai.fleet:
                    print('\n', '-' * 23, 'Победа игрока!', '-' * 23, '\n')
                    self._draw()
                    break
                event = self._logic.ai.generate_move()
                while True:
                    try:
                        self._logic.process_event(event)
                    except HitError:
                        event = self._logic.ai.generate_move()
                    else:
                        break
                # Проверка на выигрыш компьютера
                if not self._logic.player.fleet:
                    print('\n', '-' * 23, 'Победа компьютера!', '-' * 23, '\n')
                    self._draw()
                    break
            # Вывести сообщение о неверных координатах
            except HitError as e:
                print('\n', e, '\n')
            # Прервать цикл игры
            except GameExit as e:
                print('\n', e, '\n')
                break
            except Exception as e:
                print(f'\nОшибка: {e}\n')

    # Внутренний метод для вывода полей на экран
    def _draw(self) -> None:
        p = ['|', 1, '|', 2, '|', 3, '|', 4, '|', 5, '|', 6, '|']
        print(' ', *p, '\t', '\t', *p, sep=' ')
        for i in range(len(self._logic.player.board)):
            print(i+1, *self._logic.player.board[i], '\t', i+1,
                  *self._logic.player.target_board[i], sep=' | ', end=' |\n')

    # Внутренний метод для запроса команд от игрока
    def _player_event(self) -> GameEvent:
        players_move = input('Ваш ход: ').split()
        if 'stop' in players_move:
            event = GameEvent(GameEvent.Event_Exit, None, Player)
        else:
            players_move = Pos(int(players_move[1]) - 1, int(players_move[0]) - 1)
            event = GameEvent(GameEvent.Event_Hit, players_move, Player)
        return event


if __name__ == '__main__':
    logic = GameLogic()
    gui = ConsoleGameGui(logic)
    gui.run()
