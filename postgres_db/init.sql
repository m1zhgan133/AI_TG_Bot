-- Файл init.sql выполняется автоматически при первом запуске контейнера PostgreSQL
-- Все SQL команды в этом файле выполняются в порядке их написания

-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    yandex_email VARCHAR(100),
    yandex_password VARCHAR(100),
    yandex_calendar_link VARCHAR(200)
);

-- Создание таблицы scheduled_messages
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE
);

-- Создание индексов для оптимизации запросов
--CREATE INDEX IF NOT EXISTS idx_scheduled_messages_user_id ON scheduled_messages(user_id);
--CREATE INDEX IF NOT EXISTS idx_scheduled_messages_scheduled_time ON scheduled_messages(scheduled_time);
