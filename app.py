from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cardb'  # Update with your MySQL credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords
    role = db.Column(db.Enum('buyer', 'seller', name='user_roles'), nullable=False)


# Car model representing the cars table
class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    fuel_type = db.Column(db.String(50), nullable=False)
    transmission = db.Column(db.String(50), nullable=False)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Buyer or Seller

        user = User.query.filter_by(email=email, role=role).first()

        if user and user.password == password:
            # session['user_id'] = user.id
            # session['role'] = user.role

            # Redirect based on role
            if role == 'buyer':
                return redirect(url_for('buyer_dashboard'))
            elif role == 'seller':
                return redirect(url_for('seller_dashboard'))
        else:
            flash('Invalid credentials or role mismatch', 'danger')

    return render_template('login.html')



@app.route('/buyer_dashboard', methods=['GET', 'POST'])
def buyer_dashboard():
    # Query all cars and convert to Pandas DataFrame
    cars_query = Car.query.all()
    cars_list = [
        {
            'id': car.id,
            'model': car.model,
            'year': car.year,
            'price': car.price,
            'location': car.location,
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
        }
        for car in cars_query
    ]
    cars_df = pd.DataFrame(cars_list)

    # Get unique filter options from the DataFrame
    locations = cars_df['location'].dropna().unique()
    fuel_types = cars_df['fuel_type'].dropna().unique()
    transmissions = cars_df['transmission'].dropna().unique()

    # Filtering logic
    filtered_cars = cars_df  # Start with all cars
    if request.method == 'POST':
        location_filter = request.form.get('location')
        fuel_type_filter = request.form.get('fuel_type')
        transmission_filter = request.form.get('transmission')

        # Apply filters using Pandas
        if location_filter and location_filter != 'any':
            filtered_cars = filtered_cars[filtered_cars['location'] == location_filter]
        if fuel_type_filter and fuel_type_filter != 'any':
            filtered_cars = filtered_cars[filtered_cars['fuel_type'] == fuel_type_filter]
        if transmission_filter and transmission_filter != 'any':
            filtered_cars = filtered_cars[filtered_cars['transmission'] == transmission_filter]

    # Convert the filtered DataFrame back to a list of dictionaries for the template
    cars = filtered_cars.to_dict(orient='records')

    return render_template(
        'buyer_dashboard.html',
        cars=cars,
        locations=locations,
        fuel_types=fuel_types,
        transmissions=transmissions
    )

# Placeholder route for seller dashboard
@app.route('/seller_dashboard', methods=['GET', 'POST'])
def seller_dashboard():
    message = None  # Default message

    if request.method == 'POST':
        # Get form data
        model = request.form.get('car_name')
        year = request.form.get('year')
        price = request.form.get('price')
        location = request.form.get('location')
        fuel_type = request.form.get('fuel_type')
        transmission = request.form.get('transmission')

        # Validate input
        if not all([model, year, price, location, fuel_type, transmission]):
            message = "All fields are required to add a car."
        else:
            try:
                # Add the car to the database
                new_car = Car(
                    model=model,
                    year=int(year),
                    price=float(price),
                    location=location,
                    fuel_type=fuel_type,
                    transmission=transmission
                )
                db.session.add(new_car)
                db.session.commit()
                message = "Car added successfully!"
            except Exception as e:
                # Handle database errors
                message = f"An error occurred: {str(e)}"

    return render_template('seller_dashboard.html', message=message)

import logging

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']

            # Validate input
            if not username or not email or not password or not role:
                flash("All fields are required!", "danger")
                return redirect('/register')

            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email is already registered!", "danger")
                return redirect('/register')

            # Add user to database
            new_user = User(username=username, email=email, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')

    except Exception as e:
        logging.error(f"Error during registration: {e}")
        flash("An unexpected error occurred. Please try again later.", "danger")

    return render_template('register.html')


# Route for logging out
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))  # Redirect to login page


if __name__ == "__main__":
    app.run(debug=True)