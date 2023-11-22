from telegram import Bot
from config import ADMIN_ID, TOKEN

def send_message_to_admin(context):
    bot = Bot(token=TOKEN)
    name = context.user_data['name']
    surname = context.user_data['surname']
    phone = context.user_data['phone']
    food = context.user_data['food']
    message_text = f"Получен новый заказ:\n\nИмя: {name}\nФамилия: {surname}\nТелефон: {phone}\nЗаказ: {food}"
    bot.send_message(chat_id=ADMIN_ID, text=message_text)
