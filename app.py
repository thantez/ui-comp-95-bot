#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

# Imports
from cloudinary import uploader, config, utils
import logging
from os import getenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from time import time

# Constants
TELEGRAM_BOT_TOKEN = getenv('UI_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))

# -- Cloudinary
CLOUDINARY_API_KEY = getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = getenv('CLOUDINARY_API_SECRET')
CLOUDINARY_API_NAME = getenv('CLOUDINARY_API_NAME')

# -- Admins
ADMINS = getenv('UI_BOT_ADMINS').split(',')

# -- Keyboards
TERM_KEYBOARD = [
    [
        InlineKeyboardButton('ترم ۱', callback_data='Term 1'),
        InlineKeyboardButton('ترم ۲', callback_data='Term 2')
    ],
    [
        InlineKeyboardButton('ترم ۳', callback_data='Term 3'),
        InlineKeyboardButton('ترم ۴', callback_data='Term 4')
    ],
    [
        InlineKeyboardButton('ترم ۵', callback_data='Term 5'),
        InlineKeyboardButton('ترم ۶', callback_data='Term 6')
    ],
    [
        InlineKeyboardButton('ترم ۷', callback_data='Term 7'),
        InlineKeyboardButton('ترم ۸', callback_data='Term 8')
    ],
    [
        InlineKeyboardButton('قاب آخر', callback_data='Final Frame'),
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
def upload(link, user, term, context):
    """Will get a link and upload it to file storage."""
    try:
        uuid = str(time())
        path = f'ui_comp/{term}/{user.id} {user.username} _{user.first_name} {user.last_name}_ {uuid}'

        uploader.upload(link, public_id = path, resource_type="auto")
        for admin in ADMINS:
            context.bot.send_message(admin,
                'یک محتوای جدید به چیزمیزای دانشکده اضافه شد.\n'
                f'این محتوا توسط @{user.username} فرستاده شده‌است.\n'
                f'محتوا مربوط به {term} است.')
    except Exception as err:
        logger.error(err)

# -- Commands
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'سلام\n'
        'من رباتی هستم که قراره عکسای ورودی ۹۵ رو جمع‌آوری کنه.\n'
        'البته من فیلمم می‌گیرم!\n'
        'تو می‌تونی هر جوری که دلت می‌خواد، مثلا به صورت عکس یا فایل، چیزی که می‌خوای رو بفرستی.\n'
        'برای شروع کار، /send رو بفرست.\n'
        'مخفیانه بهت بگم که با /download می‌تونی همه عکسا رو دانلود کنی.\n'
        '(ایح ایح ایح ایح 😈)\n'
        'همین دیگه. برو بریم!\n')

def download(update, context):
    """Send a link of gathered infos and medias to downloading them."""
    user = update.message.from_user

    if str(user.id) in ADMINS:
        url = utils.download_zip_url(prefixes="/")
        update.message.reply_text(url)
    else:
        logger.info(f"A new user want be admin! its id: {user.id} - {user.username}")
        update.message.reply_text('کی گفته بهت این دستور کار می‌کنه؟')

# -- Filters
def photo(update, context):
    """Get User's photo."""
    photo = update.message.photo[-1]
    photo_id = photo.file_id
    photo_size = photo.file_size

    logger.info(f"Size: {photo_size}")
    if(photo_size >= 10 * 1024 * 1024):
        update.message.reply_text('مگه بهت نگفتم باید فایلت کمتر از ده مگ باشه؟')
    else:
        update.message.reply_photo(
            photo_id,
            caption='خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟',
            reply_markup=TERM_MARKUP)

def video(update, context):
    """Get User's photo."""
    video = update.message.video
    video_id = video.file_id
    video_size = video.file_size

    logger.info(f"Size: {video_size}")
    if(video_size >= 10 * 1024 * 1024):
        update.message.reply_text('مگه بهت نگفتم باید فایلت کمتر از ده مگ باشه؟')
    else:
        update.message.reply_video(
            video_id,
            caption='خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟',
            reply_markup=TERM_MARKUP)

def document(update, context):
    """Get User's photo."""
    document = update.message.document
    document_id = document.file_id
    document_size = document.file_size

    logger.info(f"Size: {document_size}")
    if(document_size >= 10 * 1024 * 1024):
        update.message.reply_text('مگه بهت نگفتم باید فایلت کمتر از ده مگ باشه؟')
    else:
        update.message.reply_document(
            document_id,
            caption='خب. گرفتمش. حالا بگو این مربوط به ترم چنده؟',
            reply_markup=TERM_MARKUP)

# -- Callback query
def button(update, context):
    query = update.callback_query
    query.answer('داره آپلود میشه.')

    message = query.message
    user = message.chat
    photo = message.photo or list([None])
    file = photo[0] or message.video or message.document
    file_url = file.get_file().file_path

    upload(file_url, user, query.data, context)

    query.edit_message_caption(caption="اوکی، ثبت شد.")

# -- Catch other messages
def other(update, context):
    """Semi help handler."""
    update.message.reply_text(
        'من نمی‌فهمم چی می‌گی!\n'
        'برام /start رو بفرست تا بهت کمک کنم.')

# -- Main
def main():
    """Start the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("download", download))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.photo, photo))
    dp.add_handler(MessageHandler(Filters.video, video))
    dp.add_handler(MessageHandler(Filters.document.category("image"), document))
    dp.add_handler(MessageHandler(Filters.document.category("video"), document))
    dp.add_handler(MessageHandler(Filters.all, other))

    updater.start_webhook(listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN)

    updater.bot.setWebhook('https://ui-comp-bot.herokuapp.com/' + TOKEN)
    logger.info("Bot started successfully!")
    updater.idle()

# Run app
if __name__ == '__main__':
    main()
