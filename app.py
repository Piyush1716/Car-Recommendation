from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_mail import Message, Mail
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from werkzeug.utils import secure_filename
import os

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

# Define the folder where images will be stored
UPLOAD_FOLDER = 'static/uploads/cars/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    kilometers_driven = db.Column(db.Integer, nullable=False)
    owner_type = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Float, nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Float, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    ageofcar = db.Column(db.Integer, nullable=False)
    brand_class = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)  # Image URL path


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
    if 'email' not in session:
        # If no user is logged in, redirect to login page
        return redirect(url_for('login'))

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
        transmissions=transmissions,
        email = session['email']
    )
# To View all Cars
@app.route('/cars', methods=['GET'])
def cars():    
    if 'email' not in session:
        return redirect(url_for('login'))

    # Query the cars table
    cars = Car.query.all()
    
    # Pass the cars info to the template
    return render_template('cars.html', cars=cars)

# Contect seller via Email
@app.route('/contact_seller', methods=['POST'])
def contact_seller():
    if 'email' not in session:
        return redirect(url_for('login'))

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
        return redirect(url_for('buyer_car_details', car_id=car_id))

    return redirect(url_for('buyer_dashboard'))

# Route to display whitelist
@app.route('/view_whitelist', methods=['GET'])
def view_whitelist():
    # Get logged-in user's email
    if 'email' not in session:
        flash("Please log in to view your whitelist.", "warning")
        return redirect(url_for('login'))

    buyer_email = session['email']
    # Fetch cars in the whitelist for the logged-in user
    whitelist = db.session.query(Car).join(UserInteraction, Car.id == UserInteraction.car_id)\
        .filter(UserInteraction.buyer_email == buyer_email, UserInteraction.in_whitelist == True).all()

    return render_template('whitelist.html', whitelist=whitelist)

# Route to display cart
@app.route('/view_cart', methods=['GET'])
def view_cart():
    # Get logged-in user's email
    if 'email' not in session:
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for('login'))

    buyer_email = session['email']
    # Fetch cars in the cart for the logged-in user
    cart = db.session.query(Car).join(UserInteraction, Car.id == UserInteraction.car_id)\
        .filter(UserInteraction.buyer_email == buyer_email, UserInteraction.in_cart == True).all()

    return render_template('cart.html', cart=cart)


@app.route('/buyer_car_details/<int:car_id>', methods=['GET'])
def buyer_car_details(car_id):
    if 'email' in session :
        car = Car.query.get_or_404(car_id)  # Fetch car details from the database
        return render_template('buyer_car_details.html', car=car)
    
    return redirect(url_for('login'))

        # Recommendation moduls
'''
        1. user based
Similar User based recommendation Modual
how works : if two users (A,B) have simiarity in interaction table
            like then have same whitelist and cart
            then A will recommend cars that are in whitelist and cart in user B
            And B will recommend cars that are in whitelist and cart in user A
'''
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

'''
        2. item baesd
Similar cars interacted by user based recommendation Modual
how works : if two cars (A,B) have simiarity in interaction table
            if many users interact (shortlisted  and liked) similarly with cars A and B, 
            they are considered similar.
            After identifying the cars the user has interacted with, 
            the system recommends cars similar to those based on the interaction patterns of all users, 
            not just the individual user.
'''

@app.route('/item_based_recommendations', methods=['GET'])
def item_based_recommendations():
    if 'email' not in session:
        flash("Please log in to get recommendations.", "warning")
        return redirect(url_for('login'))

    user_email = session['email']

    # Step 1: Fetch user interaction data
    interactions = UserCarInteraction.query.all()
    interaction_list = [
        {'user_email': inter.user_email, 'car_id': inter.car_id, 'weight': inter.weight}
        for inter in interactions
    ]
    interaction_df = pd.DataFrame(interaction_list)

    if interaction_df.empty:
        flash("No interaction data available for recommendations.", "info")
        return redirect(url_for('buyer_dashboard'))

    # Step 2: Create item-user matrix
    item_user_matrix = interaction_df.pivot_table(index='car_id', columns='user_email', values='weight', fill_value=0)

    # Step 3: Compute item-item similarity matrix
    from sklearn.metrics.pairwise import cosine_similarity
    item_similarity_matrix = cosine_similarity(item_user_matrix)
    item_similarity_df = pd.DataFrame(item_similarity_matrix, index=item_user_matrix.index, columns=item_user_matrix.index)

    # Step 4: Generate recommendations
    def recommend_similar_cars(user_email, num_recommendations=5):
        # Get cars the user has interacted with
        user_interactions = interaction_df[interaction_df['user_email'] == user_email]['car_id'].tolist()

        # Aggregate similarity scores for all cars
        similar_cars_scores = pd.Series(dtype=float)
        for car_id in user_interactions:
            if car_id in item_similarity_df.index:
                similar_cars_scores = similar_cars_scores.add(item_similarity_df[car_id], fill_value=0)

        # Exclude cars already interacted with
        similar_cars_scores = similar_cars_scores.drop(index=user_interactions, errors='ignore')

        # Get top recommended cars
        return similar_cars_scores.nlargest(num_recommendations).index.tolist()

    recommended_car_ids = recommend_similar_cars(user_email)

    # Step 5: Fetch car details
    if not recommended_car_ids:
        flash("No recommendations available at this time.", "info")
        return redirect(url_for('buyer_dashboard'))

    recommended_cars = Car.query.filter(Car.id.in_(recommended_car_ids)).all()

    return render_template('recommendations.html', cars=recommended_cars)
