def start_game():
    # Начало игры
    print('Формат ввода:')
    print('Первая цифра по горизонтали, вторая, через пробел, по вертикали')
    print('Чтобы преждевременно завершить игру введите "stop"')
    start()

    # Продолжение игры
    while True:
        choice = input('Хотите продолжить? (y/n)')
        if choice == 'y':
            start()
        else:
            break


def start():
    game_active = True
    # Матрица для вывода в консоль
    game_area = [
        [' ', 0, 1, 2],
        ['-', '-', '-'],
        ['-', '-', '-'],
        ['-', '-', '-']
    ]
    # Главный цикл который будет работать пока истинно условие продолжения игры
    while game_active:
        break_flag = False
        for player in range(1, 3):
            # Выстраивание поля игры
            show_game_area(game_area)

            # Ход игрока записывается в специальную переменную и разбивается  на список индексов
            players_move = input(f'Ход игрока {player}: ').split()
            if 'stop' in players_move:
                break_flag = True
                break
            players_move = [int(i) for i in players_move]

            # По индексам происходит замена на игровом поле прочерка на крестик либо нолик
            game_area = place_x_or_o(game_area, player, players_move)

            # Проверка выигрыша
            game_active = checking_the_winner(game_active, game_area, player)
            if not game_active:
                show_game_area(game_area)
                break_flag = True
                break
        if break_flag:
            break


# Функция проверки выигрыша
def checking_the_winner(game_active, game_area, player):
    vertical_list = [[], [], []]
    temp_copy = game_area.copy()
    del temp_copy[0]
    # Создание копии матрицы повёрнутой на 90 градусов
    for i in range(len(temp_copy)):
        vertical_list[0].append(temp_copy[-(i + 1)][0])
        vertical_list[1].append(temp_copy[-(i + 1)][1])
        vertical_list[2].append(temp_copy[-(i + 1)][2])

    # Проверка по горизонтали
    for i in temp_copy:
        if len(set(i)) == 1 and ('x' in i or 'o' in i):
            return end_the_game(player)

    # Проверка по вертикали
    for i in vertical_list:
        if len(set(i)) == 1 and ('x' in i or 'o' in i):
            return end_the_game(player)

    # Проверка по диагонали

    # Проверка слева на право
    # Проверка на наличие крестика
    if all(check_from_left_to_right(temp_copy, 'x')):
        return end_the_game(player)
    # Проверка на наличие нолика
    else:
        if all(check_from_left_to_right(temp_copy, 'o')):
            return end_the_game(player)

    # Проверка справа на лево
    # Проверка на наличие крестика
    if all(check_from_right_to_left(temp_copy, 'x')):
        return end_the_game(player)
    # Проверка на наличие нолика
    else:
        if all(check_from_right_to_left(temp_copy, 'x')):
            return end_the_game(player)

    # Проверка на заполненность поля
    if '-' not in set(temp_copy[0]).union(temp_copy[1]).union(temp_copy[2]):
        print('Ничья')
        game_active = False
        return game_active
    return game_active


def check_from_right_to_left(temp_copy, placeholder):
    diagonal_list = []
    for i in range(len(temp_copy)):
        if temp_copy[i][-(i + 1)] == placeholder:
            diagonal_list.append(True)
        else:
            diagonal_list.append(False)
    return diagonal_list


def check_from_left_to_right(temp_copy, placeholder):
    diagonal_list = []
    for i in range(len(temp_copy)):
        if temp_copy[i][i] == placeholder:
            diagonal_list.append(True)
        else:
            diagonal_list.append(False)
    return diagonal_list


def end_the_game(player):
    print(f'Победа игрока {player}')
    game_active = False
    return game_active


# Функция размещения хода игрока
def place_x_or_o(game_area, player, players_move):
    if player == 1:
        game_area[players_move[0] + 1][players_move[1]] = 'x'
    if player == 2:
        game_area[players_move[0] + 1][players_move[1]] = 'o'
    return game_area


# Функция которая будет выстраивать поле игры
def show_game_area(area):
    print(*area[0])
    print(area[0][1],end=' ')
    print(*area[1])
    print(area[0][2], end=' ')
    print(*area[2])
    print(area[0][3], end=' ')
    print(*area[3])


start_game()