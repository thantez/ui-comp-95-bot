#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from cloudinary import uploader, api, config
import logging
from os import getenv

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PHOTO, TIME = range(2)

information_keyboard = [['term 1'], ['term 2'], ['term 3'], ['term 4'], ['term 5'], ['term 6'], ['term 7'], ['term 8'], ['term 9']]

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('سلام\n'
                              'من رباتی هستم که قراره عکسای ورودی ۹۵ رو جمع‌آوری کنه.\n'
                              'البته من فیلمم می‌گیرم!\n'
                              'تو می‌تونی هر جوری که دلت می‌خواد، مثلا به صورت عکس یا فایل، چیزی که می‌خوای رو بفرستی.\n'
                              'برای شروع کار، /send رو بفرست.\n'
                              'اگه وسط کار دلت خواست لغو کنی، /cancel رو بفرست.\n'
                              'همین دیگه. برو بریم!\n')

def other(update, context):
    """Semi help handler."""
    update.message.reply_text('من نمی‌فهمم چی می‌گی!\n'
                              'برام /send رو بفرست تا فرایندآپلود فایل شروع شه!')

    return ConversationHandler.END

def send(update, context):
    """Start photo conversation"""
    update.message.reply_text('خب. برای شروع، عکس یا فایل بفرست.\n'
                              'حواست باشه که حجم چیزی که می‌فرستی بیشتر از ۱۰ مگ نشه!')
    return PHOTO

def upload(link, user, time):
    """Will get a link and upload it to file storage."""
    path = f'ui_comp/{time}/{user.id} {user.username} _{user.first_name} {user.last_name}_'

    uploader.upload(link, public_id = path)

def photo(update, context):
    """Get User's photo."""
    photo_file = update.message.photo[-1].get_file()
    context.user_data['file_url'] = photo_file.file_path

    update.message.reply_text("خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟",
        reply_markup=ReplyKeyboardMarkup(information_keyboard, one_time_keyboard=True))

    return TIME

def file(update, context):
    """Get User's photo."""
    document = update.message.document.get_file()
    context.user_data['file_url'] = document.file_path

    update.message.reply_text("خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟\n"
                              "راستی، حتما ترم رو با کیبورد انتخاب کن!",
        reply_markup=ReplyKeyboardMarkup(information_keyboard, one_time_keyboard=True))

    return TIME

def information(update, context):
    """Get term of this file."""
    url = context.user_data['file_url']
    user = update.message.from_user
    term = update.message.text

    upload(url, user, term)

    update.message.reply_text("ذخیره شد. اگه دلت می‌خواد بازم بفرستی، /send رو بزن وگرنه خدانگهدار!", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('اوکی، لغو شد.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def main():
    """Start the bot."""
    TELEGRAM_BOT_TOKEN = getenv('UI_BOT_TOKEN')
    CLOUDINARY_API_KEY = getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = getenv('CLOUDINARY_API_SECRET')
    CLOUDINARY_API_NAME = getenv('CLOUDINARY_API_NAME')

    config(
      cloud_name = CLOUDINARY_API_NAME,
      api_key = CLOUDINARY_API_KEY,
      api_secret = CLOUDINARY_API_SECRET
    )

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send)],

        states={
            PHOTO: [
                MessageHandler(Filters.photo, photo),
                MessageHandler(Filters.document.category("image"), file),
                MessageHandler(Filters.document.category("video"), file)
            ],
            TIME: [MessageHandler(Filters.regex('^(term) [0-9]$'), information)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add conversation handler
    dp.add_handler(conv_handler)

    # on noncommand i.e message - other the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, other))

    # Start the Bot
    updater.start_polling()

    logger.info("Bot started successfully!")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
