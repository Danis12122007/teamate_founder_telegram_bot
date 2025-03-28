from telebot import types
import telebot
import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")  # Загружаем ключ из переменной окружения
bot = telebot.TeleBot(API_KEY)
print(API_KEY)

data = {'id': '', 'username': '', 'cs2': 0, 'dota2': 0, 'pubg': 0}
user_data = None
cs2_answer = None
dota2_answer = None
pubg_answer = None


def user_existance_check():
    global user_data
    global data
    if not data['id']:
        return 0
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'players.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS players (tg_id INTEGER PRIMARY KEY, nikname VARCHAR, cs2 INTEGER, dota2 INTEGER, pubg INTEGER)')
    conn.commit()

    users = cur.execute('SELECT * FROM players WHERE tg_id = ?', (data['id'],))
    user_data = users.fetchall()

    cur.close()
    conn.close()

    if user_data:
        user_data = user_data[0]
        data['id'], data['username'], data['cs2'], data['dota2'], data['pubg'] = user_data[0], user_data[1], user_data[2], user_data[3], user_data[4]
        return 1
    else:
        return 0


@bot.message_handler(commands=['start'])
def start(message):
    global user_data
    data['id'] = message.from_user.id
    # print(f'user id: {data["id"]}')
    # print(f'user_info: {message.from_user}')
    # user_existance_check()
    bot.send_message(message.chat.id, f'Здравствуйте! Вас приветствует бот для поиска напарника в различных онлайн играх, таких как Counter-Strike 2, Dota 2, PUBG')

    # print(user_data)
    if not user_existance_check():
        bot.send_message(message.chat.id, 'Для начала введите свой ник в Steam')

        bot.register_next_step_handler(message, register_nikname)
    else:
        user_data = user_data[0]
        main(message)


@bot.message_handler(commands=['register'])
def register_nikname(message):
    if user_existance_check():
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')
        return
    global data
    nikname = message.text.strip()
    if nikname[0] == '/':
        bot.send_message(message.chat.id, "Ник не должен начинаться с /")
        bot.register_next_step_handler(message, register_nikname)
    data['username'] = nikname
    data['id'] = message.from_user.id
    bot.send_message(message.chat.id, 'Хорошо! А теперь оцените ваш уровень игры в следующих играх(1-минимальные умения, 5-знание игры в совершенстве)')
    register_skill(message)


def register_skill(message):
    global cs2_answer
    global dota2_answer
    global pubg_answer
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('1', callback_data='cs21')
    btn2 = types.InlineKeyboardButton('2', callback_data='cs22')
    btn3 = types.InlineKeyboardButton('3', callback_data='cs23')
    btn4 = types.InlineKeyboardButton('4', callback_data='cs24')
    btn5 = types.InlineKeyboardButton('5', callback_data='cs25')
    markup.row(btn1, btn2, btn3, btn4, btn5)
    cs2_answer = bot.send_message(message.chat.id, 'Counter-Strike 2', reply_markup=markup)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('1', callback_data='dota21')
    btn2 = types.InlineKeyboardButton('2', callback_data='dota22')
    btn3 = types.InlineKeyboardButton('3', callback_data='dota23')
    btn4 = types.InlineKeyboardButton('4', callback_data='dota24')
    btn5 = types.InlineKeyboardButton('5', callback_data='dota25')
    markup.row(btn1, btn2, btn3, btn4, btn5)
    dota2_answer = bot.send_message(message.chat.id, 'Dota 2', reply_markup=markup)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('1', callback_data='pubg1')
    btn2 = types.InlineKeyboardButton('2', callback_data='pubg2')
    btn3 = types.InlineKeyboardButton('3', callback_data='pubg3')
    btn4 = types.InlineKeyboardButton('4', callback_data='pubg4')
    btn5 = types.InlineKeyboardButton('5', callback_data='pubg5')
    markup.row(btn1, btn2, btn3, btn4, btn5)
    pubg_answer = bot.send_message(message.chat.id, 'PUBG', reply_markup=markup)


@bot.message_handler(commands=['info'])
def info(message):
    global data
    global user_data
    if not user_existance_check():
        bot.send_message(message.chat.id, "Для начала зарегистрируйтесь!")
    else:
        bot.send_message(message.chat.id, f'Username: {data["username"]}\nCounter_strike 2: {data["cs2"]}\nDota2: {data["dota2"]}\nPUBG: {data["pubg"]}')


