from flask import Blueprint

# Создаем блюпринт с именем catalog_bp
catalog_bp = Blueprint('catalog', __name__)

# Импортируем маршруты в самом конце
from app.catalog import routes