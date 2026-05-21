import asyncio
import requests
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from aiogram.types import ReplyKeyboardRemove


TOKEN = 'YOUR_TOKEN'
TOKEN_API = 'YOUR_TOKEN'

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

db = sqlite3.connect('users_db.db')
c = db.cursor()
c.execute(""" CREATE TABLE IF NOT EXISTS users (
    id INTEGER,
    city text
)         
""")

db.commit()
db.close()

db = sqlite3.connect('otkaz.db')
c = db.cursor()
c.execute(""" CREATE TABLE IF NOT EXISTS otkaz (
    id INTEGER
)    
""")
db.commit()
db.close()


location_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Текущая погода 🌤️"),
            types.KeyboardButton(text="Отказаться от рассылки 🔕")],
        [
            types.KeyboardButton(text="Изменить город ✏️")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

return_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Текущая погода 🌤️"),
            types.KeyboardButton(text="Снова подписаться на рассылку 🔄")],
        [
            types.KeyboardButton(text="Изменить город ✏️")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

city_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text='Санкт-Петербург 🏛️'),
         types.KeyboardButton(text='Москва 🏰')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


@dp.message(Command('delalluser'))
async def del_user(message: types.Message):
    db = sqlite3.connect('users_db.db')
    c = db.cursor()
    c.execute("DELETE FROM users")
    db2 = sqlite3.connect('otkaz.db')
    c2 = db2.cursor()
    c2.execute("DELETE FROM otkaz")
    await message.answer(f'Успешно, вот док-во:{c.fetchall()},{c2.fetchall()}')
    db2.commit()
    db2.close()
    db.commit()
    db.close()


@dp.message(Command('spisok'))
async def send_spisok(message: types.Message):
    db = sqlite3.connect('users_db.db')
    c = db.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    db2 = sqlite3.connect('otkaz.db')
    c2 = db2.cursor()
    c2.execute("SELECT * FROM otkaz")
    otkaz = c2.fetchall()
    await message.answer(f"Вот актуальные пользователи: {data}, a вот список отказавшихся {otkaz}")
    db2.commit()
    db2.close()
    db.commit()
    db.close()


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("Пожалуйста, введите свой город или выберите из имеющихся 🤗", reply_markup=city_keyboard)


@dp.message(F.text == 'Снова подписаться на рассылку 🔄')
async def again_welcome(message: types.Message):
    db_otkaz = sqlite3.connect('otkaz.db')
    c_otkaz = db_otkaz.cursor()
    c_otkaz.execute(f"DELETE FROM otkaz WHERE id = {message.from_user.id}")
    db_otkaz.commit()
    db_otkaz.close()
    await message.answer("Рады вашему возвращению 🤗", reply_markup=location_keyboard)


@dp.message(F.text == 'Отказаться от рассылки 🔕')
async def stop_project(message: types.Message):
    db_otkaz = sqlite3.connect('otkaz.db')
    c_otkaz = db_otkaz.cursor()
    c_otkaz.execute(f"INSERT INTO otkaz VALUES ({message.from_user.id})")
    db_otkaz.commit()
    db_otkaz.close()
    await message.answer("Вы успешно отказались от рассылки! Очень жаль, что это произошло 🥹, если что, вы всегда можете подписаться на рассылку снова 😌", reply_markup=return_keyboard)


@dp.message(F.text == 'Изменить город ✏️')
async def rechange(message: types.Message):
    id_user = message.from_user.id
    db = sqlite3.connect('users_db.db')
    c = db.cursor()
    c.execute(f"DELETE FROM users WHERE id = {id_user}")
    db.commit()
    db.close()
    await message.answer("Пожалуйста, введите свой город или выберите из имеющихся 🤗", reply_markup=city_keyboard)


