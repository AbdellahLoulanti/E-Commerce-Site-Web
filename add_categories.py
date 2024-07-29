from app import app, db
from app.models import Category

def add_categories():
    categories = ['Tshirt', 'Shoes', 'Pants', 'Perfumes', 'Accessories']
    for name in categories:
        # Vérifiez si la catégorie existe déjà pour éviter les doublons
        existing_category = Category.query.filter_by(name=name).first()
        if not existing_category:
            category = Category(name=name)
            db.session.add(category)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        add_categories()
