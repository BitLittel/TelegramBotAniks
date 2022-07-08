# -*- coding: utf-8 -*-

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# ----------------- КЛАВИАТУРЫ ------------------
text_btn1 = 'Посмотреть вакансии 📝'
# text_btn2 = 'Тут не знаю пока что добавить'

button1 = KeyboardButton(text_btn1)
# button2 = KeyboardButton(text_btn2)
markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button1)  # .add(button2)  # тут выводим колонкой
# markup = ReplyKeyboardMarkup().row(button1, button2)  # тут выводим в одну строку


# ----------------- ИНЛАЙН КНОПКИ ---------------
def inline_keyboard_for_vacantion(id_btn: int) -> InlineKeyboardMarkup:
    inline_btn1 = InlineKeyboardButton('Откликнуться ❤️', callback_data=f'btn1_{id_btn}')
    inline_btn2 = InlineKeyboardButton('Задать вопрос 🧐', callback_data=f'btn2_{id_btn}')
    return InlineKeyboardMarkup().row(inline_btn1, inline_btn2)