@dp.message(F.text == "Текущая погода 🌤️")
async def weather_now(message: types.Message):
    db = sqlite3.connect('users_db.db')
    c = db.cursor()
    id_user = message.from_user.id
    c.execute(f"SELECT id FROM users WHERE id = {id_user}")
    if c.fetchone() != None:
        c.execute(f"SELECT * FROM users WHERE id = {id_user}")
        city_user = c.fetchall()[0][1]
        response = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key={TOKEN_API}&q={city_user}&days=1&lang=ru")
        if response.status_code == 200:
            data = response.json()
            forecast = data["forecast"]["forecastday"][0]["day"]
            rain = []
            for hour in data['forecast']['forecastday'][0]['hour']:
                if hour['will_it_rain'] == 1 and int(hour['time'].split()[1].split(':')[0]) >= 7:
                    rain.append([hour['time'].split()[1],
                                hour['chance_of_rain']])

            rain_second = []
            for t in rain:
                rain_second.append(int(t[0][:2]))
            rain_sorted = sort_time(rain_second)

            soobch = ''
            if rain_sorted:
                for h in rain_sorted:
                    if len(h) == 1:
                        soobch += f'В {h[0]}:00 высокая вероятность дождя 🌧 \n'
                    elif len(h) > 1:
                        soobch += f'C {h[0]}:00 до {h[-1]}:00 высокая вероятность дождя 🌧\n'

            if len(rain) > 0:
                await bot.send_message(id_user, f"Привет! Вот погода в вашем любимом городе, {city_user}: \n"
                                       f"Текущая температура 🌡: {data['current']['temp_c']}°C\n"
                                       f"Максимальная температура ⬆️: {forecast['maxtemp_c']}°C\n"
                                       f"Минимальная температура ⬇️: {forecast['mintemp_c']}°C\n"
                                       f"Вероятность дождя ☔️: {forecast['daily_chance_of_rain']}%\n"
                                       f"\n"
                                       f"{soobch}")
            if len(rain) == 0:
                await bot.send_message(id_user, f"Привет! Вот погода в вашем любимом городе, {city_user}: \n"
                                       f"Текущая температура 🌡: {data['current']['temp_c']}°C\n"
                                       f"Максимальная температура ⬆️: {forecast['maxtemp_c']}°C\n"
                                       f"Минимальная температура ⬇️: {forecast['mintemp_c']}°C\n"
                                       f"Вероятность дождя ☂️: 0%\n")
        elif response.status_code == 400:
            await message.answer('Введите, пожалуйста, существующий город 🙃\n'
                                 'Чтобы изменить город, откажитесь от рассылки и пройдите регистрацию заново 🙌')
    else:
        await message.answer('Сначала зарегистрируйтесь, пожалуйста 🙃')


@dp.message()
async def send_welcome_2(message: types.Message):
    message_from_user = message.text
    if message_from_user == 'Санкт-Петербург 🏛️':
        message_from_user = 'Санкт-Петербург'
    if message_from_user == 'Москва 🏰':
        message_from_user = 'Москва'
    db = sqlite3.connect('users_db.db')
    c = db.cursor()
    id_user = message.from_user.id
    city_user = message_from_user
    c.execute(f"SELECT id FROM users WHERE id = {id_user}")

    db_otkaz = sqlite3.connect('otkaz.db')
    c_otkaz = db_otkaz.cursor()
    c_otkaz.execute("SELECT * FROM otkaz")
    otkaz = []
    for user_id_otkaz in c_otkaz.fetchall():
        otkaz.append(int(str(user_id_otkaz)[1:-2]))

    response = requests.get(
        f"http://api.weatherapi.com/v1/forecast.json?key={TOKEN_API}&q={city_user}&days=1&lang=ru")
    if response.status_code == 200:
        if c.fetchone() is None:
            if response.status_code == 200:
                if id_user not in otkaz:
                    c.execute(
                        f"INSERT INTO users VALUES ({id_user},'{city_user}')")
                    await message.answer('Супер, вы подписались на ежедневную рассылку погоды в 7:00 😊', reply_markup=location_keyboard)
                elif id_user in otkaz:
                    c.execute(
                        f"INSERT INTO users VALUES ({id_user},'{city_user}')")
                    await message.answer('Супер, вы успешно сменили город 😊', reply_markup=return_keyboard)
        else:
            await message.answer('Пользователь уже подписан на рассылку 😌', reply_markup=location_keyboard)
    elif response.status_code == 400:
        await message.answer('Пожалуйста, введите настоящий город 🤕')
    db_otkaz.commit()
    db_otkaz.close()
    db.commit()
    db.close()


