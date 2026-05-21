# Weather Notification Telegram Bot 🌤️

An asynchronous Telegram bot that provides real-time weather forecasts and automated morning notifications.

## Features
* **Daily Automated Alerts:** Uses `APScheduler` to send weather updates every morning at 7:00 AM (Moscow time).
* **Smart Rain Tracking:** Parses hourly weather data to group rainy hours together and warns users about high chances of precipitation (e.g., "From 08:00 to 11:00").
* **User Management:** Utilizes `SQLite` databases to manage user subscriptions, location preferences, and opt-out requests.
* **Interactive UI:** Interactive reply keyboards for seamless navigation and changing target cities.

## Tech Stack
* **Language:** Python
* **Framework:** Aiogram 3 (Asynchronous Telegram Bot Framework)
* **Database:** SQLite3
* **Libraries:** Requests (API calls), APScheduler (Task scheduling), Pytz (Timezone handling)
* **API Used:** WeatherAPI.com

## How to Run
1. Clone the repository.
2. Install dependencies: `pip install aiogram requests apscheduler pytz`.
3. Replace `TOKEN` and `TOKEN_API` with your bot token from @BotFather and your WeatherAPI key.
4. Run `python main.py`.
