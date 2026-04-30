import telebot
from telebot import types
from database.repository import CarRepository
from bot.keyboards import get_cards_keyboard
from telebot.apihelper import ApiTelegramException

# Словник для збереження поточного стану та результатів
user_data = {}

def get_user_storage(user_id: int):
    """Ініціалізація або отримання сховища користувача"""
    if user_id not in user_data:
        user_data[user_id] = {
            'session': {'album_ids': [], 'intro_msg_id': None},
            'results': []
        }
    return user_data[user_id]

def delete_safe(bot, chat_id, message_id):
    """Безпечне видалення повідомлення"""
    try:
        bot.delete_message(chat_id, message_id)
    except (ApiTelegramException, Exception):
        pass

def clear_user_album(bot, user_id):
    """Очищення залишків медіа-груп"""
    storage = get_user_storage(user_id)
    for msg_id in storage['session'].get('album_ids', []):
        delete_safe(bot, user_id, msg_id)
    storage['session']['album_ids'] = []

def register_handlers(bot: telebot.TeleBot, repo: CarRepository):

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🔍 Підібрати авто"))
        bot.send_message(
            message.chat.id, 
            "Вітаю в автосалоні! Скористайтеся кнопкою нижче для пошуку.", 
            reply_markup=markup
        )

    @bot.message_handler(func=lambda m: m.text == "🔍 Підібрати авто")
    def start_selection(message):
        user_id = message.chat.id
        # Скидаємо попередню сесію
        user_data[user_id] = get_user_storage(user_id)
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Седан", "Позашляховик", "Спорткар", "Будь-який")
        
        msg = bot.send_message(user_id, "Крок 1. Оберіть тип кузова:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_body_type_step)

    def process_body_type_step(message):
        user_id = message.chat.id
        get_user_storage(user_id)['session']['body_type'] = message.text
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Бензин", "Дизель", "Електро", "Не має значення")
        
        msg = bot.send_message(user_id, "Крок 2. Який тип двигуна?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_fuel_step)
        
    def process_fuel_step(message):
        user_id = message.chat.id
        get_user_storage(user_id)['session']['fuel_type'] = message.text
        
        msg = bot.send_message(
            user_id, 
            "Крок 3. Введіть макс. бюджет ($):", 
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(msg, process_budget_and_search)

    def process_budget_and_search(message):
        user_id = message.chat.id
        storage = get_user_storage(user_id)
        
        try:   
            max_price = float(message.text)
        except ValueError:
            msg = bot.send_message(user_id, "❌ Помилка. Введіть число (наприклад: 15000):")
            bot.register_next_step_handler(msg, process_budget_and_search)
            return

        session = storage['session']
        bot.send_message(user_id, "⏳ Шукаю варіанти...")
        
        found_cars = repo.find_cars(
            session.get('body_type', 'Будь-який'), 
            session.get('fuel_type', 'Не має значення'), 
            max_price
        )

        if not found_cars:
            bot.send_message(user_id, "Нічого не знайдено. Спробуйте змінити параметри.")
            return

        storage['results'] = found_cars
        intro_msg = bot.send_message(user_id, "Ось результати:", reply_markup=types.ReplyKeyboardRemove())
        storage['session']['intro_msg_id'] = intro_msg.message_id

        # Показ першої картки
        car = found_cars[0]
        bot.send_photo(
            user_id, car.main_image,
            caption=car.get_full_info(),
            reply_markup=get_cards_keyboard(0, len(found_cars))
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('card_'))
    def handle_pagination(call):
        user_id = call.from_user.id
        storage = get_user_storage(user_id)
        data = call.data.split('_')
        action = data[1]
        
        bot.answer_callback_query(call.id)

        if action == 'close':
            clear_user_album(bot, user_id)
            delete_safe(bot, user_id, storage['session'].get('intro_msg_id'))
            delete_safe(bot, user_id, call.message.message_id)
            bot.send_message(user_id, "Пошук завершено. Бажаєте ще?")
            return

        current_index = int(data[2])
        cars = storage['results']
        
        if not cars:
            bot.send_message(user_id, "Сесія застаріла.")
            return

        if action == 'photos':
            show_photos(bot, user_id, cars[current_index])
        
        elif action in ['next', 'prev']:
            clear_user_album(bot, user_id)
            new_index = current_index + 1 if action == 'next' else current_index - 1
            
            if 0 <= new_index < len(cars):
                update_car_card(bot, call.message, cars[new_index], new_index, len(cars))

def show_photos(bot, user_id, car):
    """Логіка відображення медіа-групи"""
    if not hasattr(car, 'images') or len(car.images) <= 1:
        bot.send_message(user_id, "Додаткових фото немає.")
        return

    clear_user_album(bot, user_id)
    media = [types.InputMediaPhoto(url) for url in car.images]
    
    try:
        sent = bot.send_media_group(user_id, media)
        get_user_storage(user_id)['session']['album_ids'] = [m.message_id for m in sent]
    except Exception as e:
        bot.send_message(user_id, "Помилка завантаження фото.")

def update_car_card(bot, message, car, index, total):
    """Оновлення повідомлення з карткою авто"""
    bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message.message_id,
        media=types.InputMediaPhoto(car.main_image, caption=car.get_full_info()),
        reply_markup=get_cards_keyboard(index, total)
    )