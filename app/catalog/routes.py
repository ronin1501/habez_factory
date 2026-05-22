from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user
from decimal import Decimal
from app import db
from app.models import Category, Product, Warehouse, Stock, CalculatorNorm, Order, OrderItem, User, Profile

# Импортируем catalog_bp строго после моделей, 
# чтобы избежать циклической блокировки (circular import)
from app.catalog import catalog_bp

@catalog_bp.route('/')
@catalog_bp.route('/category/<int:category_id>')
def catalog(category_id=None):
    """Каталог продукции с гарантированной нормализацией ID категорий"""
    categories = Category.query.all()
    category_slug = request.args.get('category')
    
    selected_category = None

    # Сценарий 1: Переход по ID категории (из шаблона /catalog/category/<id>)
    if category_id is not None:
        selected_category = Category.query.get(category_id)

    # Сценарий 2: Переход по текстовому GET-параметру (?category=gipsokarton)
    elif category_slug:
        slug_clean = category_slug.strip().lower()
        # 1. Пробуем найти точное совпадение по slug
        selected_category = Category.query.filter_by(slug=slug_clean).first()
        
        # 2. Резерв: ищем частичное совпадение по slug (без учета регистра)
        if not selected_category:
            selected_category = Category.query.filter(Category.slug.ilike(f'%{slug_clean}%')).first()
            
        # 3. Супер-резерв: ищем совпадение по русскому названию в БД ("гипс", "картон")
        if not selected_category:
            selected_category = Category.query.filter(Category.name.ilike(f'%{slug_clean}%')).first()

    # Финальная обработка выбранной категории
    if selected_category:
        products = Product.query.filter_by(category_id=selected_category.id).all()
        # ВАЖНО: Всегда делаем current_category числовым ID, чтобы не ломать логику шаблонов
        current_category = selected_category.id
        
        # Если категория создана, но товаров в ней нет — подстраховываемся и берем все товары
        if not products:
            products = Product.query.all()
    else:
        # Если категория не определена/не найдена — выводим все товары завода
        products = Product.query.all()
        current_category = None

    # --- ОРГАНИЗАЦИЯ ТЕСТОВОГО ВЫВОДА В КОНСОЛЬ VS CODE ---
    print("\n" + "="*50)
    print(f"DEBUG ТЕРМИНАЛА ДЛЯ ВКР:")
    print(f"-> Всего категорий в вашей базе данных SQLite: {len(categories)}")
    print(f"-> Запрошенный слаг/ID: category_id={category_id}, slug='{category_slug}'")
    if selected_category:
        print(f"-> Успешно определена категория: ID={selected_category.id}, Название='{selected_category.name}'")
    else:
        print("-> Категория НЕ определена (отображается общий каталог)")
    print(f"-> Количество продуктов, отправленных на страницу: {len(products)}")
    print("="*50 + "\n")
    # ------------------------------------------------------
        
    return render_template(
        'catalog/catalog.html', 
        title='Каталог продукции', 
        products=products, 
        categories=categories, 
        current_category=current_category
    )

