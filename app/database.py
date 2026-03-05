from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Меняем URL: вместо sqlite используем postgresql
# Формат: postgresql://логин:пароль@хост:порт/название_базы
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5433/soc_db"

# 2. Создаем движок (engine).
# Для Postgres параметр check_same_thread не нужен (это только фишка SQLite)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Настраиваем сессии
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 4. Базовый класс для моделей
Base = declarative_base()