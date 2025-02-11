# Cars4You - Car Buying and Selling Platform

Cars4You is a web application designed to facilitate the buying and selling of cars. It provides a platform for sellers to list their cars and for buyers to browse, filter, and interact with car listings. The application includes features such as user authentication, car recommendations, email notifications, and interaction tracking.

## Features

### For Buyers:
- **Browse Cars**: View a list of available cars with filters for location, fuel type, and transmission.
- **Car Details**: View detailed information about a specific car, including similar car recommendations.
- **Contact Seller**: Send an email inquiry to the seller directly from the platform.
- **Whitelist**: Add cars to a favorites list for easy access later.
- **Cart**: Shortlist cars for potential purchase.
- **Recommendations**: Get personalized car recommendations based on user interactions and preferences.
  - **User-Based Recommendations**: Recommendations based on similar users' interactions.
  - **Item-Based Recommendations**: Recommendations based on similar cars.
  - **Content-Based Recommendations**: Recommendations based on car attributes.
  - **Popularity-Based Recommendations**: Recommendations based on the most popular cars.

### For Sellers:
- **Add Cars**: List new cars for sale with detailed information and images.
- **Edit Cars**: Update car details and images.
- **Delete Cars**: Remove car listings.
- **View Car Details**: View detailed information about listed cars, including the number of views and interested buyers.
- **Mark as Sold**: Mark a car as sold (placeholder functionality).

### General:
- **User Authentication**: Register, login, and logout functionality for buyers and sellers.
- **Email Notifications**: Sellers receive email notifications when a buyer is interested in their car.
- **Interaction Tracking**: Track user interactions such as views, likes, and shortlists.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: MySQL (using SQLAlchemy ORM)
- **Email Service**: Flask-Mail for sending email notifications
- **Data Processing**: Pandas for data manipulation and analysis
- **Machine Learning**: Scikit-learn for recommendation algorithms (cosine similarity, one-hot encoding, standard scaling)

## Installation

### Prerequisites
- Python 3.x
- MySQL
- Flask
- Flask-SQLAlchemy
- Flask-Mail
- Pandas
- Scikit-learn

### Steps to Run the Application

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Piyush1716/Car-Recommendation.git
   cd Car-Recommendation
   ```

2. **Set Up the Database**:
   - Create a MySQL database named `cardb`.
   - Update the database connection string in `app.py`:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cardb'
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   - Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage

### Buyer Flow:
1. **Register/Login**: Register as a buyer or log in if you already have an account.
2. **Browse Cars**: Use the filters to find cars that match your preferences.
3. **View Car Details**: Click on a car to view detailed information and similar car recommendations.
4. **Interact with Cars**: Like, shortlist, or contact the seller for more information.
5. **View Recommendations**: Check the recommendations section for personalized car suggestions.

### Seller Flow:
1. **Register/Login**: Register as a seller or log in if you already have an account.
2. **Add Cars**: List new cars for sale by filling out the car details form.
3. **Manage Listings**: Edit or delete car listings as needed.
4. **View Car Details**: Check the number of views and interested buyers for your listed cars.
5. **Mark as Sold**: Mark a car as sold when a deal is finalized.

## API Endpoints

- **GET `/`**: Redirects to the login page.
- **GET/POST `/login`**: User login.
- **GET `/buyer_dashboard`**: Buyer dashboard with car listings and filters.
- **GET `/cars`**: View all cars.
- **POST `/contact_seller`**: Send an email inquiry to the seller.
- **POST `/interaction`**: Handle user interactions (like, shortlist, view).
- **GET `/view_whitelist`**: View the buyer's whitelist (favorites).
- **GET `/view_cart`**: View the buyer's cart (shortlisted cars).
- **GET `/remove_from_cart/<int:car_id>`**: Remove a car from the cart.
- **GET `/remove_from_whitelist/<int:car_id>`**: Remove a car from the whitelist.
- **GET `/buyer_car_details/<int:car_id>`**: View detailed information about a car.
- **GET `/recommendations`**: Get user-based recommendations.
- **GET `/item_based_recommendations`**: Get item-based recommendations.
- **GET `/content_based_recommendations`**: Get content-based recommendations.
- **GET `/popularity_based_recommendations`**: Get popularity-based recommendations.
- **GET/POST `/seller_dashboard`**: Seller dashboard for managing car listings.
- **GET `/delete_car/<int:car_id>`**: Delete a car listing.
- **GET/POST `/edit_car/<int:car_id>`**: Edit a car listing.
- **GET `/seller_car_details/<int:car_id>`**: View detailed information about a seller's car.
- **GET `/mark_as_sold/<int:car_id>`**: Mark a car as sold (placeholder).
- **GET/POST `/register`**: User registration.
- **GET `/logout`**: User logout.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to the branch.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please contact:

- **Email**: chunarapiyush10@gmail.com
- **GitHub**: [Your GitHub Profile](https://github.com/Piyush1716)

---

Thank you for using Cars4You! We hope you enjoy the platform. 🚗✨
