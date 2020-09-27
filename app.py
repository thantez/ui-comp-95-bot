#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

# Imports
from cloudinary import uploader, config
import logging
from os import getenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Constants
TELEGRAM_BOT_TOKEN = getenv('UI_BOT_TOKEN')
CLOUDINARY_API_KEY = getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = getenv('CLOUDINARY_API_SECRET')
CLOUDINARY_API_NAME = getenv('CLOUDINARY_API_NAME')

# -- Keyboards
TERM_KEYBOARD = [
                [
                    InlineKeyboardButton('ترم ۱', callback_data='term 1'),
                    InlineKeyboardButton('ترم ۲', callback_data='term 2')
                ],
                [
                    InlineKeyboardButton('ترم ۳', callback_data='term 3'),
                    InlineKeyboardButton('ترم ۴', callback_data='term 4')
                ],
                [
                    InlineKeyboardButton('ترم ۵', callback_data='term 5'),
                    InlineKeyboardButton('ترم ۶', callback_data='term 6')
                ],
                [
                    InlineKeyboardButton('ترم ۷', callback_data='term 7'),
                    InlineKeyboardButton('ترم ۸', callback_data='term 8')
                ],
                [
                    InlineKeyboardButton('ترم ۹', callback_data='term 9'),
                    InlineKeyboardButton('ترم ۱۰', callback_data='term 10')
                ]
            ]
TERM_MARKUP = InlineKeyboardMarkup(TERM_KEYBOARD)

# Configs
# -- Logger config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# -- Cloudinary config
config(
  cloud_name = CLOUDINARY_API_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET
)

# Functions
def upload(link, user, term):
    """Will get a link and upload it to file storage."""
    path = f'ui_comp/{term}/{user.id} {user.username} _{user.first_name} {user.last_name}_'
    uploader.upload(link, public_id = path)

# -- Commands
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'سلام\n'
        'من رباتی هستم که قراره عکسای ورودی ۹۵ رو جمع‌آوری کنه.\n'
        'البته من فیلمم می‌گیرم!\n'
        'تو می‌تونی هر جوری که دلت می‌خواد، مثلا به صورت عکس یا فایل، چیزی که می‌خوای رو بفرستی.\n'
        'برای شروع کار، /send رو بفرست.\n'
        'اگه وسط کار دلت خواست لغو کنی، /cancel رو بفرست.\n'
        'همین دیگه. برو بریم!\n')

# -- Filters
def photo(update, context):
    """Get User's photo."""
    photo_id = update.message.photo[-1].file_id
    update.message.reply_photo(
        photo_id,
        caption='خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟',
        reply_markup=TERM_MARKUP)

def document(update, context):
    """Get User's photo."""
    document_id = update.message.document.file_id
    update.message.reply_document(
        document_id,
        caption='خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟',
        reply_markup=TERM_MARKUP)

# -- Callback query
def button(update, context):
    query = update.callback_query
    message = query.message
    user = message.chat
    photo = message.photo or list([None])
    file = photo[0] or message.document
    file_url = file.get_file().file_path

    upload(file_url, user, query.data)

    query.answer()
    query.edit_message_caption(caption="اوکی، ثبت شد.")

# -- Catch other messages
def other(update, context):
    """Semi help handler."""
    update.message.reply_text(
        'من نمی‌فهمم چی می‌گی!\n'
        'برام /send رو بفرست تا فرایندآپلود فایل شروع شه!')

# -- Main
def main():
    """Start the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.photo, photo))
    dp.add_handler(MessageHandler(Filters.document, document))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, other))

    updater.start_polling()
    logger.info("Bot started successfully!")
    updater.idle()

# Run app
if __name__ == '__main__':
    main()
