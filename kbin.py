from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def roles(players):
    roles_kb = InlineKeyboardMarkup(resize_keyboard=True)
    if players[0] == 0: roles_kb.add(InlineKeyboardButton('отправитель', callback_data="отправитель"))
    if players[1] == 0: roles_kb.add(InlineKeyboardButton('перехватчик', callback_data="перехватчик"))
    if players[2] == 0: roles_kb.add(InlineKeyboardButton('получатель', callback_data="получатель"))
    return roles_kb

todo_kb = InlineKeyboardMarkup(resize_keyboard=True)
todo_kb.add(InlineKeyboardButton('Да', callback_data="Да"))
todo_kb.add(InlineKeyboardButton('Нет', callback_data="Нет"))

basis_kb = InlineKeyboardMarkup(resize_keyboard=True)
basis_kb.add(InlineKeyboardButton('Вертикальный базис', callback_data="Вертикальный базис"))
basis_kb.add(InlineKeyboardButton('Диагональный базис', callback_data="Диагональный базис"))

vertic_kb = InlineKeyboardMarkup(resize_keyboard=True)
vertic_kb.add(InlineKeyboardButton('90°', callback_data="90°"))
vertic_kb.add(InlineKeyboardButton('0°', callback_data="0°"))

diag_kb = InlineKeyboardMarkup(resize_keyboard=True)
diag_kb.add(InlineKeyboardButton('45°', callback_data="45°"))
diag_kb.add(InlineKeyboardButton('-45°', callback_data="-45°"))