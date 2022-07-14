# -*- coding: utf-8 -*-

import asyncio
import re
from sqlalchemy import and_
from database import Users, Vacancies, Questions, Citys, Responses, Session
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
import keyboard as kb

db = Session()  # через сессию будем отправлять запросы к БД
API_TOKEN = '' # add here your api token telegram bot
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def check_city(city: str) -> bool:
    check = db.query(Citys).filter(Citys.name_city == city.upper()).first()
    return check is not None


# Состояние нашей формы регистрации для пользователя
class FormRegistration(StatesGroup):
    FIO = State()
    serial_and_number_pass = State()
    city = State()
    tel_number = State()


help_text = "Вот доступные комманды:\n" \
            "<b>/help</b> - Вывод доступных команд\n" \
            "<b>/start</b> - Запуск бота, начало регистрации\n" \
            "<b>/cancel</b> - Отмена действий"


@dp.message_handler(commands='help')
async def help_message(message: types.Message):
    await bot.send_message(message.from_id, help_text, parse_mode=ParseMode.HTML)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    get_user = db.query(Users).filter(Users.id_telegram == message.from_id).first()
    if get_user is None:
        # Установка состояния
        await FormRegistration.FIO.set()
        await message.reply("<b>Здравствуйте!</b>\n"
                            "Я бот по поиску доступных вакансий в Аниксе.\n"
                            "Давайте зарегистрируемся\n"
                            "Введите Фамилию, Имя и Отчество\n"
                            "Пример: <b>Иванов Иван Иванович</b>\n"
                            "<i>Если у вас нет <u>отчества</u>, то пример ниже для вас</i>\n"
                            "Пример: <b>Иванов Иван -</b>",
                            parse_mode=ParseMode.HTML)
    else:
        await message.answer("С возвращением", reply_markup=kb.markup)


# Если ФИО введено не правильно, но говорим что человек ошибся
@dp.message_handler(lambda message: re.search(r"^([а-яА-Я]+) ([а-яА-Я]+) (([а-яА-Я]+)|(-))$",  message.text) is None,
                    state=FormRegistration.FIO)
async def process_FIO_invalid(message: types.Message):
    return await message.reply("ФИО введено не верно.\n"
                               "Пример: <b>Иванов Иван Иванович</b> или <b>Иванов Иван -</b>",
                               parse_mode=ParseMode.HTML)


# Если пользователь ввёл верно ФИО то сохраняем в состоянии и переходим к след состоянию
@dp.message_handler(lambda message: re.search(r"^([а-яА-Я]+) ([а-яА-Я]+) (([а-яА-Я]+)|(-))$", message.text) is not None,
                    state=FormRegistration.FIO)
async def process_FIO(message: types.Message, state: FSMContext):
    await state.update_data(FIO=message.text)  # сохраняем ФИО в нашь класс состояния
    await FormRegistration.next()  # переходим к следующему полю
    await message.reply("Хорошо.\n"
                        "Теперь введите серию и номер паспорта\n"
                        "Пример: <b>1234 567890</b>", parse_mode=ParseMode.HTML)


# тут так же как и выше, но уже проверям на ввод серии и номера паспорта
@dp.message_handler(lambda message: re.search(r"^(\d{4}) (\d{6})$", message.text) is None,
                    state=FormRegistration.serial_and_number_pass)
async def process_serial_and_number_pass_invalid(message: types.Message):
    return await message.reply("Серия и номер паспорта введены не верно.\n"
                               "Пример: <b>1234 567890</b>",
                               parse_mode=ParseMode.HTML)


# если серия и номер паспорта прошли проверку идём к след состоянию
@dp.message_handler(lambda message: re.search(r"(\d{4}) (\d{6})$", message.text) is not None,
                    state=FormRegistration.serial_and_number_pass)
async def process_serial_and_number_pass(message: types.Message, state: FSMContext):
    await FormRegistration.next()
    await state.update_data(serial_and_number_pass=message.text)
    await message.reply("Отлично, а теперь напишите из какого вы города")


@dp.message_handler(lambda message: check_city(message.text) is False, state=FormRegistration.city)
async def process_city_invalid(message: types.Message):
    await message.reply("Похоже вы не верно ввели название города\n"
                        "Попробуйте ещё раз.")


@dp.message_handler(lambda message: check_city(message.text) is True, state=FormRegistration.city)
async def process_city(message: types.Message, state: FSMContext):
    await FormRegistration.next()
    await state.update_data(city=message.text)
    await message.reply("И последнее.\n"
                        "Введите контактный номер телефона\n"
                        "Пример: <b>+71234567890</b> или <b>81234567890</b>",
                        parse_mode=ParseMode.HTML)


