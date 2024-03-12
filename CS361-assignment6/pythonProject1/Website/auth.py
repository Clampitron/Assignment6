from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from . import db
import requests
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import Bookmark


auth = Blueprint('auth', __name__)
url_list = []


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    firstname = db.Column(db.String(150))
    password = db.Column(db.String(150))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # In real-world applications, this should be hashed

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            # Login success
            session['User_id'] = user.id  # Store user's ID in session correctly within the scope
            flash('Logged in successfully!', category='success')
            return redirect(url_for('auth.home'))  # Ensure this matches your actual profile view function name
        else:
            flash('Invalid login credentials.', category='error')

    return render_template("Login.html")


@auth.route('/logout')
def logout():
    # Remove user_id from session to log the user out
    session.pop('User_id', None)

    # Flash a message to indicate successful logout
    flash('You have been logged out.', category='info')

    # Redirect to login page or home page after logout
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Redirect logged-in users
    if 'User_id' in session:
        return redirect(url_for('auth.home'))  # Adjust the redirection as needed

    if request.method == 'POST':
        email = request.form.get('email', '')
        firstname = request.form.get('firstName', '')
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')

        # Check if user already exists
        user_exists = User.query.filter_by(email=email).first() is not None

        if user_exists:
            flash('Email already registered.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(firstname) <= 2:
            flash('Name must be longer than 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password has to be at least 7 characters long.', category='error')
        else:
            new_user = User(email=email, firstname=firstname, password=password1)
            db.session.add(new_user)
            try:
                db.session.commit()
                flash('Account created!', category='success')
            except IntegrityError:
                db.session.rollback()
                flash('Email already registered.', category='error')
            except SQLAlchemyError:
                db.session.rollback()
                flash('Database error. Please try again.', category='error')

    return render_template("Sign_up.html")


@auth.route('/My-Recipe')
def my_recipe():
    user_id = session.get('User_id')
    if user_id is not None:
        bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
        return render_template("My_recipes.html", bookmarks=bookmarks)
    else:
        return redirect(url_for('auth.login'))


@auth.route('/Found-Recipes', methods=['GET', 'POST'])
def Found_Recipes():
    # Default message for direct navigation or incomplete selections
    message = "Please go back to the home page to select preferences."
    url_list = []

    if request.method == 'POST':
        cuisine = request.form.get('cuisine')
        type = request.form.get('type')
        lifestyle = request.form.get('lifestyle')

        # Validate selections
        if cuisine and type and lifestyle:
            # Store validated preferences in session
            session['recipe_preferences'] = {
                'cuisine': cuisine,
                'type': type,
                'lifestyle': lifestyle
            }
            headers = {'Content-Type': 'application/json'}
            # Call microservice and return URL list that match the preferences
            r = requests.post('http://localhost:5001/mservice', json=session['recipe_preferences'])
            if r.status_code == 200:
                url_list = r.json().get('links', [])
                print(url_list)
            else:
                flash('Failed to retrieve recipes. Please try again later.', 'error')
                return redirect(url_for('auth.home'))
        else:
            # If any selection is missing, flash a message and redirect back to home
            flash('You must select one option from each category.', 'error')
            return redirect(url_for('auth.home'))

    # Retrieve preferences for rendering or show default message
    preferences = session.get('recipe_preferences', [])

    return render_template("Found_Recipes.html", preferences=preferences, url_list=url_list, message=message)


@auth.route('/bookmark', methods=['POST'])
def bookmark_recipe():
    if 'User_id' not in session:
        return jsonify({'error': 'User not logged in'}), 403

    data = request.get_json()
    url = data.get('url')
    user_id = session.get('User_id')

    # Assuming you have a Bookmark model with a user_id and url field
    new_bookmark = Bookmark(user_id=user_id, url=url)
    db.session.add(new_bookmark)
    try:
        db.session.commit()
        return jsonify({'message': 'Bookmark added successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add bookmark'}), 500


@auth.route('/')
def home():
    preferences = session.get('recipe_preferences', {})
    return render_template("home.html")
