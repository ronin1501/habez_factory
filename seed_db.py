from app import create_app, db
from app.models import Document

app = create_app()

with app.app_context():
    # Теперь это сработает, так как мы добавили поле description в модель
    doc1 = Document(
        title="ГОСТ 31358-2007", 
        category="ГОСТ", 
        file_path="docs/gost.pdf", 
        description="Смеси строительные на гипсовом вяжущем"
    )
    
    db.session.add(doc1)
    db.session.commit()
    print("Данные успешно добавлены!")