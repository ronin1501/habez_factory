from flask import Blueprint

# Создаем блюпринт с именем auth_bp
auth_bp = Blueprint('auth', __name__)

# Загружаем маршруты в самом конце
from app.auth import routes