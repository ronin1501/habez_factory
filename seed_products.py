# seed_products.py
from app import create_app, db
from app.models import Category, Product

app = create_app()

with app.app_context():
    # 1. Ищем или создаем категорию гипсокартона
    category = Category.query.filter(
        (Category.slug == 'gipsokarton') | (Category.name.ilike('%Гипсокартон%'))
    ).first()

    if not category:
        category = Category(name="Гипсокартон (ГКЛ)", slug="gipsokarton")
        db.session.add(category)
        db.session.commit()
        print(f"Создана новая категория: {category.name} с ID: {category.id}")

    # 2. Добавляем товары с обязательным полем SKU (артикул)
    existing_products = Product.query.filter_by(category_id=category.id).count()
    if existing_products == 0:
        p1 = Product(
            name="Гипсокартон (8 мм) 8,0х1200х2500",
            sku="GKL-8-2500",  # Добавили обязательный артикул!
            description="Гипсокартонный лист – популярный конструкционный материал. Состоит из гипсового сердечника, обернутого слоем специального картона. Экологичный и универсальный материал для ненагружаемых декоративных элементов.",
            price=76.00,
            weight=20.0,
            category_id=category.id,
            image_file="gkl_8mm.jpg" # Имя картинки
        )
        p2 = Product(
            name="Гипсокартон стандартный (12,5 мм) 12,5х1200х2500",
            sku="GKL-12-2500",
            description="Обычный лист гипсокартона, который используется в нормальных условиях влажности и имеет класс пожарной безопасности КМ2. Строительные и отделочные материалы по ценам заводов.",
            price=81.00,
            weight=29.0,
            category_id=category.id,
            image_file="gkl_12_5_2500.jpg"
        )
        p3 = Product(
            name="Гипсокартон удлиненный (12,5 мм) 12,5х1200х3000",
            sku="GKL-12-3000",
            description="Влагостойкий лист гипсокартона (ГКЛВ). Характеристики листа позволяют использовать его в помещениях с повышенной влажностью – ванных комнатах, душевых, кухнях.",
            price=84.40,
            weight=35.0,
            category_id=category.id,
            image_file="gkl_12_5_3000.jpg"
        )

        db.session.add_all([p1, p2, p3])
        db.session.commit()
        print("Успешно добавлено 3 вида гипсокартона в базу данных!")
    else:
        print(f"В этой категории уже есть товары ({existing_products} шт.).")