import telebot
from config import BOT_TOKEN
from database.repository import CarRepository
from bot.handlers import register_handlers

def main():
    print("Ініціалізація бази даних...")
    repo = CarRepository('database/cars.db')
    
    print("Запуск Telegram-бота...")
    bot = telebot.TeleBot(BOT_TOKEN)
  
    register_handlers(bot, repo)
    
    print("Бот успішно запущений і готовий до роботи!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()
