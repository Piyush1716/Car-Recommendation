from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and configure database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cardb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Car model
class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    fuel_type = db.Column(db.String(50), nullable=True)
    transmission = db.Column(db.String(50), nullable=True)

# Test route for pagination
@app.route('/test_pagination')
def test_pagination():
    try:
        # Set test pagination parameters
        page = 1
        per_page = 20

        # Fetch cars with pagination
        cars = Car.query.paginate(page, per_page, False)

        # Print the results
        for car in cars.items:
            print(f"Car ID: {car.id}, model: {car.model}, Price: {car.price}")

        # Pagination details
        print(f"Current Page: {cars.page}")
        print(f"Total Pages: {cars.pages}")
        print(f"Has Next: {cars.has_next}")
        print(f"Has Previous: {cars.has_prev}")

        return "Pagination Test Successful. Check console output."

    except Exception as e:
        print(f"Error: {e}")
        return f"An error occurred: {e}"

if __name__ == "__main__":
    app.run(debug=True)