def sort_time(numb):
    result = []
    if numb:
        current_group = [numb[0]]
        for num in numb[1:]:
            if num == current_group[-1]+1:
                current_group.append(num)
            else:
                result.append(current_group)
                current_group = [num]
        result.append(current_group)
        return result


async def project_time():
    db = sqlite3.connect('users_db.db')
    c = db.cursor()
    c.execute("SELECT * FROM users")
    spisok = c.fetchall()
    db_otkaz = sqlite3.connect('otkaz.db')
    c_otkaz = db_otkaz.cursor()
    c_otkaz.execute("SELECT * FROM otkaz")
    otkaz = []
    for user_id_otkaz in c_otkaz.fetchall():
        otkaz.append(int(str(user_id_otkaz)[1:-2]))
    for user in spisok:
        user_id = user[0]
        user_city = user[1]
        if user_id not in otkaz:
            response = requests.get(
                f"http://api.weatherapi.com/v1/forecast.json?key={TOKEN_API}&q={user_city}&days=1&lang=ru")
            data = response.json()
            forecast = data["forecast"]["forecastday"][0]["day"]
            if response.status_code == 200:
                rain = []
                for hour in data['forecast']['forecastday'][0]['hour']:
                    if hour['will_it_rain'] == 1 and int(hour['time'].split()[1].split(':')[0]) >= 7:
                        rain.append([hour['time'].split()[1],
                                    hour['chance_of_rain']])
                rain_second = []
                for t in rain:
                    rain_second.append(int(t[0][:2]))
                rain_sorted = sort_time(rain_second)

                soobch = ''
                if rain_sorted:
                    for h in rain_sorted:
                        if len(h) == 1:
                            soobch += f'В {h[0]}:00 высокая вероятность дождя 🌧 \n'
                        elif len(h) > 1:
                            soobch += f'C {h[0]}:00 до {h[-1]}:00 высокая вероятность дождя 🌧\n'
                if len(rain) > 0:
                    await bot.send_message(user_id, f"Доброе утро 🌕!  \n"
                                           f"Текущая температура 🌡: {data['current']['temp_c']}°C\n"
                                           f"Максимальная температура ⬆️: {forecast['maxtemp_c']}°C\n"
                                           f"Минимальная температура ⬇️: {forecast['mintemp_c']}°C\n"
                                           f"Вероятность дождя ☔️: {forecast['daily_chance_of_rain']}%\n"
                                           f"\n"
                                           f"{soobch}")
                if len(rain) == 0:
                    await bot.send_message(user_id, f"Доброе утро 🌕!\n"
                                           f"Текущая температура 🌡: {data['current']['temp_c']}°C\n"
                                           f"Максимальная температура ⬆️: {forecast['maxtemp_c']}°C\n"
                                           f"Минимальная температура ⬇️: {forecast['mintemp_c']}°C\n"
                                           f"Вероятность дождя ☂️: 0%\n")
    db_otkaz.commit()
    db_otkaz.close()
    db.commit()
    db.close()


scheduler.add_job(
    func=project_time,
    trigger="cron",
    hour=7,
    minute=0,
    timezone=pytz.timezone("Europe/Moscow")
)


# async def error():
#     for user in [(2039042151, 'Санкт-Петербург'), (953748668, 'Санкт-Петербург'), (5213710664, 'Санкт-Петербург'), (921204383, 'Санкт-Петербург')]:
#         await bot.send_message(user[0], 'По техническим причинам бот не работает в течении 30 минут в связи с добавлением нового функционала')


async def main():
    # await error()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
