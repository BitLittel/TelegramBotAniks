# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, create_engine, DateTime, Text, Unicode, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.scoping import scoped_session
import config_DB

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    # id = Column(Integer, primary_key=True, autoincrement=True)
    id_telegram = Column(Integer, primary_key=True)
    FIO = Column(Unicode(255, collation='utf8_unicode_ci'))
    serial_and_number_pass = Column(Unicode(128, collation='utf8_unicode_ci'))
    city = Column(Unicode(255, collation='utf8_unicode_ci'))
    tel_number = Column(Unicode(255, collation='utf8_unicode_ci'))
    question = relationship('Questions', backref='question_user', lazy='dynamic')
    responses = relationship('Responses', backref='response_user', lazy='dynamic')

    def __repr__(self):
        return "<Users(%r, %r, %r)>" % (self.id, self.id_telegram, self.FIO)


class Vacancies(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(Unicode(255, collation='utf8_unicode_ci'))
    dateFrom = Column(DateTime)
    dateTo = Column(DateTime)
    type_vacancies = Column(Unicode(255, collation='utf8_unicode_ci'))
    about = Column(Text)
    price = Column(Integer)
    address = Column(Unicode(255, collation='utf8_unicode_ci'))
    question = relationship('Questions', backref='question_vacancie', lazy='dynamic')
    response = relationship('Responses', backref='responses_vacancie', lazy='dynamic')
    # called = Column(Integer)

    def __repr__(self):
        return "<Vacancies(%r, %r, %r)>" % (self.id, self.city, self.dateFrom)


class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_telegram_question = Column(Integer, ForeignKey(Users.id_telegram))
    vacancie_id = Column(Integer, ForeignKey(Vacancies.id))
    question = Column(Text)
    answer = Column(Text, default="")
    sended = Column(Boolean, default=False)

    def __repr__(self):
        return "<Questions(%r, %r, %r)>" % (self.id, self.id_telegram_question, self.question)


class Responses(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_telegram_user = Column(Integer, ForeignKey(Users.id_telegram))
    id_vacancies = Column(Integer, ForeignKey(Vacancies.id))


class Citys(Base):
    __tablename__ = 'citys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name_city = Column(Unicode(255, collation='utf8_unicode_ci'))


engine = create_engine('mysql+pymysql://%s:%s@%s/%s?charset=utf8' % (config_DB.USER,
                                                                     config_DB.PASSWORD,
                                                                     config_DB.IP,
                                                                     config_DB.DATABASE_NAME),
                       encoding='utf8', echo=False)
Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker())
Session.configure(bind=engine)  # Создаём сессию с БД
