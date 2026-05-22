import os

# Получаем абсолютный путь к папке, где лежит этот файл конфигурации
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Секретный ключ для защиты форм от CSRF-атак
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-secret-key-12345'
    
    # ПОДКЛЮЧЕНИЕ К POSTGRESQL (вместо SQLite)
    # Формат: postgresql://логин:пароль@хост:порт/имя_базы
    # Обязательно замените 'ВАШ_ПАРОЛЬ' на реальный пароль от вашего pgAdmin!
    # И проверьте имя базы данных в конце (например, 'habez_db')
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = _db_url or \
        'postgresql://postgres:postgres@localhost:5432/habez_db?client_encoding=utf8'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False