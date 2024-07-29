from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.forms import RegistrationForm, LoginForm, PurchaseForm, ProductForm, ReservationForm
from app.models import User, Product, Category, Reservation
from flask_login import login_user, current_user, logout_user, login_required
import os
import secrets
from PIL import Image
from flask import current_app
import subprocess

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/product_pics', picture_fn)
    
    output_size = (800, 800)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/')
@app.route('/home')
def home():
    recent_products = Product.query.order_by(Product.id.desc()).limit(8).all()
    return render_template('home.html', recent_products=recent_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.is_admin = form.is_admin.data  # Enregistrement de l'état admin
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                return redirect(next_page or url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product(product_id):
    product = Product.query.get_or_404(product_id)
    form = PurchaseForm()
    if form.validate_on_submit():
        flash('Purchase successful!', 'success')
        return redirect(url_for('home'))
    return render_template('product.html', product=product, form=form)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/products')
def show_products():
    categories = Category.query.all()
    return render_template('product.html', categories=categories)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('home'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image_file=save_picture(form.image.data),
            category_id=form.category_id.data,
            available_sizes=form.available_sizes.data.strip() if form.available_sizes.data else ''
        )
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_product.html', title='Add Product', form=form)

@app.route('/reserve/<int:product_id>', methods=['GET', 'POST'])
def reserve_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReservationForm()

    if product.available_sizes:
        sizes = product.available_sizes.split(',')
        form.size.choices = [(size.strip(), size.strip()) for size in sizes if size.strip()]
    else:
        form.size.choices = []

    if form.validate_on_submit():
        reservation = Reservation(
            product_id=product.id,
            full_name=form.full_name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            address=form.address.data,
            size=form.size.data
        )
        db.session.add(reservation)
        db.session.commit()
        flash('Your reservation has been successfully recorded!', 'success')
        return redirect(url_for('home'))
    return render_template('reserve.html', title='Reserve Product', product=product, form=form)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('home'))
    categories = Category.query.all()
    return render_template('admin_dashboard.html', categories=categories)

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(product_id)
    form = ProductForm()

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        if form.image.data:
            product.image_file = save_picture(form.image.data)
        product.category_id = form.category_id.data
        product.available_sizes = form.available_sizes.data.strip() if form.available_sizes.data else ''
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))

    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.description.data = product.description
        form.category_id.data = product.category_id
        form.available_sizes.data = product.available_sizes
    
    return render_template('edit_product.html', title='Edit Product', form=form)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reservations', methods=['GET', 'POST'])
@login_required
def admin_reservations():
    if not current_user.is_admin:
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('home'))
    
    reservations = Reservation.query.all()
    return render_template('admin_reservations.html', reservations=reservations)

@app.route('/admin/reservation/complete/<int:reservation_id>', methods=['POST'])
@login_required
def complete_reservation(reservation_id):
    if not current_user.is_admin:
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('home'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = "Completed"
    db.session.commit()
    flash('Reservation marked as completed!', 'success')
    return redirect(url_for('admin_reservations'))

if __name__ == '__main__':
    app.run(debug=True)
