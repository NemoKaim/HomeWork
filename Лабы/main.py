import telebot
import asyncio

import sqlite3
from sqlite3 import Error


conn = sqlite3.connect('main.db')

  
cursor = conn.cursor()

# Создаем таблицу Waiting
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Waiting'")
if cursor.fetchone() is None:
	# Таблица не существует, создаем ее
	cursor.execute('''
		CREATE TABLE Waiting (
			user_id INTEGER
		)
	''')
	print("Таблица Waiting создана")

# Проверяем существование таблицы Members
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Members'")
if cursor.fetchone() is None:
	# Таблица не существует, создаем ее
	cursor.execute('''
		CREATE TABLE Members (
			member_id INTEGER,
			member_id2 INTEGER
		)
	''')
	print("Таблица Members создана")


# Сохраняем изменения в базе данных
conn.commit()

# Закрываем подключение
conn.close()


TOKEN = '6440756289:AAFr0f_cyyQTCpnvK_NBW-YmBqYRbezwELg'


bot = telebot.TeleBot(TOKEN)
big_text = """
	***Привет***, я предоставляю возможность всем пользователям общаться ***анонимно***, и абсолютно с ***случайным собеседником.***

	> /join - Для поиска собеседника
	> /leave - Выход из поиска/чата

	"""
@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, big_text, parse_mode="Markdown")

@bot.message_handler(commands=['join'])
def search_chat(message):
	user_id = message.from_user.id
	join_user(user_id)

@bot.message_handler(commands=['leave'])
def leave_chat(message):
	user_id = message.from_user.id
	conn = sqlite3.connect('main.db')
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Members WHERE member_id = ? OR member_id2 = ?", (user_id, user_id))
	row = cursor.fetchone()
	if row:
		if row[0]==user_id:
			Return = row[1]
		else:
			Return = row[0]
		cursor.execute("DELETE FROM Members WHERE member_id=? OR member_id2=?", (user_id,user_id))
		conn.commit()
		print("Строка удалена, Return=", Return)
		cursor.execute('INSERT INTO Waiting (user_id) VALUES (?)', (Return,))

		conn.commit()
		conn.close()

		bot.send_message(user_id, "Вы вышли из чата/поиска -> !join, найти собеседника")

		bot.send_message(Return, "Собеседник вышел из чата, вы снова находитесь в списке поиска собеседника")
		join_user(Return)

	else:
		conn = sqlite3.connect('main.db')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Waiting WHERE user_id=?", (user_id,))
		row = cursor.fetchone()

		if row is None:
			bot.send_message(user_id, "Вы и не находились в поиске/чате")
		else:
			cursor.execute("DELETE FROM Waiting WHERE user_id=?", (user_id,))
			conn.commit()
			bot.send_message(user_id, "Вы вышли из чата/поиска -> !join, найти собеседника")

	conn.close()

def join_user(arg_id):
	conn = sqlite3.connect('main.db')
	cursor = conn.cursor()



	cursor.execute("SELECT * FROM Members WHERE member_id = ? OR member_id2 = ?", (arg_id, arg_id))
	row = cursor.fetchone()

	cursor.execute("SELECT * FROM Waiting WHERE user_id = ?", (arg_id,))
	row2 = cursor.fetchone()

	if row or row2:
		bot.send_message(arg_id, "Вы уже в очереди/чате")
		conn.commit()	
		conn.close()
		return

	conn.close()

	conn = sqlite3.connect('main.db')
	cursor = conn.cursor()

	cursor.execute('INSERT INTO Waiting (user_id) VALUES (?)', (arg_id,))
	conn.commit()
	conn.close()
   
	bot.send_message(arg_id, "Готово, вы в списке поиска собеседника. \n Мы сообщим вам когда найдём для вас собеседника")
	

	
	conn = sqlite3.connect('main.db')
	cursor = conn.cursor()

	
	cursor.execute('SELECT user_id FROM Waiting WHERE user_id != ? ORDER BY RANDOM() LIMIT 1', (arg_id,))


	row = cursor.fetchone()
	conn.close()

	if row is not None:

		conn = sqlite3.connect('main.db')
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Waiting WHERE user_id=?", (arg_id,))
		cursor.execute("DELETE FROM Waiting WHERE user_id=?", (row[0],))
		cursor.execute("INSERT INTO Members (member_id, member_id2) VALUES (?, ?)", (arg_id, row[0]))
		conn.commit()
		conn.close()

		bot.send_message(arg_id, "Собеседник найден.\n")

		bot.send_message(row[0], "Собеседник найден.\n")


@bot.message_handler(func=lambda message: message.from_user.is_bot == False)
def handle_message(message):
	user_id = message.from_user.id
	conn = sqlite3.connect('main.db')
	cursor = conn.cursor()


	cursor.execute("SELECT * FROM Members WHERE member_id = ? OR member_id2 = ?", (user_id, user_id))
	row = cursor.fetchone()
	conn.close()
	if row:
		if row[0]==user_id:
			bot.send_message(row[1], message.text)

		if row[1]==user_id:
			bot.send_message(row[0], message.text)

bot.polling(none_stop=True)