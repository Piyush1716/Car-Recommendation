from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_mail import Message, Mail
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ww17161716@gmail.com'  # Sender's email
app.config['MAIL_PASSWORD'] = 'kdth avtu poge wdak'  # Sender's app password
app.config['MAIL_DEFAULT_SENDER'] = 'ww17161716@gmail.com'  # Default sender email

# Initialize Flask-Mail
mail = Mail(app)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cardb'  # Update with your MySQL credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model representing the users table
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
    seller_email = db.Column(db.String(150), nullable=False)

# UserCarInteraction model representing the UserCarInterractions (inter) table
class UserCarInteraction(db.Model):
    __tablename__ = 'inter'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(150), db.ForeignKey('users.email'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    weight = db.Column(db.Integer, nullable=False)  # Represents the interaction weight
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Manages Cart and Whitelist
class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'
    id = db.Column(db.Integer, primary_key=True)
    buyer_email = db.Column(db.String(255), db.ForeignKey('users.email'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    in_cart = db.Column(db.Boolean, default=False)
    in_whitelist = db.Column(db.Boolean, default=False)

@app.route('/', methods = ['GET','POST'])
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Buyer or Seller

        user = User.query.filter_by(email=email, role=role).first()

        if user and user.password == password:
            session['email'] = email
            session['role'] = user.role

            # Redirect based on role
            if role == 'buyer':
                return redirect(url_for('buyer_dashboard'))
            elif role == 'seller':
                return redirect(url_for('seller_dashboard'))
        else:
            flash('Invalid credentials or role mismatch', 'danger')

    return render_template('login.html')


# Buyers dashboard
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
            'seller_email' : car.seller_email
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


    #showing only fisrt 10 cars
    top10 = filtered_cars.head(10)
    # Convert the filtered DataFrame back to a list of dictionaries for the template
    cars = top10.to_dict(orient='records')

    return render_template(
        'buyer_dashboard.html',
        cars=cars,
        locations=locations,
        fuel_types=fuel_types,
        transmissions=transmissions
    )
# To View all Cars
@app.route('/cars', methods=['GET'])
def cars():    
    # Query the cars table
    cars = Car.query.all()
    
    # Pass the cars info to the template
    return render_template('cars.html', cars=cars)

# Contect seller via Email
@app.route('/contact_seller', methods=['POST'])
def contact_seller():

    buyer_email = session['email']
    seller_email = request.form['seller_email']
    car_model = request.form['car_model']

    # Retrieve the seller's name (assuming User model has a 'name' attribute)
    user = User.query.filter_by(email=seller_email).first()
    user_name = user.username if user else "Seller"

    # Subject and body
    subject = "Inquiry Received for Your Car Listing on Cars4you.com"


    # Create the email message
    msg = Message(subject, recipients=[seller_email])
    msg.html = f"""
    <html>
    <body>
        <p>Dear {user_name},</p>
        <p>We are excited to inform you that a buyer is interested in your car listing:</p>
        <ul>
        <li><strong>Car Model</strong>: {car_model}</li>
        </ul>
        <p>Here are the buyer's contact details for your reference:</p>
        <ul>
        <li><strong>Email</strong>: {buyer_email}</li>
        </ul>
        <p>We recommend contacting the buyer promptly to discuss further details and finalize the deal.</p>
        <p>If you have any questions or need assistance, feel free to reach out to our support team at 
        <a href="mailto:support@cars4you.com">support@cars4you.com</a>.</p>
        <p>Thank you for choosing Cars4you.com to sell your vehicle.</p>
        <p>Best regards,</p>
        <p><strong>The Cars4you Team</strong></p>
        <p><a href="https://www.cars4you.com">Cars4you.com</a></p>
    </body>
    </html>
    """
    
    try:
        mail.send(msg)
        flash('Email sent successfully!', 'success')
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'danger')

    return redirect(url_for('buyer_dashboard'))

# Handle User Interaction
@app.route('/interaction', methods=['POST'])
def interaction():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    car_id = request.form['car_id']
    interaction_type = request.form['interaction_type']

    # Handle the interaction types
    if interaction_type == 'like':
        # Check if the car is already in the whitelist
        existing_interaction = UserInteraction.query.filter_by(
            buyer_email=user_email, car_id=car_id
        ).first()

        if existing_interaction:
            if existing_interaction.in_whitelist:  # checks if cars is already in whitelist
                flash("Car is already in your favorites!", "info")
            else:   # car is already in cart beacause record alredy exits , so just change in_whitelist = true
                existing_interaction.in_whitelist = True
                usercarinteraction = UserCarInteraction(user_email=user_email, car_id=car_id, weight=5) # also add interaction weight
                db.session.add(usercarinteraction)
                db.session.commit()
                flash("Car added to your favorites!", "success")
        else:
            usercarinteraction = UserCarInteraction(user_email=user_email, car_id=car_id, weight=5)
            userinteraction = UserInteraction(buyer_email=user_email, car_id=car_id, in_whitelist=True)
            db.session.add(userinteraction)
            db.session.add(usercarinteraction)
            db.session.commit()
            flash("Car added to your favorites!", "success")

    elif interaction_type == 'shortlist':
        # Check if the car is already in the cart
        existing_interaction = UserInteraction.query.filter_by(
            buyer_email=user_email, car_id=car_id
        ).first()

        if existing_interaction:
            if existing_interaction.in_cart:   # checks if cars is already in cart
                flash("Car is already in your cart!", "info")
            else:   # car is already in whitelist , so just change in_cart = true
                existing_interaction.in_cart = True
                usercarinteraction = UserCarInteraction(user_email=user_email, car_id=car_id, weight=10) # also add interaction weight
                db.session.add(usercarinteraction)
                db.session.commit()
                flash("Car added to your cart!", "success")
        else:
            usercarinteraction = UserCarInteraction(user_email=user_email, car_id=car_id, weight=10)
            userinteraction = UserInteraction(buyer_email=user_email, car_id=car_id, in_cart=True)
            db.session.add(userinteraction)
            db.session.add(usercarinteraction)
            db.session.commit()
            flash("Car added to your cart!", "success")

    elif interaction_type == 'view':
        # Redirect to the car details page
        usercarinteraction = UserCarInteraction(user_email=user_email, car_id=car_id, weight=1)
        db.session.add(usercarinteraction)
        db.session.commit()
        return redirect(url_for('car_details', car_id=car_id))

    return redirect(url_for('buyer_dashboard'))

# Route to display whitelist
@app.route('/view_whitelist', methods=['GET'])
def view_whitelist():
    # Get logged-in user's email
    buyer_email = session['email']
    if not buyer_email:
        flash("Please log in to view your whitelist.", "warning")
        return redirect(url_for('login'))

    # Fetch cars in the whitelist for the logged-in user
    whitelist = db.session.query(Car).join(UserInteraction, Car.id == UserInteraction.car_id)\
        .filter(UserInteraction.buyer_email == buyer_email, UserInteraction.in_whitelist == True).all()

    return render_template('whitelist.html', whitelist=whitelist)

# Route to display cart
@app.route('/view_cart', methods=['GET'])
def view_cart():
    # Get logged-in user's email
    buyer_email = session['email']
    if not buyer_email:
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for('login'))

    # Fetch cars in the cart for the logged-in user
    cart = db.session.query(Car).join(UserInteraction, Car.id == UserInteraction.car_id)\
        .filter(UserInteraction.buyer_email == buyer_email, UserInteraction.in_cart == True).all()

    return render_template('cart.html', cart=cart)


@app.route('/car_details/<int:car_id>', methods=['GET'])
def car_details(car_id):
    car = Car.query.get_or_404(car_id)  # Fetch car details from the database
    return render_template('car_details.html', car=car)

# Our recommendation Modual
@app.route('/recommendations', methods=['GET'])
def recommendations():
    if 'email' not in session:
        flash("Please log in to get recommendations.", "warning")
        return redirect(url_for('login'))

    user_email = session['email']

    # Step 1: Fetch user interaction data using the UserCarInteraction model
    interactions = UserCarInteraction.query.all()
    interaction_list = [
        {
            'user_email': inter.user_email,
            'car_id': inter.car_id,
            'weight': inter.weight
        }
        for inter in interactions
    ]

    # Convert interaction data into a pandas DataFrame
    interaction_df = pd.DataFrame(interaction_list)

    if interaction_df.empty:
        flash("No interaction data available for recommendations.", "info")
        return redirect(url_for('buyer_dashboard'))

    # Step 2: Create a user-item interaction matrix
    interaction_matrix = interaction_df.pivot_table(index='user_email', columns='car_id', values='weight', fill_value=0)

    # Step 3: Compute similarity matrix
    similarity_matrix = cosine_similarity(interaction_matrix)
    user_similarity = pd.DataFrame(similarity_matrix, index=interaction_matrix.index, columns=interaction_matrix.index)

    # Step 4: Generate recommendations for the logged-in user
    def recommend_cars_for_user(user_email, num_recommendations=5):
        if user_email not in interaction_matrix.index:
            return []

        # Get similarity scores for the user
        similar_users = user_similarity[user_email].sort_values(ascending=False)

        # Weighted sum of car interactions from similar users
        weighted_scores = pd.Series(0, index=interaction_matrix.columns)
        for other_user, similarity in similar_users.items():
            if other_user == user_email:
                continue
            weighted_scores += similarity * interaction_matrix.loc[other_user]

        # Exclude cars the user already interacted with
        interacted_cars = interaction_matrix.loc[user_email]
        weighted_scores = weighted_scores[interacted_cars == 0]

        # Recommend the top cars
        return weighted_scores.nlargest(num_recommendations).index.tolist()

    recommended_car_ids = recommend_cars_for_user(user_email)

    # Step 5: Fetch car details for the recommended car IDs using the Car model
    if not recommended_car_ids:
        flash("No recommendations available at this time.", "info")
        return redirect(url_for('buyer_dashboard'))

    recommended_cars = Car.query.filter(Car.id.in_(recommended_car_ids)).all()

    return render_template('recommendations.html', cars=recommended_cars)


# Placeholder route for seller dashboard
@app.route('/seller_dashboard', methods=['GET', 'POST'])
def seller_dashboard():
    message = None  # Default message

    if 'email' not in session:
        # If no user is logged in, redirect to login page
        return redirect(url_for('login'))

    seller_email = session['email']  # Get the logged-in user's email

    if request.method == 'POST':
        # Get form data for adding a new car
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
                    transmission=transmission,
                    seller_email=seller_email  # Assign the logged-in seller's email
                )
                db.session.add(new_car)
                db.session.commit()
                message = "Car added successfully!"
            except Exception as e:
                # Handle database errors
                message = f"An error occurred: {str(e)}"

    # Fetch cars listed by the logged-in seller
    seller_cars = Car.query.filter_by(seller_email=seller_email).all()

    return render_template('seller_dashboard.html', message=message, cars=seller_cars)

