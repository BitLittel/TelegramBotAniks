# -*- coding: utf-8 -*-

from aiogram import Bot
from main_bot import db
from database import Questions
from sqlalchemy import and_
from aiogram.types import ParseMode


async def check_and_send_answer(bot: Bot):
    get_all_answer = db.query(Questions).filter(and_(Questions.answer != "", Questions.sended == False)).all()
    for answer in get_all_answer:
        await bot.send_message(answer.id_telegram_question,
                               f'<b>Поступил ответ на ваш вопрос по вакансии №{answer.vacancie_id}!</b>\n'
                               f'Ваш вопрос: {answer.question}\n\n'
                               f'Ответ: {answer.answer}', parse_mode=ParseMode.HTML)
        answer.sended = True
    db.commit()


# Создаем функцию, в которой будет добавление наших тасков.
def set_scheduled_jobs(scheduler, bot, *args, **kwargs):
    # Добавляем задачи на выполнение
    scheduler.add_job(check_and_send_answer, "interval", seconds=120, args=(bot,))
