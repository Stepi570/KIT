import asyncio
import logging
import sys
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from openpyxl import load_workbook  # type: ignore # для работы с Excel
from datetime import date, datetime, timedelta
import pytz  # type: ignore # для работы с часовыми поясами
import pandas as pd  # type: ignore # если используете для обработки данных
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


file_path = 'file.xlsx'
df = pd.read_excel('file.xlsx')
API_TOKEN = 'Ваш API токен' #Вставьте токен
Bot = Bot(token=API_TOKEN,request_timeout=300)
dp = Dispatcher()
awaiting_file = False
user_id_to_notify = "963729102"
ADMIN_ID = 963729102
days_mapping = {
    'пн': 'Понедельник',
    'вт': 'Вторник',
    'ср': 'Среда',
    'чт': 'Четверг',
    'пт': 'Пятница',
    'сб': 'Суббота',
    'вс': 'Воскресенье'
}



main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Завтра'),KeyboardButton(text='Сегодня')],
    [KeyboardButton(text='День недели'),KeyboardButton(text='Все расписание'),KeyboardButton(text='Какая неделя')],
    [KeyboardButton(text='Группа'),KeyboardButton(text='Преподаватели'),KeyboardButton(text='Обратная связь')]
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

otmena = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True, input_field_placeholder='Обратная связь...')

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='id учасников'),KeyboardButton(text='Поменять файл')],
    [KeyboardButton(text='Рассылка'),KeyboardButton(text='Сообщение пользователю')],
    [KeyboardButton(text='Назад')]
    
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

chet_nechet = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Четная'),KeyboardButton(text='Нечетная')],
    [KeyboardButton(text='Общее')],
    [KeyboardButton(text='Назад')]
    
], resize_keyboard=True, input_field_placeholder='Чет или нечет...')


days_of_week_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Понедельник'),KeyboardButton(text='Вторник')],
    [KeyboardButton(text='Среда'),KeyboardButton(text='Четверг')],
    [KeyboardButton(text='Пятница'),KeyboardButton(text='Суббота')],
    [KeyboardButton(text='Назад')]
], resize_keyboard=True, input_field_placeholder='Выберите день...')



user_ids = []
router = Router(name=__name__)
tasks = {}  
user_groups = {}
register = []
group_list = []
waiting_for_file = 0
waiting_for_group = False
USERS_FILE = "users.txt"
USERS_NEW = "user_new.txt"
day = None
id = 0
id_pip=1
def get_users_ids():
    """Загружает ID пользователей из файла."""
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(map(int, f.read().splitlines()))

def get_users_new():
    """Загружает ID пользователей из файла."""
    if not os.path.exists(USERS_NEW):
        return set()
    with open(USERS_NEW, "r") as f:
        return set(map(int, f.read().splitlines()))

def save_user_id(user_id):
    users_ids = get_users_ids()
    users_ids.add(user_id)
    with open(USERS_FILE, "w") as f:
        f.write("\n".join(map(str, users_ids)))

def save_user_new(e_user_new):
    global USERS_NEW
    
    # Читаем все существующие пользователи из файла
    with open(USERS_NEW, "r") as f:
        existing_users = set(line.strip() for line in f.readlines())
    
    # Проверяем, существует ли пользователь
    if e_user_new not in existing_users:
        # Если нет, добавляем его в файл
        with open(USERS_NEW, "a") as f:
            f.write(e_user_new + "\n")

def remove_user_id(user_id):
    """Удаляет ID пользователя из файла."""
    users_ids = get_users_ids()
    if user_id in users_ids:
        users_ids.remove(user_id)
        with open(USERS_FILE, "w") as f:
            f.write("\n".join(map(str, users_ids)))


class BroadcastState(StatesGroup):
    """Состояния для процесса рассылки"""
    waiting_for_message = State()
    waiting_for_confirmation = State()
    select_group = State()
    iluz = State()
    obrashenie= State()
    svaz= State()
    Message_from_human= State()
    Message_from_human2= State()