@app.route('/delete_car/<int:car_id>', methods=['GET'])
def delete_car(car_id):

    # If no user is logged in, redirect to login page
    if 'email' not in session:
        return redirect(url_for('login'))

    # Fetch the car from the database by its ID
    car = Car.query.get_or_404(car_id)
    
    # Get the email of the currently logged-in user from the session
    current_seller_email = session['email']
    
    # Check if the logged-in user's email matches the car's seller_email
    if car.seller_email != current_seller_email:
        abort(403)  # If not, prevent deletion and show 403 Forbidden error
    
    # If the emails match, proceed with deletion
    db.session.delete(car)
    db.session.commit()
    flash("Car deleted successfully!", "info")
    
    # Redirect back to the seller dashboard
    return redirect(url_for('seller_dashboard'))

@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):

    # If no user is logged in, redirect to login page
    if 'email' not in session:
        return redirect(url_for('login'))

    # Fetch the car from the database by its ID
    car = Car.query.get_or_404(car_id)
    
    # Get the email of the currently logged-in user from the session
    current_seller_email = session['email']

    # Verify if the logged-in user's email matches the car's seller_email
    if car.seller_email != current_seller_email:
        abort(403)  # If not, prevent editing and show 403 Forbidden error
    
    # Handle form submission (POST request)
    if request.method == 'POST':
        car.model = request.form['car_name']
        car.year = request.form['year']
        car.price = request.form['price']
        car.location = request.form['location']
        car.fuel_type = request.form['fuel_type']
        car.transmission = request.form['transmission']

        # Commit the changes to the database
        db.session.commit()
        
        # Flash success message
        flash("Car details updated successfully!", "success")
        
        # Redirect to the seller dashboard after updating
        return redirect(url_for('seller_dashboard'))

    # Handle GET request (render the edit form)
    return render_template('edit_car.html', car=car)

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