@dp.message_handler(lambda message: re.search(r"^(([+]\d{1,3})\d{10})|(8+\d{10})$", message.text) is None,
                    state=FormRegistration.tel_number)
async def process_tel_number_invalid(message: types.Message):
    return await message.reply("Телефон введён не верно\n"
                               "Пример: <b>+71234567890</b> или <b>81234567890</b>",
                               parse_mode=ParseMode.HTML)


@dp.message_handler(lambda message: re.search(r"^(([+]\d{1,3})\d{10})|(8+\d{10})$", message.text) is not None,
                    state=FormRegistration.tel_number)
async def process_tel_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tel_number'] = message.text

        new_user = Users(id_telegram=message.from_id, FIO=data['FIO'],
                         serial_and_number_pass=data['serial_and_number_pass'], city=data['city'].upper(),
                         tel_number=data['tel_number'])
        db.add(new_user)
        db.commit()

        await bot.send_message(message.chat.id,
                               "Регистрация прошла успешно!\n"
                               "Теперь вы можете просмотреть список вакансий",
                               reply_markup=kb.markup)
    await state.finish()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Отмена.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals=kb.text_btn1))
async def show_vacantions(message: types.Message):

    # получаем данные пользователя и все доступные вакансии
    get_user = db.query(Users).filter(Users.id_telegram == message.from_id).first()
    get_vacansions = db.query(Vacancies).filter(and_(Vacancies.city == get_user.city)).all()

    # Выводим все вакансии с кнопками если они есть
    if get_vacansions:
        for i in get_vacansions:

            text_message = f"<b>Вакансия №{i.id}</b>\n" \
                           f"<b>Город:</b> {i.city}\n" \
                           f"<b>Адрес:</b> {i.address}\n" \
                           f"<b>Время:</b> от {i.dateFrom} - до {i.dateTo}\n" \
                           f"<b>Тип занятости:</b> {i.type_vacancies}\n" \
                           f"<b>О вакансии:</b> {i.about}\n" \
                           f"<b>Цена:</b> {i.price} руб. 💵"

            await bot.send_message(message.from_id, text_message, reply_markup=kb.inline_keyboard_for_vacantion(i.id),
                                   parse_mode=ParseMode.HTML)
            await asyncio.sleep(.05)
            # задержку нужно чтобы не было додос по сообщения и вроде максимум 30 сообщений в сек, но у нас 20 в сек
    # Иначе выводим что вакансий нет
    else:
        await bot.send_message(message.from_id, "К сожалению вакансий пока нет 😢")


# если у вакансии нажата кнопка "откликнуться"
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn1'))
async def process_callback_btn1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    get_user = db.query(Users).filter(Users.id_telegram == callback_query.from_user.id).first()
    get_vacantion = db.query(Vacancies).filter(Vacancies.id == int(callback_query.data.split('_')[1])).first()

    get_response = db.query(Responses).filter(and_(
        Responses.id_telegram_user == get_user.id_telegram,
        Responses.id_vacancies == get_vacantion.id
    )).first()

    if get_response is not None:
        await bot.send_message(callback_query.from_user.id,
                               "Вы уже оставляли отклик на эту вакансию 😌")
    else:
        new_response = Responses(response_user=get_user, responses_vacancie=get_vacantion)
        db.add(new_response)
        db.commit()
        await bot.send_message(callback_query.from_user.id,
                               "Вы успешно откликнулись 😊\n"
                               "С вами возможно позже свяжутся")


class FormQuestion(StatesGroup):
    vacancie_id = State()
    question = State()


# если у вакансии нажата кнопка "задать вопрос"
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn2'))
async def process_callback_btn2(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    id_vacantion = callback_query.data.split('_')[1]

    await FormQuestion.vacancie_id.set()
    await state.update_data(vacancie_id=int(id_vacantion))
    await FormQuestion.next()
    await bot.send_message(callback_query.from_user.id,
                           f"Напишите вопрос по вакансии №{id_vacantion}")


@dp.message_handler(state=FormQuestion.question)
async def process_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        get_vacantion = db.query(Vacancies).filter(Vacancies.id == int(data['vacancie_id'])).first()
        get_user = db.query(Users).filter(Users.id_telegram == message.from_user.id).first()

        data['question'] = message.text

        new_question = Questions(question_user=get_user, question_vacancie=get_vacantion, question=data['question'])
        db.add(new_question)
        db.commit()

        await bot.send_message(message.chat.id,
                               "Ваш вопрос успешно отправлен!\n"
                               "Ожидайте ответа, он вам обязательно придёт")
    await state.finish()


