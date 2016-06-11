#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4

import random
import re

from telegram import InlineQueryResultArticle, ParseMode, \
	InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yo me apunto!", callback_data="ButtonYes")], [InlineKeyboardButton("Finalizar", callback_data="ButtonEnd")]])
reply_markup_2 = InlineKeyboardMarkup([[InlineKeyboardButton("Ver mi amigo invisible..", callback_data="ButtonShow")]])


secretSantas = {}


#### Callbacks - Handlers ####

def start(bot, update):
	bot.sendMessage(update.message.chat_id, text='Hi!')

def help(bot, update):
	bot.sendMessage(update.message.chat_id, text='Help!')

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def escape_markdown(text):
	"""Helper function to escape telegram markup symbols"""
	escape_chars = '\*_`\['
	return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def new_secret_santa(bot, update):
	query = update.inline_query.query
	results = list()

	
	results.append(InlineQueryResultArticle(id=uuid4(),
											title=">> Crear Nuevo Amigo Invisible <<",
											input_message_content=InputTextMessageContent(
												"Amigo Invisible: De momento se apuntan 0 personas"),
											reply_markup=reply_markup))

	bot.answerInlineQuery(update.inline_query.id, results=results)



def aceptar_votacion(bot, update):
	query = update.callback_query
	santa_id = query.inline_message_id
	buttonid = query.data
	user = query.from_user

	# print(user)

	if buttonid == "ButtonYes":
		if santa_id not in secretSantas:
			secretSantas[santa_id] = {"people": [user], "status": "open", "relations": None}
		else:
			if secretSantas[santa_id]["status"] == "open":
				# Check if the person is already in the list..
				flag = 0
				for u in secretSantas[santa_id]["people"]:
					if u.id == user.id:
						flag = 1
				# ..if not, add it
				if flag == 0:
					secretSantas[santa_id]["people"].append(user)

				reply_message = "*AMIGO INVISIBLE!*  \nDe momento se apuntan " + str(len(secretSantas[santa_id]["people"])) + " personas: "
				for i in range(len(secretSantas[santa_id]["people"])-1):
					reply_message = reply_message + secretSantas[santa_id]["people"][i].first_name + ", "
				reply_message = reply_message + secretSantas[santa_id]["people"][-1].first_name

				bot.editMessageText(text=reply_message,
								inline_message_id=santa_id,
								reply_markup=reply_markup,
								parse_mode="Markdown")


	if buttonid == "ButtonEnd":

		if len(secretSantas[santa_id]["people"]) > 1: # with one person cannot shuffle :D

			secretSantas[santa_id]["status"] = "closed"
			names = list(map(lambda l: l.first_name + " " + l.last_name, secretSantas[santa_id]["people"]))
			secretSantas[santa_id]["relations"] = shuffle(names)
			print(secretSantas[santa_id]["relations"])

			reply_message = "*AMIGO INVISIBLE!* \nStatus: Cerrado  \nPersonas apuntadas: " + str(len(secretSantas[santa_id]["people"])) + " personas: "
			for i in range(len(secretSantas[santa_id]["people"])-1):
				reply_message = reply_message + secretSantas[santa_id]["people"][i].first_name + ", "
			reply_message = reply_message + secretSantas[santa_id]["people"][-1].first_name

			bot.editMessageText(text=reply_message,
								inline_message_id=santa_id,
								reply_markup=reply_markup_2,
								parse_mode="Markdown")


	if buttonid == "ButtonShow":
		if user.first_name + " " + user.last_name in secretSantas[santa_id]["relations"]:
			reply = "Tu amigo invisible es... " + secretSantas[santa_id]["relations"][user.first_name + " " + user.last_name]
		else:
			reply = "Tu no participas"

		bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
								text= reply,
								show_alert=True)





def shuffle(people):
	targets = people[:]
	done = False
	while not done:
		random.shuffle(targets)
		done = all(people[i] != targets[i] for i in range(len(people)))
	return dict(zip(people, targets))




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
	dp.add_handler(CallbackQueryHandler(aceptar_votacion))







	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
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

