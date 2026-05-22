from flask import render_template
from app.main import main_bp
from app.models import Document, Product

@main_bp.route('/')
@main_bp.route('/index')
def index():
    featured_products = Product.query.limit(3).all()
    return render_template('main/index.html', title='Главная', products=featured_products)

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title='О производстве')

@main_bp.route('/documents')
def documents():
    docs = Document.query.order_by(Document.upload_date.desc()).all()
    return render_template('main/documents.html', title='Сертификаты и ГОСТы', documents=docs)