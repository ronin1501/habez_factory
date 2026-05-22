from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Вспомогательная функция Flask-Login для получения пользователя из БД по ID"""
    return User.query.get(int(user_id))


# ==========================================
# ПРОМЕЖУТОЧНЫЕ ТАБЛИЦЫ ДЛЯ СВЯЗЕЙ MANY-TO-MANY
# ==========================================

product_documents = db.Table('product_documents',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
)


# ==========================================
# МОДУЛЬ 1: ПОЛЬЗОВАТЕЛИ И ДОСТУП
# ==========================================

class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='buyer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    __tablename__ = 'profiles'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(12), unique=True, nullable=False)
    kpp = db.Column(db.String(9), nullable=False)
    legal_address = db.Column(db.Text, nullable=False)
    discount_level = db.Column(db.Float, default=0.0)


# ==========================================
# МОДУЛЬ 2: КАТАЛОГ ПРОДУКЦИИ И СКЛАД
# ==========================================

class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='default_product.jpg')
    
    @property
    def image_url(self):
        if not self.image_file:
            return 'images/products/default_product.png'
        if self.image_file.startswith('images/'):
            return self.image_file
        return f'images/products/{self.image_file}'
    
    documents = db.relationship('Document', secondary=product_documents, backref=db.backref('products', lazy='dynamic'))
    norms = db.relationship('CalculatorNorm', backref='product', lazy=True, cascade="all, delete-orphan")
    stocks = db.relationship('Stock', backref='product', lazy=True, cascade="all, delete-orphan")

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    stocks = db.relationship('Stock', backref='warehouse', lazy=True, cascade="all, delete-orphan")

class Stock(db.Model):
    __tablename__ = 'stocks'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)


# ==========================================
# МОДУЛЬ 3: ДОКУМЕНТАЦИЯ (ИСПРАВЛЕННЫЙ)
# ==========================================

class Document(db.Model):
    __tablename__ = 'documents'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    # ДОБАВЛЕНО: поле, которое вы пытались использовать в скрипте
    description = db.Column(db.String(500), nullable=True) 
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
# ==========================================
# МОДУЛЬ 4: КАЛЬКУЛЯТОР
# ==========================================

class CalculatorNorm(db.Model):
    __tablename__ = 'calculator_norms'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    surface_type = db.Column(db.String(100), nullable=False)
    consumption_per_sqm = db.Column(db.Float, nullable=False)


# ==========================================
# МОДУЛЬ 5: ЗАКАЗЫ
# ==========================================

class OrderStatus(db.Model):
    __tablename__ = 'order_statuses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)
    orders = db.relationship('Order', backref='current_status', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('order_statuses.id'), nullable=False, default=1)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)
    delivery_type = db.Column(db.String(50), nullable=False)
    delivery_address = db.Column(db.Text, nullable=True)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)
    product_info = db.relationship('Product')