from telebot import types

def get_cards_keyboard(current_index: int, total_count: int):
    markup = types.InlineKeyboardMarkup()
    
    prev_btn = types.InlineKeyboardButton("⬅️ Назад", callback_data=f"card_prev_{current_index}")
    count_btn = types.InlineKeyboardButton(f"{current_index + 1} / {total_count}", callback_data="card_ignore")
    next_btn = types.InlineKeyboardButton("Вперед ➡️", callback_data=f"card_next_{current_index}")
    
    row = []
    if current_index > 0:
        row.append(prev_btn)
    row.append(count_btn)
    if current_index < total_count - 1:
        row.append(next_btn)
        
    markup.add(*row)
  
    
    photo_btn = types.InlineKeyboardButton("📸 Показати всі фото", callback_data=f"card_photos_{current_index}")
    markup.add(photo_btn)

    close_btn = types.InlineKeyboardButton("🔄 Новий пошук", callback_data="card_close")
    markup.add(close_btn)
    
    return markup
