from flask import render_template, redirect, url_for, request, flash, jsonify
from app import app, db
from app.controller import PostController, SearchController
from flask_login import login_required, current_user
import sqlalchemy as sa
from app.models import User
from app.forms import EditProfileForm
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html')

@app.route('/explore', methods=['GET'])
def load_explorepage():
    arguments = request.args
    if len(arguments) > 0:
        if len(arguments) == 1 and arguments.get('query', '') == '':
            return PostController.get_top_questions()
        else:
            return PostController.get_searched_questions(arguments)
    else:
        return PostController.get_top_questions()

@app.route('/create', methods=['GET', 'POST'])
def load_createpage():
    return PostController.create_post()
    posts = []
    return render_template("explorePage.html", posts=posts)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "This username or email already exists."}), 400
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "You have been registered."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_email = data.get('username_email')
    password = data.get('password')
    user = User.query.filter((User.username == username_email) | (User.email == username_email)).first()
    if user and user.check_password(password):
        return jsonify({"message": "Logged in."}), 200
    return jsonify({"error": "Entered credentials are invalid."}), 401

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)