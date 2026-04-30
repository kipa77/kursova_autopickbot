import telebot
from telebot import types
from database.repository import CarRepository
from bot.keyboards import get_cards_keyboard
from telebot.apihelper import ApiTelegramException

user_sessions = {}
user_results = {}

def clear_album(bot, user_id):
    album_ids = user_sessions.get(user_id, {}).get('album_ids', [])
    for msg_id in album_ids:
        try:
            bot.delete_message(chat_id=user_id, message_id=msg_id)
        except Exception:
            pass
  
    if user_id in user_sessions:
        user_sessions[user_id]['album_ids'] = []

def register_handlers(bot: telebot.TeleBot, repo: CarRepository):

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔍 Підібрати авто")
        markup.add(btn1)
        
        bot.send_message(
            message.chat.id, 
            "Вітаю в автосалоні! Натисніть 'Підібрати авто', щоб розпочати пошук.", 
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text == "🔍 Підібрати авто")
    def start_selection(message):
        user_id = message.chat.id
        user_sessions[user_id] = {'album_ids': [], 'intro_msg_id': None} 
       
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Седан", "Позашляховик", "Спорткар", "Будь-який")
        
        msg = bot.send_message(user_id, "Крок 1. Оберіть тип кузова:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_body_type_step)

    def process_body_type_step(message):
        user_id = message.chat.id
        user_sessions[user_id]['body_type'] = message.text
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Бензин", "Дизель", "Електро", "Не має значення")
        
        msg = bot.send_message(user_id, "Крок 2. Який тип двигуна розглядаєте?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_fuel_step)
        
    def process_fuel_step(message):
        user_id = message.chat.id
        user_sessions[user_id]['fuel_type'] = message.text
        
        markup = types.ReplyKeyboardRemove()
        msg = bot.send_message(user_id, "Крок 3. Введіть ваш максимальний бюджет у доларах (тільки цифри):", reply_markup=markup)
        
        bot.register_next_step_handler(msg, process_budget_and_search)

    def process_budget_and_search(message):
        user_id = message.chat.id
        
        try:   
            max_price = float(message.text)
        except ValueError:
            msg = bot.send_message(user_id, "Будь ласка, введіть суму тільки цифрами (наприклад: 15000):")
            bot.register_next_step_handler(msg, process_budget_and_search)
            return

        session = user_sessions.get(user_id, {})
        body_type = session.get('body_type', 'Будь-який')
        fuel_type = session.get('fuel_type', 'Не має значення')

        bot.send_message(user_id, "⏳ Шукаю найкращі варіанти для вас...")
        found_cars = repo.find_cars(body_type, fuel_type, max_price)

        if not found_cars:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("🔍 Підібрати авто")
            bot.send_message(
                user_id, 
                "На жаль, за вашими критеріями зараз немає авто. Спробуйте збільшити бюджет або змінити тип кузова.", 
                reply_markup=markup
            )
            return

        user_results[user_id] = found_cars

        remove_markup = types.ReplyKeyboardRemove()
        intro_msg = bot.send_message(user_id, "Ось що я знайшов:", reply_markup=remove_markup)
        
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]['intro_msg_id'] = intro_msg.message_id

        first_car = found_cars[0]
        bot.send_photo(
            chat_id=user_id,
            photo=first_car.main_image,         
            caption=first_car.get_full_info(),   
            reply_markup=get_cards_keyboard(0, len(found_cars))
        )


    @bot.callback_query_handler(func=lambda call: call.data.startswith('card_'))
    def handle_pagination(call):
        bot.answer_callback_query(call.id)
        
        try:
            user_id = call.from_user.id
            data = call.data.split('_')
            action = data[1] 
            
            if action == 'ignore':
                return
                
            if action == 'close':
                clear_album(bot, user_id)
                intro_msg_id = user_sessions.get(user_id, {}).get('intro_msg_id')
                if intro_msg_id:
                    try:
                        bot.delete_message(chat_id=user_id, message_id=intro_msg_id)
                    except Exception:
                        pass

                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("🔍 Підібрати авто")
                bot.send_message(user_id, "Пошук завершено. Бажаєте почати спочатку?", reply_markup=markup)
                return

            current_index = int(data[2])
            cars = user_results.get(user_id)
            
            if not cars:
                bot.send_message(user_id, "Сесія застаріла, почніть пошук знову.")
                return

            if action == 'photos':
                car = cars[current_index]
                
                if not hasattr(car, 'images') or not car.images or len(car.images) <= 1:
                    bot.send_message(user_id, "Для цього авто поки немає додаткових фото.")
                    return
                
                clear_album(bot, user_id)
                
                loading_msg = bot.send_message(user_id, "⏳ Завантажую альбом...")
                
                media_group = []
                for image_url in car.images:
                    media_group.append(types.InputMediaPhoto(media=image_url))
                
                try:
                    sent_messages = bot.send_media_group(chat_id=user_id, media=media_group)
                    user_sessions[user_id]['album_ids'] = [msg.message_id for msg in sent_messages]
                    
                    bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
                except Exception as e:
                    bot.send_message(user_id, "Не вдалося завантажити деякі фотографії.")
                    print(f"Помилка відправки альбому: {e}")
                return

            if action in ['next', 'prev']:
                clear_album(bot, user_id)

            new_index = current_index + 1 if action == 'next' else current_index - 1

            if 0 <= new_index < len(cars):
                car = cars[new_index]
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=types.InputMediaPhoto(
                        media=car.main_image,
                        caption=car.get_full_info()
                    ),
                    reply_markup=get_cards_keyboard(new_index, len(cars))
                )
                
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                print(f"Помилка Telegram API: {e}")
        except Exception as e:
            print(f"Неочікувана помилка пагінації: {e}")
