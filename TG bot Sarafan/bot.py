from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Updater, CommandHandler, CallbackContext, CallbackQueryHandler, 
                          ConversationHandler, MessageHandler, Filters)
from delivery import start_delivery, get_surname, get_name, get_phone, get_food
from config import TOKEN

NAME, SURNAME, PHONE, FOOD = range(4)

def start(update: Update, context: CallbackContext) -> None: 
    update.message.reply_text(
        "Привет! Добро пожаловать в бот кафе Сарафан. Для получения более подробной информации выберите один из вариантов ниже:", 
        reply_markup=main_menu_keyboard()
    )

def show_menu(update: Update, context: CallbackContext) -> None:
    update.callback_query.message.reply_text("Меню", reply_markup=menu_keyboard())

def show_event(update: Update, context: CallbackContext) -> None:
    update.callback_query.message.reply_text("Мероприятия", reply_markup=event_keyboard())

def show_contacts(update: Update, context: CallbackContext) -> None:
    update.callback_query.message.reply_text(
        "Контакты: тел. +7 (918) 253 45 42",
    )

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'menu':
        show_menu(update, context)
    elif query.data == 'contacts':
        show_contacts(update, context)
    elif query.data == 'events':
        show_event(update, context)
    elif query.data == 'order':
        return start_delivery(update, context)
    elif query.data == 'call_contact':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Свяжитесь с нами по номеру +7 (918) 253 45 42")

def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Меню", callback_data='menu')],
        [InlineKeyboardButton("Мероприятия", callback_data='events')],
        [InlineKeyboardButton("Контакты", callback_data='contacts')],
        [InlineKeyboardButton("Оставить заказ", callback_data='order')]
    ]
    return InlineKeyboardMarkup(keyboard)

def menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Основные блюда", url='https://sarafan-cafe.ru/#Main')],
        [InlineKeyboardButton("Завтраки", url='https://sarafan-cafe.ru/#Breakfast')],
        [InlineKeyboardButton("Закуски", url='https://sarafan-cafe.ru/#Snacks')],
        [InlineKeyboardButton("Салаты", url='https://sarafan-cafe.ru/#Salads')],
        [InlineKeyboardButton("Детское меню", url='https://sarafan-cafe.ru/#Children')],
        [InlineKeyboardButton("Сезонное меню", url='https://sarafan-cafe.ru/#Season')]
    ]
    return InlineKeyboardMarkup(keyboard)

def event_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Регистрация на мероприятие", url='https://sarafan-cafe.ru/page31019388.html')],
    ]
    return InlineKeyboardMarkup(keyboard)

delivery_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_delivery, pattern='^order')],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        SURNAME: [MessageHandler(Filters.text & ~Filters.command, get_surname)],
        PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
        FOOD: [MessageHandler(Filters.text & ~Filters.command, get_food)]
    },
    fallbacks=[]
)

updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(delivery_conv_handler)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
