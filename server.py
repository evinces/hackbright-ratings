"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Movie, Rating, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = 'ABC123'

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


# =============================================================================
# Homepage

@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')

# =============================================================================
# Users


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/users/<user_id>')
def user_page(user_id):
    """ Show user profile """

    user = User.query.filter_by(user_id=user_id).first()
    return render_template('user.html', user=user)

# =============================================================================
# Movies


@app.route('/movies')
def movie_list():
    """Show movie list"""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template('movie_list.html', movies=movies)


@app.route('/movies/<movie_id>')
def movie_page(movie_id):
    """ Show movie details """

    movie = Movie.query.filter_by(movie_id=movie_id).first()
    return render_template('movie.html', movie=movie)

# =============================================================================
# Registration


@app.route('/register', methods=['GET'])
def register_form():
    """User creation form"""

    return render_template('register_form.html')


@app.route('/register', methods=['POST'])
def register_process():
    """User intake"""

    email = request.form.get('email')
    password = request.form.get('password')
    age = int(request.form.get('age'))
    zipcode = request.form.get('zipcode')

    if User.query.filter(User.email == email).first() is None:
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        session['email'] = email
        flash('User created and logged in')
        return redirect('/users/{}'.format(user.user_id))

    flash('User already exists')
    return redirect('/login')

# =============================================================================
# Login / Logout


@app.route('/login', methods=['GET'])
def login_form():
    """Display login form"""

    if 'email' in session:
        del session['email']

    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def login_process():
    """Log in user"""

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('User not found')
        return redirect('/login')

    if password == user.password:
        session['email'] = email
        flash('Logged in')
        return redirect('/users/{}'.format(user.user_id))

    flash('Invalid password')
    return redirect('/login')


@app.route('/logout')
def logout_process():
    """Log out user"""

    if 'email' in session:
        del session['email']
        flash("Logged out")

    return redirect('/')


if __name__ == '__main__':
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