@dp.message(F.text == '/start')
async def start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в расписание КИТ !Рад тебя видеть!", reply_markup=main_keyboard)
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")




@dp.message(F.text == "Группа")
async def start_grup(message: types.Message, state: FSMContext):
    await message.answer("Введите номер группы:")
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
    await state.set_state(BroadcastState.select_group)





@dp.message(lambda message: str(message.text).startswith('4'),StateFilter(BroadcastState.select_group))
async def process_group(message: types.Message, state: FSMContext):
    a=1
    global group_list
    while True:
        try:
            number_group = df.iloc[a][df.columns[0]]
            number_group=str(number_group)
            if number_group not in group_list:
                group_list.append(number_group)
            a=a+1
        except IndexError as e:
            print("Конец")
            break
    if len(message.text) == 4 and message.text.startswith('4'):
        if message.text in group_list:
            group = message.text
            user_groups[message.from_user.id] = group
            await message.answer(f"Я запомнил твою группу! Теперь выбери, что именно ты хочешь узнать",reply_markup=main_keyboard)
            await state.clear()
        else:
            await message.answer(f"Данной группы нет в расписании,попробуй еще раз :/")
    else:
        await message.answer(f"Введите группу коректно,попробуй еще раз :/")
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
            
@dp.message(F.text == "Назад")
async def start(message: types.Message, state: FSMContext):
    await message.answer('Выбери пункт...', reply_markup=main_keyboard)
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
    await state.clear()



@dp.message(F.text == "Все расписание")
async def process_group(message: types.Message, state: FSMContext):
    await message.answer("Выбери четность недели:",reply_markup=chet_nechet)
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")



@dp.message(F.text == "Общее")
async def process_group(message: types.Message, state: FSMContext):
    group = user_groups.get(message.from_user.id, "Не введена")
    if group == "Не введена":
        await message.answer("Для начала введи группу:")
        if user_id not in user_ids:
            user_ids.append(user_id)
            await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
        await state.set_state(BroadcastState.select_group)
        return

    a=-1 #Номера строк
    b=0 #Номера столбцов
    d=0 #номер дня недели
    q=1 #только 1 раз ввести день недели 
    R_3=""
    j=0
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']
    day = days[d]
    
    x = 0 #Только 1 раз ввести и группу и день недели
    number_group = df.iloc[a][df.columns[1]]
    for i in range(6):
        while j == 0:
            try:
                if {str(number_group)} == {str(group)}:
                    b=b+1
                    R1 = df.iloc[a][df.columns[b]]
                    b=b+2
                    R3 = df.iloc[a][df.columns[b]]
                    R3=str(R3)
                    global days_mapping
                    if {str(R3)} == {'nan'}:   
                            R3 = "чет/неч"
                    if R3 != "чет/неч":
                        R3 = R3[:3]
                    if len(R1) > 2:
                        R1 = R1[:2]
                    if {str(R1)} == {str(day)} :
                        
                        
                        b=b-1
                        R2 = df.iloc[a][df.columns[b]]
                        R2=str(R2)
                        R2=R2[:5]
                        b=b+2
                        R4 = df.iloc[a][df.columns[b]]
                        b=b+1
                        R5 = df.iloc[a][df.columns[b]]
                        if R5.startswith("л."):
                            R5=R5[:4]  # Оставляем первые 4 символа
                        elif R5.startswith("лек"):
                            R5=R5[:3]  # Оставляем первые 3 символа
                        elif R5.startswith("пр"):
                            R5=R5[:2]  # Оставляем первые 2 символа
                        b=b+1
                        R6 = df.iloc[a][df.columns[b]]
                        b=b+1
                        R7 = df.iloc[a][df.columns[b]]
                        R7=str(R7)
                        if R7.startswith("КСК"):  # Проверяем, начинается ли строка с "КСК"
                            R7=R7[:3]
                        R6=str(R6)
                        if R6.startswith("КСК КАИ ОЛИМП"):  # Проверяем, начинается ли строка с "КСК"
                            R6=R6[:13]
                        else:
                            R6=R6[:4]
                        b=b+2
                        R8 = df.iloc[a][df.columns[b]]
                        if x == 0:
                            R1 = days_mapping[R1]
                            R_1=f"➤{R1}\n➤{group}\n\n"
                            x=x+1
                        else:
                            if q==0:
                                R1 = days_mapping[R1]
                                R_1=f"➤{R1}\n"
                                q=q+1

                            else:
                                R_1=''
                        R_2=f"{R_1}➤ <b>{R3}</b> 🕘 <b>{R2}</b>\n<b>{R4}</b>({R5})\n{R6}_{R7}зд.\n{R8}"
                        R_3=f"{R_3}\n{R_2}"
                        b=b-9
                        
                    else:
                        b=b-3
                
                a=a+1
                number_group = df.iloc[a][df.columns[b]] 
            except IndexError as e:
                print("Конец")
                
                j=1 
                q=0
                
                a=-1
        await message.answer(R_3, parse_mode='HTML')   
        d=d+1
        j=0
        R_3=""
        days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']
        try:
            day = days[d]
        except:
            x=x
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")

