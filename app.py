from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import schedule
import time
import smtplib
from threading import Thread
import os
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS (only if serving frontend separately)
CORS(app)

# Configuration for MySQL database using pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password01@127.0.0.1:3306/drug_inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Drug model
class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    manufacture_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    supplier_id = db.Column(db.String(50), nullable=False)
    supplier_name = db.Column(db.String(100), nullable=False)
    supply_date = db.Column(db.Date, nullable=False)
    purchase_order_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    warehouse_id = db.Column(db.String(50), nullable=False)
    warehouse_location = db.Column(db.String(100), nullable=False)
    stock_in_date = db.Column(db.Date, nullable=False)
    stock_out_date = db.Column(db.Date, nullable=True)
    current_stock_level = db.Column(db.Integer, nullable=False)
    predicted_expiry_risk = db.Column(db.String(50), nullable=False)
    notification_date = db.Column(db.Date, nullable=False)

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Handle favicon requests
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

# Endpoint to add drugs to the inventory
@app.route('/add_drug', methods=['POST'])
def add_drug():
    data = request.get_json()

    try:
        expiry_date = datetime.strptime(data['Expiry_Date'], '%Y-%m-%d').date()
        notification_date = expiry_date - timedelta(days=10)

        drug = Drug(
            drug_name=data['Drug_Name'],
            batch_number=data['Batch_Number'],
            manufacture_date=datetime.strptime(data['Manufacture_Date'], '%Y-%m-%d').date(),
            expiry_date=expiry_date,
            supplier_id=data['Supplier_ID'],
            supplier_name=data['Supplier_Name'],
            supply_date=datetime.strptime(data['Supply_Date'], '%Y-%m-%d').date(),
            purchase_order_id=data['Purchase_Order_ID'],
            quantity=int(data['Quantity']),
            warehouse_id=data['Warehouse_ID'],
            warehouse_location=data['Warehouse_Location'],
            stock_in_date=datetime.strptime(data['Stock_In_Date'], '%Y-%m-%d').date(),
            stock_out_date=None if 'Stock_Out_Date' not in data else datetime.strptime(data['Stock_Out_Date'], '%Y-%m-%d').date(),
            current_stock_level=int(data['Current_Stock_Level']),
            predicted_expiry_risk=data['Predicted_Expiry_Risk'],
            notification_date=notification_date
        )

        db.session.add(drug)
        db.session.commit()

        return jsonify({"message": "Drug added successfully", "Notification_Date": notification_date.strftime('%Y-%m-%d')}), 201
    except Exception as e:
        return jsonify({"message": "Failed to add drug", "error": str(e)}), 400

# Endpoint to get a list of all drugs
@app.route('/drugs', methods=['GET'])
def get_drugs():
    drugs = Drug.query.all()
    drug_list = [{
        "Drug_Name": drug.drug_name,
        "Batch_Number": drug.batch_number,
        "Expiry_Date": drug.expiry_date.strftime('%Y-%m-%d')
    } for drug in drugs]

    return jsonify(drug_list), 200

# Function to send email notifications
def send_notification(drug_name, expiry_date):
    sender_email = "shreya.22211616@viit.ac.in"  # Replace with your email
    receiver_email = "vanshika.22211207@viit.ac.in"  # Replace with recipient email
    password = "repo2k26"  # Replace with your email password
    subject = f"Drug Expiry Alert: {drug_name} is nearing expiry"
    body = f"The drug {drug_name} is set to expire on {expiry_date}. Please take appropriate action."

    # Create the email content
    message = f"Subject: {subject}\n\n{body}"

    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        print(f"Notification sent for {drug_name}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check for drugs nearing expiry
def check_for_expiry():
    today = datetime.today().date()
    drugs = Drug.query.filter(Drug.notification_date <= today).all()
    
    for drug in drugs:
        send_notification(drug.drug_name, drug.expiry_date)

## Scheduler to run the notifier every minute
def run_scheduler():
    with app.app_context():  # Ensure the scheduler runs inside the app context
        while True:
            schedule.run_pending()
            time.sleep(1)



# Start the scheduler in a background thread
def start_scheduler():
    thread = Thread(target=run_scheduler)
    thread.start()

# Additional endpoints
@app.route('/test_expiry_notification', methods=['GET'])
def test_expiry_notification():
    try:
        check_for_expiry()  # Call the function that checks for expiry
        return "Expiry notification logic triggered!", 200
    except Exception as e:
        print(f"Error occurred while checking for expiry: {e}")
        return "An error occurred!", 500

@app.route('/routes', methods=['GET'])
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(str(rule))
    return jsonify(output), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    start_scheduler()  # Start the scheduler
    print("Starting Flask app...")  # Debugging statement
    app.run(debug=True)