'''
        3. content based recommendations
        Content-Based Filtering recommends items similar to those the user 
        has already interacted with. The similarity is determined based on the 
        item's attributes (e.g., price, fuel type, mileage).
        - Fuel Type, Transmission, Owner Type, and Brand Class (Categorical Attributes).
        - Price, Mileage, Age of Car (Numerical Attributes).
        1. fetch cars that user has interacted
        2. convert attributes into a formate that is suitable for calculations
        3. numerical -> standard scaler   categorical -> one hot encoder
        4. cosine similarity btw cars.
        5. For each car the user interacted with, aggregate similarity scores with other cars.
            Exclude cars the user has already interacted with.
            Recommend cars with the highest similarity scores.
'''

@app.route('/content_based_recommendations', methods=['GET'])
def content_based_recommendations():
    if 'email' not in session:
        flash("Please log in to get recommendations.", "warning")
        return redirect(url_for('login'))

    user_email = session['email']

    # Step 1: Fetch user interaction data
    user_interactions = UserCarInteraction.query.filter_by(user_email=user_email).all()
    if not user_interactions:
        flash("No interaction data available for recommendations.", "info")
        return redirect(url_for('buyer_dashboard'))

    # Get IDs of cars the user has interacted with
    interacted_car_ids = [interaction.car_id for interaction in user_interactions]

    # Step 2: Fetch attributes of all cars and convert to a DataFrame
    cars = Car.query.all()
    car_data = [
        {
            'id': car.id,
            'brand_class': car.brand_class,
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
            'mileage': car.mileage,
            'price': car.price,
            'kilometers_driven': car.kilometers_driven,
            'engine': car.engine,
            'power': car.power,
            'seats': car.seats,
            'age_of_car': car.ageofcar
        }
        for car in cars
    ]
    car_df = pd.DataFrame(car_data)

    # Step 3: Preprocess data

    # Define categorical and numerical columns
    categorical_cols = ['brand_class', 'fuel_type', 'transmission']
    numerical_cols = ['mileage', 'price', 'kilometers_driven', 'engine', 'power', 'seats', 'age_of_car']

    # One-hot encode categorical columns and scale numerical columns
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(), categorical_cols)
        ]
    )

    car_features = preprocessor.fit_transform(car_df[categorical_cols + numerical_cols])

    # Step 4: Compute similarity matrix
    similarity_matrix = cosine_similarity(car_features)

    # Convert similarity matrix to a DataFrame for easier manipulation
    similarity_df = pd.DataFrame(similarity_matrix, index=car_df['id'], columns=car_df['id'])

    # Step 5: Generate recommendations based on user interactions
    def recommend_similar_cars(interacted_car_ids, num_recommendations=5):
        # Aggregate similarity scores for all interacted cars
        similar_cars_scores = pd.Series(dtype=float)
        for car_id in interacted_car_ids:
            if car_id in similarity_df.index:
                similar_cars_scores = similar_cars_scores.add(similarity_df[car_id], fill_value=0)

        # Exclude cars the user has already interacted with
        similar_cars_scores = similar_cars_scores.drop(index=interacted_car_ids, errors='ignore')

        # Return top recommended car IDs
        return similar_cars_scores.nlargest(num_recommendations).index.tolist()

    recommended_car_ids = recommend_similar_cars(interacted_car_ids)

    # Step 6: Fetch details of recommended cars
    if not recommended_car_ids:
        flash("No recommendations available at this time.", "info")
        return redirect(url_for('buyer_dashboard'))

    recommended_cars = Car.query.filter(Car.id.in_(recommended_car_ids)).all()

    return render_template('recommendations.html', cars=recommended_cars)

