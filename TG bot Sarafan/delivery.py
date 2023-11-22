from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters
from database import create_connection, insert_order, close_connection
from sendmessage import send_message_to_admin

NAME, SURNAME, PHONE, FOOD = range(4)

def start_delivery(update: Update, context: CallbackContext) -> int:
    message = update.effective_message
    message.reply_text('Введите Ваше имя:')
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text('Теперь введите Вашу фамилию:')
    return SURNAME

def get_surname(update: Update, context: CallbackContext) -> int:
    context.user_data['surname'] = update.message.text
    update.message.reply_text('Введите Ваш номер телефона в формате +7XXXXXXXXXX:')
    return PHONE

def get_phone(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    update.message.reply_text('Введите список блюд, который Вы хотите заказать:')
    return FOOD

def get_food(update: Update, context: CallbackContext) -> int:
    context.user_data['food'] = update.message.text
    save_order_to_db(context)
    update.message.reply_text(
        'Спасибо за ваш заказ. Мы скоро Вам позвоним для уточнения деталей. ')
    return ConversationHandler.END

def save_order_to_db(context: CallbackContext):
    # Сохранение информации о заказе в базе данных
    conn = create_connection()
    name = context.user_data['name']
    surname = context.user_data['surname']
    phone = context.user_data['phone']
    food = context.user_data['food']
    order = (name, surname, phone, food)
    insert_order(conn, order)
    send_message_to_admin(context) # Отправка информации администратору
    close_connection(conn)