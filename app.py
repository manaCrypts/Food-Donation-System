import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-food-donation-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

food_types = [
    'Any',
    'Vegetarian',
    'Cooked Meal',
    'Dry Food',
    'Bakery',
    'Fruits & Vegetables',
    'Packaged Food',
    'Ready-to-Eat',
]


def get_admin_credentials():
    return (
        os.environ.get('ADMIN_USERNAME', 'admin'),
        os.environ.get('ADMIN_PASSWORD', 'password123'),
    )


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(120), nullable=False)
    food_type = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    pickup_address = db.Column(db.String(250), nullable=True)
    city = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    expiry_date = db.Column(db.String(60), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def home():
    db.create_all()
    latest_donations = Donation.query.filter_by(is_available=True).order_by(Donation.created_at.desc()).limit(4).all()
    available_count = Donation.query.filter_by(is_available=True).count()
    return render_template(
        'home.html',
        latest_donations=latest_donations,
        available_count=available_count,
    )


@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        donor_name = request.form.get('donor_name', '').strip()
        food_type = request.form.get('food_type', '').strip()
        quantity = request.form.get('quantity', '').strip()
        description = request.form.get('description', '').strip()
        pickup_address = request.form.get('pickup_address', '').strip()
        city = request.form.get('city', '').strip()
        phone = request.form.get('phone', '').strip()
        expiry_date = request.form.get('expiry_date', '').strip()

        if not donor_name or not food_type or not quantity or not city or not phone or not expiry_date:
            flash('Please complete all required fields before submitting.', 'danger')
            return redirect(url_for('donate'))

        donation = Donation(
            donor_name=donor_name,
            food_type=food_type,
            quantity=quantity,
            description=description,
            pickup_address=pickup_address,
            city=city,
            phone=phone,
            expiry_date=expiry_date,
        )
        db.session.add(donation)
        db.session.commit()

        flash('Thank you for donating food. Your donation is now visible to people nearby.', 'success')
        return redirect(url_for('results'))

    return render_template('donate.html', food_types=food_types)


@app.route('/find', methods=['GET', 'POST'])
def find_food():
    if request.method == 'POST':
        food_type = request.form.get('food_type', '').strip()
        city = request.form.get('city', '').strip()
        return redirect(url_for('results', food_type=food_type, city=city))

    return render_template('find_food.html', food_types=food_types)


@app.route('/results')
def results():
    food_type = request.args.get('food_type', '').strip()
    city = request.args.get('city', '').strip()

    query = Donation.query.filter_by(is_available=True)
    if food_type and food_type != 'Any':
        query = query.filter(Donation.food_type == food_type)
    if city:
        query = query.filter(Donation.city.ilike(f'%{city}%'))

    food_donations = query.order_by(Donation.created_at.desc()).all()
    return render_template(
        'results.html',
        food_donations=food_donations,
        search_term={'food_type': food_type, 'city': city},
    )


@app.route('/take/<int:donation_id>')
def take_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    donation.is_available = False
    db.session.commit()
    flash('This donation has been marked as taken and removed from the available list.', 'success')
    return redirect(url_for('results'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        admin_username, admin_password = get_admin_credentials()

        if username == admin_username and password == admin_password:
            session['admin'] = True
            flash('Admin login successful.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid admin credentials. Please try again.', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('login.html')


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    available_count = Donation.query.filter_by(is_available=True).count()
    taken_count = Donation.query.filter_by(is_available=False).count()
    total_count = available_count + taken_count

    city_counts = {}
    for donation in Donation.query.filter_by(is_available=True).all():
        city_counts[donation.city] = city_counts.get(donation.city, 0) + 1

    return render_template(
        'dashboard.html',
        total_count=total_count,
        available_count=available_count,
        taken_count=taken_count,
        city_counts=city_counts,
        donations=donations,
    )


if __name__ == '__main__':
    app.run(debug=True)