from datetime import datetime
''' 
        4. Popularity based recommendations
        Popularity-Based Recommendations suggest items that are most popular among all users

        1. Rating average: Recommending items with the highest average ratings from users.
        2. Recency-based popularity: Prioritizing items that are popular recently (e.g., within the last month).
'''
@app.route('/popularity_based_recommendations', methods=['GET'])
def popularity_based_recommendations():
    if 'email' not in session:
        flash("Please log in to get recommendations.", "warning")
        return redirect(url_for('login'))

    # Step 1: Fetch user interaction data
    interactions = UserCarInteraction.query.all()
    interaction_list = [
        {
            'car_id': inter.car_id,
            'weight': inter.weight,
            'timestamp': inter.timestamp
        }
        for inter in interactions
    ]
    interaction_df = pd.DataFrame(interaction_list)

    if interaction_df.empty:
        flash("No interaction data available for recommendations.", "info")
        return redirect(url_for('buyer_dashboard'))

    # Step 2: Calculate weighted popularity with recency
    # Calculate days since interaction
    current_time = datetime.now()
    interaction_df['days_since_interaction'] = (current_time - interaction_df['timestamp']).dt.days

    # Apply recency weight: More recent interactions are more significant
    interaction_df['recency_weight'] = 1 / (1 + interaction_df['days_since_interaction'])

    # Calculate final weighted popularity score
    interaction_df['weighted_score'] = interaction_df['weight'] * interaction_df['recency_weight']

    # Aggregate scores by car_id
    car_popularity = interaction_df.groupby('car_id')['weighted_score'].sum().reset_index(name='popularity_score')
    car_popularity = car_popularity.sort_values(by='popularity_score', ascending=False)

    # Step 3: Fetch details for the top cars
    top_car_ids = car_popularity['car_id'].head(5).tolist()  # Get top 5 most popular cars
    recommended_cars = Car.query.filter(Car.id.in_(top_car_ids)).order_by(
        db.case(
            *[(Car.id == car_id, idx) for idx, car_id in enumerate(top_car_ids)]
        )
    ).all()

    return render_template('recommendations.html', cars=recommended_cars)

