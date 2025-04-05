import sqlite3
import os


# Определяем путь к базе данных внутри db_lession иначе anketa.db создается в корне
DB_PATH = os.path.join(os.path.dirname(__file__), "anketa.db")


"""Что делает этот код?
        Этот декоратор (ensure_connection) автоматически создает соединение с базой данных SQLite перед выполнением функции и закрывает его после выполнения.
        ✅ Преимущества:
            Не нужно вручную открывать и закрывать соединение при каждом запросе.
            with sqlite3.connect(DB_PATH) автоматически закроет соединение, даже если возникнет ошибка.
            Упрощает код, так как функции, работающие с БД, просто принимают conn как аргумент.
"""
# Декоратор для автоматического установления соединения с базой данных
def ensure_connection(func):
    
    # Внутренняя функция-обертка, принимающая любые аргументы
    def inner(*args, **kwargs):
        # Открываем соединение с базой данных в контексте "with"
        with sqlite3.connect(DB_PATH) as conn:
            # Вызываем оригинальную функцию, передавая соединение как аргумент
            res = func(*args, conn=conn, **kwargs)
        # Возвращаем результат выполнения функции
        return res
    
    return inner  # Возвращаем обернутую функцию


# Создание основной базы
@ensure_connection
def db_start( conn, force: bool = False):
    """ Проверить что нужные таблицы существют, иначе создать их
        Важно: миграция на такие табличы вы должны производить самостоятельно!
        :parm conn: Подключение к СУБД
        :param force: явно пересоздать все таблицы
    """
    try:
        print("Подключение успешно:", DB_PATH)  # Отладочный вывод
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS find_number_bot_user_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                is_bot BOOLEAN NOT NULL,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                type TEXT NOT NULL
            )
        ''')

        conn.commit()

        print("База данных и Таблицы созданы если нет и записыны данные!")

    except sqlite3.Error as e:
        print("Ошибка при подключении к базе данных:", e)

    # Сохранить изменения
    conn.commit()


# Создание базы для статистики
@ensure_connection
def find_number_bot_user_stat(conn, force: bool = False):
    """ Создание базы для статистики игры угадай число
    """
    try:
        print("Подключение успешно:", DB_PATH)

        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS find_number_bot_user_stat (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                in_game BOOLEAN NOT NULL,
                secret_number INTEGER,
                attempts INTEGER,
                total_games INTEGER,
                wins INTEGER
            )
        ''')

        conn.commit()
        print("База данных и Таблицы для сатистикы созданы!")
    except sqlite3.Error as e:
        print("Ошибка при подключении к базе данных статистикы:", e)


# Добавлет в базу данные личное пользователя 
@ensure_connection
def add_user_main_dp(user_id: int, is_bot: bool, first_name:str, last_name:str, username:str, type:str, conn=None,):
    c = conn.cursor()
    c.execute('INSERT INTO find_number_bot_user_data (user_id, is_bot, first_name, last_name, username, type) VALUES (?, ?, ?, ?, ?, ?)', (user_id, is_bot, first_name, last_name, username, type))
    conn.commit()


# возвращает из базы проверку есть ли пользователь в базе
@ensure_connection
def check_user(user_id: int, conn=None):
    c = conn.cursor()
    c.execute('SELECT user_id FROM find_number_bot_user_stat WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    return row[0] if row else None


@ensure_connection
def add_user_stat(user_id: int, in_game: bool, secret_number: int, attempts: int, total_games: int, wins: int, conn=None):
    c = conn.cursor()
    c.execute('INSERT INTO find_number_bot_user_stat (user_id, in_game, secret_number, attempts, total_games, wins) VALUES (?, ?, ?, ?, ?, ?)', (user_id, in_game, secret_number, attempts, total_games, wins))
    conn.commit()

@ensure_connection
def check_user_main_db(user_id: int, conn=None):
    c = conn.cursor()
    c.execute('SELECT user_id FROM find_number_bot_user_data WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    return row[0] if row else None


@ensure_connection
def get_user_stat(user_id: int, conn=None):
    """Получает статистику пользователя по user_id"""
    c = conn.cursor()
    c.execute('SELECT in_game, secret_number, attempts, total_games, wins FROM find_number_bot_user_stat WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    
    if row:
        return {
            "in_game": row[0],
            "secret_number": row[1],
            "attempts": row[2],
            "total_games": row[3],
            "wins": row[4]
        }
    return None  # Если пользователя нет в базе


@ensure_connection
def update_user_stat(user_id: int, in_game=None, secret_number=None, attempts=None, total_games=None, wins=None, conn=None):
    """Обновляет статистику пользователя, изменяя только переданные параметры"""
    
    c = conn.cursor()  # Создаём курсор для работы с базой данных

    # Список полей, которые будем обновлять
    update_fields = []  
    values = []  # Список значений для подстановки в SQL-запрос

    # Проверяем каждый параметр. Если он передан (не None), добавляем его в список обновлений
    if in_game is not None:
        update_fields.append("in_game = ?")
        values.append(in_game)
    if secret_number is not None:
        update_fields.append("secret_number = ?")
        values.append(secret_number)
    if attempts is not None:
        update_fields.append("attempts = ?")
        values.append(attempts)
    if total_games is not None:
        update_fields.append("total_games = ?")
        values.append(total_games)
    if wins is not None:
        update_fields.append("wins = ?")
        values.append(wins)

    # Если есть хотя бы одно поле для обновления
    if update_fields:
        # Формируем SQL-запрос. Поля объединяем через запятую
        query = f"UPDATE find_number_bot_user_stat SET {', '.join(update_fields)} WHERE user_id = ?"
        
        values.append(user_id)  # Добавляем user_id в конец списка значений
        c.execute(query, values)  # Выполняем SQL-запрос с параметрами
        conn.commit()  # Фиксируем изменения в базе данных




if __name__ == '__main__':
    db_start()
    check_user()
    #find_number_bot_user_stat()
    #add_user(user_id=77788, is_bot=False, username='kass', first_name='Kassym', last_name='Sauyt', type=False)