def registration_success(message):
    bot.send_message(message.chat.id, "Ваш аккаунт успешно зарегистрирован")
    main(message)


@bot.message_handler(commands=['main'])
def main(message):
    if user_existance_check():
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Найти напарника', callback_data='find')
        btn2 = types.InlineKeyboardButton('Мои данные', callback_data='info')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Выберите опцию", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Для начала зарегистрируйтесь!")


@bot.message_handler(commands=['find_sim_players'])
def find_sim_players(message):
    global data
    global user_data
    if user_existance_check():
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, 'players.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('SELECT nikname FROM players WHERE cs2 = ? AND dota2 = ? AND pubg = ? AND tg_id != ?', (data['cs2'], data['dota2'], data['pubg'], data['id']))
        players = cur.fetchall()
        if players:
            players = players[0]
            players = "\n".join(players)
            bot.send_message(message.chat.id, "Вот список игроков с таким же уровнем игры как и у вас:")
            bot.send_message(message.chat.id, players)
        else:
            bot.send_message(message.chat.id, 'Игроков с таким же уровнем игры не нашлось')
    else:
        bot.send_message(message.chat.id, "Для начала зарегистрируйтесь!")


def write_to_db(message):
    global data
    global user_data
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'players.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('INSERT INTO players (tg_id, nikname, cs2, dota2, pubg) VALUES (?, ?, ?, ?, ?)', (data['id'], data["username"], data["cs2"], data["dota2"], data["pubg"]))
    conn.commit()

    users = cur.execute('SELECT * FROM players WHERE tg_id = ?', (data['id'],))
    print(f'1{users}')
    user_data = users.fetchall()[0]
    print(f'2{user_data}')
    cur.close()
    conn.close()
    registration_success(message)


@bot.message_handler(commands=['help'])
def help(message):
    text = "Список доступных команд:\n/start - запустить бота\n/register - зарегистрироваться\n/info - показать информацию о пользователе\n/main - показать основные опции\n/find_sim_players - найти напарников\n/help - помощь"
    bot.send_message(message.chat.id, text)


@bot.callback_query_handler()
def callback_handler(callback):
    global data
    if callback.data[:3] == 'cs2':
        if callback.data == 'cs21':
            data['cs2'] = 1
        elif callback.data == 'cs22':
            data['cs2'] = 2
        elif callback.data == 'cs23':
            data['cs2'] = 3
        elif callback.data == 'cs24':
            data['cs2'] = 4
        elif callback.data == 'cs25':
            data['cs2'] = 5
        bot.edit_message_text(f"Counter-Strike 2: {data['cs2']}", callback.message.chat.id, cs2_answer.message_id)
    elif callback.data[:3] == 'dot':
        if callback.data == 'dota21':
            data['dota2'] = 1
        elif callback.data == 'dota22':
            data['dota2'] = 2
        elif callback.data == 'dota23':
            data['dota2'] = 3
        elif callback.data == 'dota24':
            data['dota2'] = 4
        elif callback.data == 'dota25':
            data['dota2'] = 5
        bot.edit_message_text(f"Dota 2: {data['dota2']}", callback.message.chat.id, dota2_answer.message_id)
    elif callback.data[:3] == 'pub':
        if callback.data == 'pubg1':
            data['pubg'] = 1
        elif callback.data == 'pubg2':
            data['pubg'] = 2
        elif callback.data == 'pubg3':
            data['pubg'] = 3
        elif callback.data == 'pubg4':
            data['pubg'] = 4
        elif callback.data == 'pubg5':
            data['pubg'] = 5
        bot.edit_message_text(f"PUBG: {data['pubg']}", callback.message.chat.id, pubg_answer.message_id)

    if data['cs2'] != 0 and data['dota2'] != 0 and data['pubg'] != 0 and (callback.data[:3] == 'cs2' or callback.data[:3] == 'dot' or callback.data[:3] == 'pub'):
        write_to_db(callback.message)

    if callback.data == 'info':
        info(callback.message)

    if callback.data == 'find':
        find_sim_players(callback.message)


bot.remove_webhook()
bot.infinity_polling()