@dp.message(F.text == 'Отмена',StateFilter(BroadcastState.obrashenie))
async def process_group(message: types.Message, state: FSMContext):
    await message.answer("Действие отменено",reply_markup=main_keyboard)
    await state.clear()


@dp.message(StateFilter(BroadcastState.obrashenie))
async def process_group(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await Bot.send_message(user_id_to_notify, f"@{message.from_user.username}\nID: {user_id}\nОбращение:\n{message.text}")
    await message.answer("Спасибо за обратную связь!",reply_markup=main_keyboard)
    await state.clear()
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")


@dp.message(F.text == "Обратная связь")
async def process_group(message: types.Message, state: FSMContext):
    await message.answer("Мы рады услышать тебя! Оставь свои комментарии,вопросы или отзывы, и мы постараемся ответить как можно скорее",reply_markup=otmena)
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
    await state.set_state(BroadcastState.obrashenie)
@dp.message(F.text == "Нечетная")
@dp.message(F.text == "Четная")
async def process_group(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
    group = user_groups.get(message.from_user.id, "Не введена")
    if group == "Не введена":
        await message.answer("Для начала введи группу:")
        await state.set_state(BroadcastState.select_group)
        return
    a=-1 #Номера строк
    b=0 #Номера столбцов
    d=0 #номер дня недели
    q=1 #только 1 раз ввести день недели 
    R_3=""
    j=0
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']
    day = days[d]
    if message.text == "Четная":
        week_type = "чет"
    else:
        week_type = "неч"
    x = 0 #Только 1 раз ввести и группу и день недели
    number_group = df.iloc[a][df.columns[1]]
    for i in range(6):
        while j == 0:
            try:
                if {str(number_group)} == {str(group)}:
                    b=b+1
                    R1 = df.iloc[a][df.columns[b]]
                    b=b+2
                    R3 = df.iloc[a][df.columns[b]]
                    R3=str(R3)
                    global days_mapping
                    if {str(R3)} == {'nan'}:   
                            R3 = "чет/неч"
                    if R3 != "чет/неч":
                        R3 = R3[:3]
                    if len(R1) > 2:
                        R1 = R1[:2]
                    if {str(R1)} == {str(day)} :
                        
                        if R3 == week_type or R3 == "чет/неч":
                            b=b-1
                            R2 = df.iloc[a][df.columns[b]]
                            R2=str(R2)
                            R2=R2[:5]
                            b=b+2
                            R4 = df.iloc[a][df.columns[b]]
                            b=b+1
                            R5 = df.iloc[a][df.columns[b]]
                            if R5.startswith("л."):
                                R5=R5[:4]  # Оставляем первые 4 символа
                            elif R5.startswith("лек"):
                                R5=R5[:3]  # Оставляем первые 3 символа
                            elif R5.startswith("пр"):
                                R5=R5[:2]  # Оставляем первые 2 символа
                            b=b+1
                            R6 = df.iloc[a][df.columns[b]]
                            b=b+1
                            R7 = df.iloc[a][df.columns[b]]
                            R7=str(R7)
                            if R7.startswith("КСК"):  # Проверяем, начинается ли строка с "КСК"
                                R7=R7[:3]
                            R6=str(R6)
                            if R6.startswith("КСК КАИ ОЛИМП"):  # Проверяем, начинается ли строка с "КСК"
                                R6=R6[:13]
                            else:
                                R6=R6[:4]
                            b=b+2
                            R8 = df.iloc[a][df.columns[b]]
                            if x == 0:
                                R1 = days_mapping[R1]
                                R_1=f"➤{R1}\n➤{group}\n\n"
                                x=x+1
                            else:
                                if q==0:
                                    R1 = days_mapping[R1]
                                    R_1=f"➤{R1}\n"
                                    q=q+1

                                else:
                                    R_1=''
                            R_2=f"{R_1}➤ <b>{R3}</b> 🕘 <b>{R2}</b>\n<b>{R4}</b>({R5})\n{R6}_{R7}зд.\n{R8}"
                            R_3=f"{R_3}\n{R_2}"
                            b=b-9
                        else:
                            b=b-3
                    else:
                        b=b-3
                
                a=a+1
                number_group = df.iloc[a][df.columns[b]] 
            except IndexError as e:
                print("Конец")
                print(week_type)
                j=1 
                q=0
                
                a=-1
        await message.answer(R_3, parse_mode='HTML')   
        d=d+1
        j=0
        R_3=""
        days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']
        try:
            day = days[d]
        except:
            x=x
@dp.message(F.text == "День недели")
async def process_group(message: types.Message, state: FSMContext):
    await message.answer("Выберите день недели",reply_markup=days_of_week_keyboard)
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")

@dp.message(F.text == "Iluz")
@dp.message(F.text == "iluz")
async def process_group(message: types.Message, state: FSMContext):
        if message.from_user.id == 963729102 or message.from_user.id == 1624096187:
            await message.answer("Добро пожаловать в ADMIN панель",reply_markup=admin_panel)

@dp.message(F.text == 'Сообщение пользователю')
async def start(message: types.Message, state: FSMContext):
    if message.from_user.id == 963729102 or message.from_user.id == 1624096187:
        await message.answer("Введи ID пользователя")
        await state.set_state(BroadcastState.Message_from_human)

@dp.message(StateFilter(BroadcastState.Message_from_human))
async def start(message: types.Message, state: FSMContext):
    global id_pip
    id_pip=message.text
    await message.answer("Введи текст который хочешь отправить пользователю")
    await state.clear()
    await state.set_state(BroadcastState.Message_from_human2)

@dp.message(StateFilter(BroadcastState.Message_from_human2))
async def start(message: types.Message, state: FSMContext):
    try:
        await Bot.send_message(id_pip, f"Сообщение от Администратора:\n{message.text}")
        await message.answer("Сообщение отправленно")
        await state.clear()
    except:
        await message.answer("Ошибка")
        await state.clear()

async def send_message_to_user(user_id, message):
    """Отправляет сообщение пользователю."""
    try:
        if message.text:
            await Bot.send_message(user_id, message.text)
        elif message.photo:
            if message.caption:
                await Bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            else:
                await Bot.send_photo(user_id, message.photo[-1].file_id)
        elif message.video:
            if message.caption:
                await Bot.send_video(user_id, message.video.file_id, caption=message.caption)
            else:
                await Bot.send_video(user_id, message.video.file_id)
        elif message.voice:
            await Bot.send_voice(user_id, message.voice.file_id)
        elif message.document:
            if message.caption:
                await Bot.send_document(user_id, message.document.file_id, caption=message.caption)
            else:
                await Bot.send_document(user_id, message.document.file_id)
        else:
            await Bot.send_message(user_id, 'Данный тип сообщений не поддерживается')

    except TelegramForbiddenError:
        logging.info(f"Пользователь {user_id} заблокировал бота.")
        remove_user_id(user_id)  # Удаляем заблокировавшего пользователя
    except TelegramBadRequest as e:
        logging.error(f"Ошибка отправки пользователю {user_id}: {e}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка при отправке пользователю {user_id}: {e}")


async def broadcast_message(message: types.Message, state: FSMContext, bot_message):
    """Рассылает сообщение всем пользователям"""
    await message.answer("Начинаю рассылку...")
    users_ids = get_users_ids()
    for user_id in users_ids:
        await send_message_to_user(user_id, bot_message)
        await asyncio.sleep(0.2)  # Задержка что бы не заблочили бота
    await message.answer("Рассылка завершена!")


@dp.message(F.text == "Рассылка")
async def start_broadcast_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /send_broadcast"""
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Отправьте мне сообщение, которое вы хотите разослать пользователям:")
    await state.set_state(BroadcastState.waiting_for_message)  # Переключаем бота в состояние ожидания сообщения для рассылки
@dp.message(StateFilter(BroadcastState.waiting_for_message))
async def get_broadcast_message_handler(message: types.Message, state: FSMContext):
    """Получение сообщения для рассылки"""
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(message_to_broadcast=message)  # Сохраняем сообщение
    await message.answer(
        f"Вы хотите отправить следующее сообщение пользователям:\n{message.text if message.text else 'Фото или другой тип сообщения'}\n\nНажмите /confirm для подтверждения или отправьте другое сообщение, чтобы изменить")
    await state.set_state(BroadcastState.waiting_for_confirmation)  # Переключаем бота в состояние ожидания подтверждения


@dp.message(Command("confirm"), StateFilter(BroadcastState.waiting_for_confirmation))
async def confirm_broadcast_handler(message: types.Message, state: FSMContext):
    """Обработка подтверждения рассылки"""
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    message_to_broadcast = data.get("message_to_broadcast")
    await broadcast_message(message, state, message_to_broadcast)  # Вызываем функцию рассылки
    await state.clear()  # Очищаем состояние

@dp.message(lambda message: message.text == "Поменять файл")
async def process_change_file(message: types.Message, state: FSMContext):
    if message.from_user.id == 963729102 or message.from_user.id == 1624096187:
        global waiting_for_file
        if not waiting_for_file:
            waiting_for_file = 1
            await message.reply("Пожалуйста, отправьте файл.")
            await state.set_state(BroadcastState.iluz)
        else:
            await message.reply("Вы уже находитесь в процессе изменения файла. Пожалуйста, отправьте файл.")


@dp.message(F.content_type.in_({'document', 'file', 'video', 'video_note', 'audio'}),StateFilter(BroadcastState.iluz))
async def handle_file(message: types.Message, state: FSMContext):
    if message.from_user.id == 963729102 or message.from_user.id == 1624096187:
        global waiting_for_file
        global file_path
        global df

        if waiting_for_file == 1:
            # Получаем документ
            document = message.document  
            file_id = document.file_id

            # Получаем файл
            file = await Bot.get_file(file_id)

            # Создаем имя файла с указанным путем
            file_path = 'file.xlsx'  # Указываем путь для сохранения файла

            # Загружаем файл
            await Bot.download_file(file.file_path, file_path)

            # Предполагаем, что файл Excel корректный и загружаем его
            try:
                df = pd.read_excel(file_path)
                await message.reply("Файл успешно сохранён как 'file.xlsx'.")
                waiting_for_file = 0
                await state.clear()
            except Exception as e:
                await message.reply(f"Ошибка при чтении файла: {e}")
                waiting_for_file = 0
                await state.clear()

@dp.message(F.text == "id учасников")
async def process_group(message: types.Message, state: FSMContext):
    if message.from_user.id == 963729102 or message.from_user.id == 1624096187:
        USERS_FILE = "users.txt"
        USERS_NEW = "user_new.txt"  # Укажите путь к вашему текстовому файлу
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as file:
                file_content = file.read()

            await message.answer(file_content)
        if os.path.exists(USERS_NEW):
            with open(USERS_NEW, 'r', encoding='utf-8') as file:
                file_content = file.read()

            await message.answer(file_content)
    else:
        await message.answer("Файл не найден.")

@dp.message(F.text == "Преподаватели")
async def process_group(message: types.Message, state: FSMContext):
    group = user_groups.get(message.from_user.id, "Не введена")
    if group == "Не введена":
        await message.answer("Для начала введи группу:")
        await state.set_state(BroadcastState.select_group)
        return
    a=-1 #Номера строк
    b=0 #Номера 
    Type_spis=[]
    prepod_spis=[]
    para_spis=[]
    anser=f"➤Преподаватели\n"
    Rw_spis=[]
    h=[] #тест
    number_group = df.iloc[a][df.columns[b]]
    while True:
        try:
            number_group = df.iloc[a][df.columns[b]]
            if {str(number_group)} == {str(group)}:
                b=b+4
                para = df.iloc[a][df.columns[b]]
                b=b+1
                type = df.iloc[a][df.columns[b]]
                if type.startswith("л."):
                    type=type[:4]  # Оставляем первые 4 символа
                elif type.startswith("лек"):
                    type=type[:3]  # Оставляем первые 3 символа
                elif type.startswith("пр"):
                    type=type[:2]  
                para_spis.append(para)
                b=b+4
                prepod = df.iloc[a][df.columns[b]]
                prepod = ' '.join(word.capitalize() for word in prepod.lower().split())
                Rw=f"▎• <b>{para}({type})</b>\n   {prepod}\n"
                if str(Rw) not in Rw_spis:
                    Rw_spis.append(str(Rw))
                    Rw=str(Rw)
                    h.append(Rw)
                    
                b=b-9
                
            a=a+1
                 
        except IndexError as e:
            print("Конец")
            break 
    sorted_h = sorted(h, key=lambda x: x[1:])
    sorted_h = [anser] + sorted_h
    first_sorted_h = sorted_h[:25]
    second_sorted_h = sorted_h[25:]
    first_sorted_h = '\n'.join(first_sorted_h)
    second_sorted_h = '\n'.join(second_sorted_h)
    await message.answer(first_sorted_h, parse_mode='HTML')
    await message.answer(second_sorted_h, parse_mode='HTML')
@dp.message(F.text == "Какая неделя")
async def process_group(message: types.Message, state: FSMContext):
    start_date = datetime(2025, 1, 20)
    time_shift = timedelta(hours=3)
    today = datetime.now() + time_shift
    weeks_difference = (today - start_date).days // 7
    if today < start_date:
        week_type = "неделя не определена до 20.01.2025"
    else:
        week_type = "Четная" if weeks_difference % 2 == 0 else "Нечетная"
    await message.answer(week_type)
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")

@dp.message(F.text == "Завтра")
@dp.message(F.text == "Сегодня")
async def process_group(message: types.Message, state: FSMContext):
    group = user_groups.get(message.from_user.id, "Не введена")
    if group == "Не введена":
        await message.answer("Для начала введи группу:")
        await state.set_state(BroadcastState.select_group)
        return
    if message.text == "Сегодня":
        dayss=0
    elif message.text == "Завтра":
        dayss=1
    group = user_groups.get(message.from_user.id, "Не введена")

    a=-1 #Номера строк
    b=0 #Номера столбцов
    d=0 #номер дня недели
    q=1 #только 1 раз ввести день недели 
    R_3=""

    moscow_tz = pytz.timezone('Europe/Moscow')
    today = datetime.now(moscow_tz)
    tomorrow = today + timedelta(0)
    
    day_of_week = tomorrow.weekday()
    
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    t_day = days[day_of_week]
    tomorrow = today + timedelta(dayss)
    day_of_week = tomorrow.weekday()
    
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    day = days[day_of_week]
    if day == "вс":
        await message.answer("Выходной получается")
    else:
        number_group = df.iloc[a][df.columns[1]]
        start_date = datetime(2025, 1, 20)
        time_shift = timedelta(hours=3)
        today = datetime.now() + time_shift
        weeks_difference = (today - start_date).days // 7
        if today < start_date:
            week_type = "неделя не определена до 20.01.2025"
        else:
            week_type = "чет" if weeks_difference % 2 == 0 else "неч"
        
        x = 0
        a=-1
        b=0
        a=-1 #Номера строк
        if message.text == "Завтра" and t_day == "вс":
            if week_type == "чет":
                week_type = "неч"
            else:
                week_type = "чет"
        number_group = df.iloc[a][df.columns[1]]
        while True:
            try:
                if {str(number_group)} == {str(group)}:
                    b=b+1
                    R1 = df.iloc[a][df.columns[b]]
                    b=b+2
                    R3 = df.iloc[a][df.columns[b]]
                    R3=str(R3)
                    global days_mapping
                    if {str(R3)} == {'nan'}:   
                            R3 = "чет/неч"
                    if R3 != "чет/неч":
                        R3 = R3[:3]
                    if len(R1) > 2:
                        R1 = R1[:2]
                    if {str(R1)} == {str(day)} :
                        
                        if R3 == week_type or R3 == "чет/неч":
                            b=b-1
                            R2 = df.iloc[a][df.columns[b]]
                            R2=str(R2)
                            R2=R2[:5]
                            b=b+2
                            R4 = df.iloc[a][df.columns[b]]
                            b=b+1
                            R5 = df.iloc[a][df.columns[b]]
                            if R5.startswith("л."):
                                R5=R5[:4]  # Оставляем первые 4 символа
                            elif R5.startswith("лек"):
                                R5=R5[:3]  # Оставляем первые 3 символа
                            elif R5.startswith("пр"):
                                R5=R5[:2]  # Оставляем первые 2 символа
                            b=b+1
                            R6 = df.iloc[a][df.columns[b]]
                            b=b+1
                            R7 = df.iloc[a][df.columns[b]]
                            R7=str(R7)
                            if R7.startswith("КСК"):  # Проверяем, начинается ли строка с "КСК"
                                R7=R7[:3]
                            R6=str(R6)
                            if R6.startswith("КСК КАИ ОЛИМП"):  # Проверяем, начинается ли строка с "КСК"
                                R6=R6[:13]
                            else:
                                R6=R6[:4]
                            b=b+2
                            R8 = df.iloc[a][df.columns[b]]
                            if x == 0:
                                R1 = days_mapping[R1]
                                R_1=f"➤{R1}\n➤{group}\n\n"
                                x=x+1
                            else:
                                if q==0:
                                    R1 = days_mapping[R1]
                                    R_1=f"➤{R1}"
                                else:
                                    R_1=''
                            R_2=f"{R_1}➤ <b>{R3}</b> 🕘 <b>{R2}</b>\n<b>{R4}</b>({R5})\n{R6}_{R7}зд.\n{R8}"
                            R_3=f"{R_3}\n{R_2}"
                            b=b-9
                        else:
                            b=b-3
                    else:
                        b=b-3
                
                a=a+1
                number_group = df.iloc[a][df.columns[b]] 
            except IndexError as e:
                print("Конец")
                print(week_type)
                break 
                x = 0
        await message.answer(R_3, parse_mode='HTML')
        user_id = message.from_user.id
        e_user_new=f"@{message.from_user.username} ID: {user_id}"
        save_user_new(e_user_new)
        save_user_id(user_id)
        if user_id not in user_ids:
            user_ids.append(user_id)
            await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")


@dp.message(lambda message: message.text in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'])
async def process_group(message: types.Message, state: FSMContext):
    group = user_groups.get(message.from_user.id, "Не введена")
    if group == "Не введена":
        await message.answer("Для начала введи группу:")
        await state.set_state(BroadcastState.select_group)
        return
    global day
    # Обновляем переменную day в зависимости от нажатой кнопки
    if message.text == 'Понедельник':
        day = 'пн'
    elif message.text == 'Вторник':
        day = 'вт'
    elif message.text == 'Среда':
        day = 'ср'
    elif message.text == 'Четверг':
        day = 'чт'
    elif message.text == 'Пятница':
        day = 'пт'
    elif message.text == 'Суббота':
        day = 'сб'
    group = user_groups.get(message.from_user.id, "Не введена")
    a = 0
    b = 0
    time_shift = timedelta(hours=3)
    today = datetime.now() + time_shift
    number_group = df.iloc[a][df.columns[1]]
    start_date = datetime(2025, 1, 20)
    a=-1 #Номера строк
    b=0 #Номера столбцов
    d=0 #номер дня недели
    q=1 #только 1 раз ввести день недели 
    R_3=""
    weeks_difference = (today - start_date).days // 7
    if today < start_date:
        week_type = "неделя не определена до 20.01.2025"
    else:
        week_type = "чет" if weeks_difference % 2 == 0 else "неч"
    x = 0
    a=-1
    b=0
    number_group = df.iloc[a][df.columns[1]]

    while True:
            try:
                if {str(number_group)} == {str(group)}:
                    b=b+1
                    R1 = df.iloc[a][df.columns[b]]
                    b=b+2
                    R3 = df.iloc[a][df.columns[b]]
                    R3=str(R3)
                    global days_mapping
                    if {str(R3)} == {'nan'}:   
                            R3 = "чет/неч"
                    if R3 != "чет/неч":
                        R3 = R3[:3]
                    if len(R1) > 2:
                        R1 = R1[:2]
                    if {str(R1)} == {str(day)} :
                        
                        if R3 == week_type or R3 == "чет/неч":
                            b=b-1
                            R2 = df.iloc[a][df.columns[b]]
                            R2=str(R2)
                            R2=R2[:5]
                            b=b+2
                            R4 = df.iloc[a][df.columns[b]]
                            b=b+1
                            R5 = df.iloc[a][df.columns[b]]
                            if R5.startswith("л."):
                                R5=R5[:4]  # Оставляем первые 4 символа
                            elif R5.startswith("лек"):
                                R5=R5[:3]  # Оставляем первые 3 символа
                            elif R5.startswith("пр"):
                                R5=R5[:2]  # Оставляем первые 2 символа
                            b=b+1
                            R6 = df.iloc[a][df.columns[b]]
                            b=b+1
                            R7 = df.iloc[a][df.columns[b]]
                            R7=str(R7)
                            if R7.startswith("КСК"):  # Проверяем, начинается ли строка с "КСК"
                                R7=R7[:3]
                            R6=str(R6)
                            if R6.startswith("КСК КАИ ОЛИМП"):  # Проверяем, начинается ли строка с "КСК"
                                R6=R6[:13]
                            else:
                                R6=R6[:4]
                            b=b+2
                            R8 = df.iloc[a][df.columns[b]]
                            if x == 0:
                                R1 = days_mapping[R1]
                                R_1=f"➤{R1}\n➤{group}\n\n"
                                x=x+1
                            else:
                                if q==0:
                                    R1 = days_mapping[R1]
                                    R_1=f"➤{R1}"
                                else:
                                    R_1=''
                            R_2=f"{R_1}➤ <b>{R3}</b> 🕘 <b>{R2}</b>\n<b>{R4}</b>({R5})\n{R6}_{R7}зд.\n{R8}"
                            R_3=f"{R_3}\n{R_2}"
                            b=b-9
                        else:
                            b=b-3
                    else:
                        b=b-3
                
                a=a+1
                number_group = df.iloc[a][df.columns[b]] 
            except IndexError as e:
                print("Конец")
                print(week_type)
                break 
                x = 0
    await message.answer(R_3, parse_mode='HTML')
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")

@dp.message()
async def process_group(message: types.Message):
    await message.answer("Не понимаю тебя, напиши /start")
    user_id = message.from_user.id
    e_user_new=f"@{message.from_user.username} ID: {user_id}"
    save_user_new(e_user_new)
    save_user_id(user_id)
    if user_id not in user_ids:
        user_ids.append(user_id)
        await Bot.send_message(user_id_to_notify, f"Зарегистрирован @{message.from_user.username}\nID: {user_id}")
   

    

async def main():
    await dp.start_polling(Bot)

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print ('Бот выключен')

