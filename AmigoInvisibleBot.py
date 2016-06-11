# -*- coding: utf-8 -*-


from uuid import uuid4

import re

from telegram import InlineQueryResultArticle, ParseMode, \
	InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler
import logging

from secret_santa import SecretSanta

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

BUTTON_SIGNUP	= "BUTTON_SIGNUP"
BUTTON_CLOSE 	= "BUTTON_CLOSE"
BUTTON_VIEW  	= "BUTTON_VIEW"

buttons_open   = InlineKeyboardMarkup([[InlineKeyboardButton("Yo me apunto!", callback_data=BUTTON_SIGNUP)], [InlineKeyboardButton("Finalizar", callback_data=BUTTON_CLOSE)]])
buttons_closed = InlineKeyboardMarkup([[InlineKeyboardButton("Ver mi amigo invisible..", callback_data=BUTTON_VIEW)]])




secret_santas = {}

#### Callbacks - Handlers ####

def help(bot, update):
	bot.sendMessage(update.message.chat_id, text="""
		Manda un mensaje en un grupo que empieze por @Amigo_Invisible_bot 
	""")

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def escape_markdown(text):
	"""Helper function to escape telegram markup symbols"""
	escape_chars = '\*_`\['
	return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def build_message(ss):
	users = ss.user_list()

	reply_message = (
		"*Amigo invisible*           	\n"	+
		"*==========================*	\n"	+
		"Estado: _{}_                	\n" +
		"Hay {} personas apuntadas:  	\n"	+
		"{}                          	\n"	#
	).format(
		"abierto" if ss.is_open else "cerrado",
		len(users),
		"".join(map(lambda u: "+ {}\n".format(escape_markdown(u)), users))
	)

	reply_markup = buttons_open if ss.is_open else buttons_closed

	return {
		"text": reply_message,
		"reply_markup": reply_markup,
		"parse_mode": "Markdown",
	}


def new_secret_santa(bot, update):
	query = update.inline_query.query
	results = [
		InlineQueryResultArticle(
			id                   	= uuid4(),
			title                	= ">> Crear Nuevo Amigo Invisible <<",
			input_message_content	= InputTextMessageContent("Amigo Invisible\nNo hay nadie apuntado. Se el primero!"),
			reply_markup         	= buttons_open)
	]
	bot.answerInlineQuery(update.inline_query.id, results=results)


def button_click_callback(bot, update):
	query = update.callback_query
	message_id = query.inline_message_id
	ss = secret_santas.get(message_id)

	if ss == None:
		ss = secret_santas[message_id] = SecretSanta(message_id)

	button_id = query.data
	user = query.from_user

	if button_id == BUTTON_SIGNUP:
		if ss.sign_up(user) == True:

			users = ss.user_list()

			bot.editMessageText(
				inline_message_id = message_id,
				**build_message(ss))

		else:
			bot.answerCallbackQuery(
				callback_query_id	= update.callback_query.id,
				text             	= "Ya estas apuntado campeon!",
				show_alert       	= True)


	elif button_id == BUTTON_CLOSE:

		if not ss.close():
			bot.answerCallbackQuery(
				callback_query_id	= update.callback_query.id,
				text             	= "No se ha podido cerrar. Asegurate de que haya mas de 1 persona apuntada!",
				show_alert       	= True)
			return

		bot.editMessageText(
			inline_message_id = message_id,
			**build_message(ss))


	if button_id == BUTTON_VIEW:

		secret_santa_user = ss.get_secret_santa_for(user)

		alert_text = ""

		if secret_santa_user is not None:
			alert_text = "Tu amigo invisible es: {}".format(secret_santa_user)
		else:
			alert_text = "No estas participando!"

		bot.answerCallbackQuery(
			callback_query_id	= update.callback_query.id,
			text             	= alert_text,
			show_alert       	= True)



def main():

	# Read config file
	with open("token.txt") as f:
		bot_token = f.readline().strip()

	# Create the Updater and pass it your bot's token.
	updater = Updater(bot_token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(InlineQueryHandler(new_secret_santa))
	dp.add_handler(CallbackQueryHandler(button_click_callback))

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", help))
	dp.add_handler(CommandHandler("help", help))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Block until the user presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()

