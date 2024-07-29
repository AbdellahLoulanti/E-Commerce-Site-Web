from app import app, db
from app.models import Product, Category

def delete_products():
    # Trouver les catégories Tshirt et Shoes
    tshirt_category = Category.query.filter_by(name='Tshirt').first()
    shoes_category = Category.query.filter_by(name='Shoes').first()

    # Supprimer les produits de ces catégories
    if tshirt_category:
        Product.query.filter_by(category_id=tshirt_category.id).delete()
    if shoes_category:
        Product.query.filter_by(category_id=shoes_category.id).delete()

    # Sauvegarder les changements dans la base de données
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        delete_products()