# Allowed extensions for image files
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Function to check allowed image extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/seller_dashboard', methods=['GET', 'POST'])
def seller_dashboard():
    if 'email' not in session:
        # If no user is logged in, redirect to login page
        return redirect(url_for('login'))
    
    seller_email = session['email']  # Get the logged-in user's email

    if request.method == 'POST':
        # Get the form data
        car_name = request.form['car_name']
        year = request.form['year']
        price = request.form['price']
        location = request.form['location']
        fuel_type = request.form['fuel_type']
        transmission = request.form['transmission']
        kilometers_driven = request.form['kilometers_driven']
        owner_type = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4}.get(request.form['owner_type'].lower(), None)
        mileage = request.form['mileage']
        engine = request.form['engine']
        power = request.form['power']
        seats = request.form['seats']
        age_of_car = request.form['age_of_car']
        brand_class = request.form['brand_class']
        
        # Handle image upload
        car_image = request.files['car_image']
        image_path = 'None'

        try:
            # Create a new Car object with the form data (without the image_url)
            new_car = Car(
                model=car_name,
                year=year,
                price=price,
                location=location,
                fuel_type=fuel_type,
                transmission=transmission,
                seller_email=seller_email,  # Assign the logged-in seller's email
                kilometers_driven=kilometers_driven,
                owner_type=owner_type,
                mileage=mileage,
                engine=engine,
                power=power,
                seats=seats,
                ageofcar=age_of_car,
                brand_class=brand_class,
                image_url=image_path  # Placeholder for the image URL
            )

            # Add the new car to the database
            db.session.add(new_car)
            db.session.commit()  # Commit to generate the car_id

            # After committing, we can get the car_id
            car_id = new_car.id

            if car_image and allowed_file(car_image.filename):
                # Generate the unique filename for the image
                new_filename = f"{car_name.replace(' ', '_')}_{car_id}{os.path.splitext(car_image.filename)[1]}"
                new_image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

                # Save the image to the specified folder
                car_image.save(new_image_path)

                # Update the car record with the new image filename
                new_car.image_url = new_image_path
                db.session.commit()  # Commit the image URL update
            flash("Car added successfully! ", "success")
        except Exception as e:
            # for developer to understand which error occurd !!
            # flash(f'An error occurred: {str(e)} ',"warning")
            flash(f'An error occurred!! ',"warning")
        return redirect(url_for('seller_dashboard'))

    # Fetch the list of cars for display
    cars = Car.query.filter_by(seller_email=seller_email).all()

    # Fetch total views and interested buyers
    car_ids = [car.id for car in cars]
    car_views = {
        car_id: db.session.query(db.func.count(UserCarInteraction.id)).filter(UserCarInteraction.car_id == car_id, UserCarInteraction.weight == 1).scalar() or 0
        for car_id in car_ids
    }
    # Calculate total views across all cars
    total_views = sum(car_views.values())
    total_views = db.session.query(db.func.count(UserCarInteraction.weight)).filter(UserCarInteraction.car_id.in_(car_ids), UserCarInteraction.weight == 1).scalar() or 0
    total_likes = db.session.query(db.func.count(UserCarInteraction.weight)).filter(UserCarInteraction.car_id.in_(car_ids), UserCarInteraction.weight == 5).scalar() or 0
    total_shortlisted = db.session.query(db.func.count(UserCarInteraction.weight)).filter(UserCarInteraction.car_id.in_(car_ids), UserCarInteraction.weight == 10).scalar() or 0
    interested_buyers = total_likes + total_shortlisted

    return render_template('seller_dashboard.html', cars=cars, total_views=total_views, interested_buyers=interested_buyers,car_views=car_views)


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
    
    if request.method == 'POST':
        try:
            # Handle form submission (POST request)
            old_model_name = car.model  # Store old model name
            car.model = request.form['car_name']
            car.year = request.form['year']
            car.price = request.form['price']
            car.location = request.form['location']
            car.fuel_type = request.form['fuel_type']
            car.transmission = request.form['transmission']
            car.kilometers_driven = request.form['kilometers_driven']
            car.owner_type = request.form['owner_type']
            car.mileage = request.form['mileage']
            car.engine = request.form['engine']
            car.power = request.form['power']
            car.seats = request.form['seats']
            car.ageofcar = request.form['age_of_car']
            car.brand_class = request.form['brand_class']

            # Handle image upload
            car_image = request.files['car_image']
            
            if car_image and car_image.filename != '':
                # Delete old image if it exists
                if car.image_url:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(car.image_url))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # Generate a new filename using car name and car ID
                if allowed_file(car_image.filename):
                    new_filename = f"{car.model.replace(' ', '_')}_{car.id}{os.path.splitext(car_image.filename)[1]}"
                    new_image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    car_image.save(new_image_path)
                    car.image_url = new_image_path
            else:
                # If image not uploaded but model name changed, rename the existing image
                if old_model_name != car.model and car.image_url:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(car.image_url))
                    new_filename = f"{car.model.replace(' ', '_')}_{car.id}{os.path.splitext(old_image_path)[1]}"
                    new_image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    os.rename(old_image_path, new_image_path)
                    car.image_url = new_image_path

            # Commit the changes to the database
            db.session.commit()

            # Flash success message
            flash(f"Car details updated successfully!" , "success")
        except Exception as e:
            # For developer to understand which error occurred
            flash(f"An error occurred: {str(e)}", "warning")

        # Redirect to the seller dashboard after updating
        return redirect(url_for('seller_dashboard'))

    # Handle GET request (render the edit form)
    return render_template('edit_car.html', car=car)

@app.route('/seller_car_details/<int:car_id>', methods=['GET'])
def seller_car_details(car_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    seller_email = session['email']

    # Get the current car details
    current_car = Car.query.filter_by(id=car_id, seller_email=seller_email).first()
    if not current_car:
        flash("Car not found or you don't have permission to view this car.", "danger")
        return redirect(url_for('seller_dashboard'))

    # Get the previous and next cars for the seller
    previous_car = (
        Car.query.filter(Car.seller_email == seller_email, Car.id < car_id)
        .order_by(Car.id.desc())
        .first()
    )
    next_car = (
        Car.query.filter(Car.seller_email == seller_email, Car.id > car_id)
        .order_by(Car.id.asc())
        .first()
    )

    # Pass the data to the template
    return render_template(
        'seller_car_details.html',
        car=current_car,
        prev_car=previous_car,
        next_car=next_car
    )

@app.route('/mark_as_sold/<int:car_id>', methods=['GET'])
def mark_as_sold(car_id):
    if 'email' in session:
        car = Car.query.get_or_404(car_id)  # Fetch car details from the database
        return render_template('seller_car_details.html', car=car)
    
    return redirect(url_for('login'))

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