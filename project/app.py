from flask import Flask, render_template, request, redirect, session, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import smtplib

app = Flask(__name__)
app.secret_key = 'USAERDroot00$$GreenBELLYyellowThumbTomORROWHABETVCQWTVQKJHDF*&#(&@%*!)'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'https://mail.google.com/'  # Replace with your email server
app.config['MAIL_PORT'] = 587  # Replace with the appropriate port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'danielchico5411'  # Replace with your email username
app.config['MAIL_PASSWORD'] = 'password919'  # Replace with your email password

mail = Mail(app)

# Database initialization
conn = sqlite3.connect('database1.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, email TEXT, lic TEXT, miles INTEGER, weight INTEGER, total_price INTEGER, truck TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS guest (id INTEGER PRIMARY KEY AUTOINCREMENT, gmiles INTEGER, gweight INTEGER, gtotal_price INTEGER, gtruck TEXT, guest_email TEXT)')


@app.route('/')
def index():
    if 'user_id' not in session:
        return render_template('guest.html')

    user_id = session['user_id']
    cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    return render_template('dashboard.html', username=user[1])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        lic = request.form['lic']
        email = request.form['email']

        if not (username and email):
            flash('All fields are required.', 'error')
            return redirect('/register')

        # Hash the password and license before storing them in the database
        hashed_lic = generate_password_hash(lic)
        hashed_password = generate_password_hash(password)

        # Check if the username or email already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username or email already exists.', 'error')
            return redirect('/register')

        conn.execute('INSERT INTO users (username, password, email, lic) VALUES (?, ?, ?, ?)',
                     (username, hashed_password, email, hashed_lic))
        conn.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/get_guest_quote', methods=['GET', 'POST'])
def get_guest_quote():
    if request.method == "POST":
        guest_email = request.form['guest_email']
        gtruck = request.form['gtruck']
        gmiles = float(request.form["gmiles"])
        gweight = float(request.form["gweight"])
        gprice_per_mile = 1.75
        gprice_per_pound = 1.50
        gtotal_price = gmiles * gprice_per_mile + gweight * gprice_per_pound

        # Check if the guest email has already been used
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE guest_email = ?', (guest_email,))
        existing_guest = cursor.fetchone()
        if existing_guest:
            flash('Email already used.', 'error')
            return redirect('/get_guest_quote')

        # Validate the guest email

        # Store the quote details in the database
        conn.execute('INSERT INTO guest (gmiles, gweight, gtotal_price, gtruck, guest_email) VALUES (?, ?, ?, ?, ?)',
                     (gmiles, gweight, gtotal_price, gtruck, guest_email))
        conn.commit()

        return render_template("guest_quote.html", guest_email=guest_email, miles=gmiles, truck=gtruck,
                               price_per_mile=gprice_per_mile, total_price=gtotal_price, weight=gweight,
                               price_per_pound=gprice_per_pound)

    return render_template('get_guest_quote.html')


@app.route('/get_quote', methods=['GET', 'POST'])
def get_quote():
    if request.method == "POST":
        truck = request.form['truck']
        miles = float(request.form["miles"])
        weight = float(request.form["weight"])
        price_per_mile = 1
        price_per_pound = 1
        total_price = miles * price_per_mile + weight * price_per_pound

        if not (truck and miles and weight):
            flash('All fields are required.', 'error')
            return redirect('/get_quote')

        user_id = session['user_id']
        cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        return render_template("quote.html", username=user[1], miles=miles, truck=truck, price_per_mile=price_per_mile,
                               total_price=total_price, weight=weight, price_per_pound=price_per_pound)

    return render_template('get_quote.html')


@app.route('/quote', methods=['GET', 'POST'])
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    return render_template('get_quote.html')


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Create and send the email
    msg = Message('New Contact Form Submission', sender='sender@example.com', recipients=['daniel.j.chico@outlook.com'])
    msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    mail.send(msg)

    flash('Thank you for your message. We will get back to you soon!', 'success')
    return redirect('/')


@app.route('/guest_quote', methods=['GET', 'POST'])
def guest_quote():
    return render_template('guest_quote.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/user_about', methods=['GET', 'POST'])
def user_about():
    return render_template('user_about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/user_contact', methods=['GET', 'POST'])
def user_contact():
    return render_template('user_contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user is not None and check_password_hash(user[2], password):
            session['user_id'] = user[0]  # store the user's ID in the session
            return redirect('/dashboard')
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    return render_template('dashboard.html', username=user[1])


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