@catalog_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Детальная страница стройматериала с калькулятором расхода"""
    product = Product.query.get_or_404(product_id)
    norms = CalculatorNorm.query.filter_by(product_id=product.id).all()
    return render_template('catalog/product.html', product=product, norms=norms)

@catalog_bp.route('/calculate_consumption', methods=['POST'])
def calculate_consumption():
    """API-эндпоинт для мгновенного AJAX-расчета расхода смеси на базе данных из таблицы CalculatorNorm"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Неверные данные'}), 400
        
    product_id = data.get('product_id')
    surface_type = data.get('surface_type')
    area = float(data.get('area', 0))
    thickness = float(data.get('thickness', 10))
    
    product = Product.query.get_or_404(product_id)
    
    norm = CalculatorNorm.query.filter_by(product_id=product_id, surface_type=surface_type).first()
    if not norm:
        # Если норматива в БД нет, используем средний расход для сухих смесей (например, 9.0 кг на 1 кв.м при толщине 10 мм)
        if product.category and product.category.slug in ['gipsokarton', 'plity']:
            # Расчет плит (1 плита ~ 0.33 кв.м)
            total_kg = product.weight * (area / 0.33)
            bags_needed = int(-(-total_kg // product.weight)) if product.weight > 0 else 1
        elif product.category and product.category.slug == 'profil':
            # Округляем по площади
            total_kg = product.weight * area
            bags_needed = int(-(-area // 3)) # профили обычно по 3 метра
        else:
            consumption_per_sqm = 9.0 # кг при 10 мм
            total_kg = consumption_per_sqm * area * (thickness / 10.0)
            bags_needed = int(-(-total_kg // product.weight)) if product.weight > 0 else 1
    else:
        total_kg = norm.consumption_per_sqm * area * (thickness / 10.0)
        bags_needed = int(-(-total_kg // product.weight)) if product.weight > 0 else 1
    
    return jsonify({
        'total_weight_kg': round(total_kg, 2),
        'bags_needed': max(1, bags_needed)
    })

@catalog_bp.route('/warehouses')
@login_required
def warehouses_availability():
    """Остатки продукции на складах. Доступно только дилерам"""
    warehouses = Warehouse.query.all()
    stocks = Stock.query.all()
    products = Product.query.all()
    return render_template('catalog/warehouses.html', title='Остатки на складах', 
                          warehouses=warehouses, products=products, stocks=stocks)

@catalog_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Добавление товара в корзину (в сессию)"""
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'error': 'Не указан ID товара'}), 400

    product = Product.query.get_or_404(product_id)
    
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    prod_id_str = str(product_id)
    
    if prod_id_str in cart:
        cart[prod_id_str] += quantity
    else:
        cart[prod_id_str] = quantity

    session['cart'] = cart
    session.modified = True
    
    return jsonify({
        'success': True,
        'cart_count': sum(cart.values())
    })

@catalog_bp.route('/cart', methods=['GET'])
def view_cart():
    """Просмотр корзины с расчетом суммы"""
    cart = session.get('cart', {})
    cart_items = []
    total_price = Decimal('0.00')

    for prod_id_str, qty in cart.items():
        product = Product.query.get(int(prod_id_str))
        if product:
            item_total = product.price * qty
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': qty,
                'total': item_total
            })

    return render_template('catalog/cart.html', title='Корзина', 
                          cart_items=cart_items, total_price=total_price)

@catalog_bp.route('/cart/update', methods=['POST'])
def update_cart():
    """Обновление количества товара в корзине"""
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if 'cart' in session and product_id in session['cart']:
        if quantity <= 0:
            session['cart'].pop(product_id)
        else:
            session['cart'][product_id] = quantity
        session.modified = True

    return redirect(url_for('catalog.view_cart'))

@catalog_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Удаление товара из корзины"""
    if 'cart' in session:
        session['cart'].pop(str(product_id), None)
        session.modified = True
    flash('Товар удален из корзины', 'info')
    return redirect(url_for('catalog.view_cart'))

@catalog_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Очистка корзины"""
    session.pop('cart', None)
    flash('Корзина очищена', 'info')
    return redirect(url_for('catalog.view_cart'))

@catalog_bp.route('/order', methods=['GET', 'POST'])
def create_order():
    """Оформление заказа из корзины"""
    cart = session.get('cart', {})
    if not cart:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('catalog.catalog'))

    cart_items = []
    total_price = Decimal('0.00')
    for prod_id_str, qty in cart.items():
        product = Product.query.get(int(prod_id_str))
        if product:
            item_total = product.price * qty
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': qty,
                'total': item_total
            })

    if request.method == 'POST':
        delivery_type = request.form.get('delivery_type', 'Самовывоз')
        delivery_address = request.form.get('delivery_address', '')
        
        # Если пользователь не авторизован, автоматически регистрируем его как гостя
        if not current_user.is_authenticated:
            fio = request.form.get('fio', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()

            if not email or not phone or not fio:
                flash('Пожалуйста, заполните все контактные поля для оформления заказа', 'danger')
                return render_template('catalog/order.html', title='Оформление заказа', 
                                      cart_items=cart_items, total_price=total_price)

            # Проверяем, существует ли уже пользователь с таким email
            user = User.query.filter_by(email=email).first()
            if not user:
                import uuid
                # Генерируем случайный пароль для гостя
                guest_password = str(uuid.uuid4())[:8]
                user = User(email=email, phone=phone, role_id=3)  # Назначаем роль Dealer (id=3)
                user.set_password(guest_password)
                db.session.add(user)
                db.session.flush()

                # Создаем профиль гостя
                profile = Profile(
                    user_id=user.id,
                    company_name=fio,
                    inn="0000000000",
                    kpp="",
                    legal_address=""
                )
                db.session.add(profile)
                db.session.commit()
                flash(f'Для вас автоматически создан личный кабинет! Email: {email}, Временный пароль: {guest_password}', 'info')
            
            # Авторизуем пользователя
            login_user(user)

        # Создаем заказ
        order = Order(
            user_id=current_user.id,
            status_id=1,  # В обработке
            total_price=total_price,
            delivery_type=delivery_type,
            delivery_address=delivery_address if delivery_type == 'Доставка' else 'Самовывоз со склада'
        )
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price_at_purchase=item['product'].price
            )
            db.session.add(order_item)

        db.session.commit()
        session.pop('cart', None)  # Очищаем корзину
        flash(f'Заказ №{order.id} успешно оформлен! Наш менеджер свяжется с вами.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('catalog/order.html', title='Оформление заказа', 
                          cart_items=cart_items, total_price=total_price)