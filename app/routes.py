from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User, Product, Wishlist
from .forms import RegisterForm, LoginForm, ProductForm
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists.')
            return redirect(url_for('main.register'))
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.catalog'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/catalog')
def catalog():
    products = Product.query.all()
    return render_template('catalog.html', products=products)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for('main.catalog'))
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('main.catalog'))
    return render_template('add_product.html', form=form)

@main.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash("Only admins can delete products.")
        return redirect(url_for('main.catalog'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.")
    return redirect(url_for('main.catalog'))

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@main.route('/add_to_wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        flash("Product already in wishlist.")
    else:
        new_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        flash("Added to wishlist.")
    return redirect(url_for('main.catalog'))

@main.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', items=wishlist_items)

@main.route('/remove_from_wishlist/<int:item_id>')
@login_required
def remove_from_wishlist(item_id):
    item = Wishlist.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("Unauthorized action.")
        return redirect(url_for('main.wishlist'))
    db.session.delete(item)
    db.session.commit()
    flash("Removed from wishlist.")
    return redirect(url_for('main.wishlist'))

@main.route('/discounts')
def discounts():
    return render_template('discounts.html')

@main.route('/return', methods=['GET', 'POST'])
@login_required
def return_request():
    return render_template('return_request.html')
