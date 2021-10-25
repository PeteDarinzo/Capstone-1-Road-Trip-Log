import re
from flask import Flask, render_template, request, url_for, redirect, flash, session, g, jsonify
from forms import BusinessSearchForm, ChangePasswordForm, EditProfileForm, LogForm, MaintenanceForm, SignupForm, LoginForm
from key import API_KEY
import requests
from datetime import datetime
import os
import functools
from sqlalchemy.exc import IntegrityError

from models import db, Location, connect_db, User, Log, Maintenance, Place

from werkzeug.utils import secure_filename

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://api.yelp.com/v3/businesses"
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['SECRET_KEY'] = "CanadianGeese1195432"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///greenflash'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connect_db(app)

# check if file is allowed
# if there is a '.' in the filename
# split the name at that dot, the second part
# is the file type
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/', methods=["GET", "POST"])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No File Part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if the user does not select a file, the brower submits an empty file with a filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('download_file', name=filename))
#         return '''
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     '''


##############################################################################
# User signup/login/logout

# LOGIN Decorator
def login_required(func):
    """Make sure user is logged in before proceeding."""
    @functools.wraps(func)
    def wrapper_login_required(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return wrapper_login_required


@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there is already a user with that username: flash message
    and re-present form.
    """

    form = SignupForm()

    if form.validate_on_submit():
        try: 
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
                )
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/signup.html", form=form)

        do_login(user)

        return redirect(url_for("home"))

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                form.password.data)

        next_url = request.form.get('next')

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")

            if next_url:
                return redirect(next_url)

            else:
                return redirect(url_for("home"))

        flash("Invalid credentials.", "danger")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle user logout."""

    do_logout()

    flash("Logout successful!", 'success')

    return redirect(url_for("login"))
    


######################################################
# Home Routes
######################################################

@app.route("/")
def landing():
    form = BusinessSearchForm()

    return redirect("/home")
    # return render_template('home-anon.html', form=form)


@app.route("/home")
def home():

    form = BusinessSearchForm()

    users=User.query.all()

    return render_template('home.html', users=users, form=form)


@app.route("/users/<username>")
def user_detail(username):
    """Show a user's profile and logs."""

    user = g.user

    return render_template("users/detail.html", user=user)

@app.route("/user/edit", methods=["GET", "POST"])
def edit_user():
    """Show a user's profile and logs."""

    user = g.user

    form = EditProfileForm(obj=user)

    if form.validate_on_submit():

        try: 
            
            form.populate_obj(user)

            f = request.files['profile_photo']

            if f:

                if user.image_name:
                    
                    os.remove(f"static/images/{user.image_name}")

                if allowed_file(f.filename):
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user.image_name=filename
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("user/edit.html", form=form)

        return redirect(f"/users/{g.user.username}")

    return render_template("users/edit_profile.html", user=user, form=form)


@app.route("/user/change_password", methods=["GET", "POST"])
def change_password():
    """Change a user's password."""


    form = ChangePasswordForm()

    if form.validate_on_submit():

        curr_password = form.curr_password.data
        new_password_one = form.new_password_one.data
        new_password_two = form.new_password_two.data

        user = User.authenticate(username=g.user.username, password=curr_password)

        if user:

            if new_password_one == new_password_two:
                user = User.change_password(username = user.username, curr_password=curr_password, new_password=new_password_one)
                db.session.commit()
                flash("Password Successfully Changed!", "success")
                return redirect(f"/users/{g.user.username}")

            else:

                flash("New Passwords Must Match", "danger")
                return render_template("users/password_form.html", form=form)
        
        else:

            flash("Current password is not correct.", "danger")
            return render_template("users/password_form.html", form=form)


    return render_template("users/password_form.html", form=form)


######################################################
# Yelp API Request Routes
######################################################

@app.route("/search", methods=["POST"])
def submit_search():
    """Return search results from user query."""

    data = request.json
    term = data['category']
    location = data['city']

    params = {'term' : term, 'location' : location}

    headers = {
        'Authorization' : f'Bearer {API_KEY}'
        }

    results = requests.get(f"{API_BASE_URL}/search", headers=headers, params=params)

    resp = results.json()

    return resp

@app.route("/places/save", methods=["POST"])
@login_required
def save_place():
    """Save a place for future reference."""

    # user = User.query.get(g.id)

    if not g.user:
        flash("Log in to save places", "danger")
        return redirect("/search")

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    place_id = request.json["placeId"]
    category=request.json["category"]
    name = request.json["name"]
    url = request.json["url"]   
    image_url = request.json["image_url"]
    address_0 = request.json["address_0"] 
    address_1 = request.json["address_1"]
    price = request.json["price"]
    phone = request.json["phone"]
    rating = request.json["rating"]        

    existing_place = Place.query.get(place_id)

    # if the place isn't in the DB (most likely condition), then it can't be in the user's places
    if not existing_place:

        # create the place.
        place = Place(id=place_id, category=category, name=name, url=url, image_url=image_url, address_0=address_0, address_1=address_1, price=price, phone=phone, rating=rating)

        db.session.add(place)
        db.session.commit()
      
        # and add it to the user's places
        user.places.append(place)
        db.session.commit()

        return jsonify(message="added")

    # if the place is in the DB, but not the user's places
    if existing_place not in user.places:

        #simply add it to the user's places
        user.places.append(existing_place)
        db.session.commit()

        return jsonify(message="added")

    # if the place exists and is in the user's place, do nothing
    return jsonify(message="already saved")


@app.route("/places")
@login_required
def show_places():
    """Show a user's saved places."""

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    places = user.places

    return render_template('/users/places.html', places=places)

@app.route("/places/<id>/delete", methods=["POST"])
@login_required
def remove_place(id):
    """Remove a place from a user's saved places."""

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    place = Place.query.get(id)

    user.places.remove(place)

    db.session.commit()

    return jsonify(message="deleted")


######################################################
# Log Routes
######################################################

@app.route("/logs/<int:id>")
@login_required
def log_detail(id):
    """Display a full log."""

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    logs = user.logs

    maintenance = user.maintenance

    log = Log.query.filter_by(id=id).first()

    return render_template("users/log.html", log=log, logs=logs, maintenance=maintenance)

@app.route("/logs/all")
@login_required
def all_logs():
    """Display a list of all logs."""

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    logs = user.logs

    return render_template("users/all_logs.html", logs=logs)

@app.route("/logs/new", methods=["GET", "POST"])
@login_required
def new_log():
    """Show user new log form."""

    form = LogForm()

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    maintenance = user.maintenance

    logs = user.logs

    if form.validate_on_submit():

        title = request.form['title']
        location = request.form['location']
        mileage = request.form['mileage']
        body = request.form['text']
        date = request.form['date']
        # date=datetime.now(tz=None)

        f = request.files['photo']

        if f:
            if allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("File must be an image!!!", "danger")
                return redirect('/logs/new')
        else:
            filename = ""

        existing_location = Location.query.filter_by(location=f"{location}").first()

        if existing_location:

            log = Log(user_id=user.id, title=title, location_id=existing_location.id, mileage=mileage, text=body,date=date, image_name=filename)

        else: 
        
            new_location = Location(location=location)

            db.session.add(new_location)
            db.session.commit()

            log = Log(user_id=user.id, title=title, location_id=new_location.id, mileage=mileage, text=body,date=date, image_name=filename)
        
        db.session.add(log)
        db.session.commit()

        return redirect(f"/logs/{log.id}")

    return render_template("users/log_form.html", form=form, logs=logs, maintenance=maintenance)


@app.route("/logs/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_log(id):
    """Edit a log."""


    user = g.user

    # user = User.query.filter_by(username=username).first()

    logs = user.logs
    maintenance=user.maintenance

    log = Log.query.get(id)

    edit_form = LogForm(obj=log)

    edit_form.location.data = log.location.location

    if edit_form.validate_on_submit():

        # string from form in the form City, State
        location = request.form['location']

        # check if the submitted location is in the DB
        new_loc = Location.query.filter_by(location=f"{location}").first()
        
        # if it's there
        if new_loc:
            
            # the id is the found location's id (most likely not to change)
            loc_id = new_loc.id

        else: 
            # make a new location 
            new_location = Location(location=location)

            # and add it to the DB
            db.session.add(new_location)
            db.session.commit()

            # get the new location's id
            loc_id = new_location.id

        # edit_form.populate_obj(log)

        log.title = request.form['title']
        log.mileage = request.form['mileage']
        log.location_id = loc_id
        log.text = request.form['text']
        log.date = request.form['date']

        f = request.files['photo']

        if f and allowed_file(f.filename):
            os.remove(f'static/images/{log.image_name}')
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log.image_name=filename
        else:
            flash("Incompatible filetype", "danger")

        db.session.commit()

        return redirect(f"/logs/{id}")

    return render_template('/users/edit_log.html', form=edit_form, logs=logs, maintenance=maintenance)


@app.route("/logs/<int:id>/delete", methods=["POST"])
@login_required
def delete_log(id):
    """Delete a log."""

    log = Log.query.get(id)

    if log.image_name:
        os.remove(f"static/images/{log.image_name}")

    db.session.delete(log)

    db.session.commit()

    return redirect('/logs/new')



######################################################
# Maintenance Record Routes
######################################################

@app.route("/maintenance/<int:id>")
@login_required
def maintenance_detail(id):
    """Display a maintenance record."""

    user = g.user


    # user = User.query.filter_by(username="birel44").first()

    logs = user.logs

    maintenance = user.maintenance

    record = Maintenance.query.filter_by(id=id).first()

    return render_template("users/maintenance.html", record=record, logs=logs, maintenance=maintenance)


@app.route("/maintenance/all")
@login_required
def all_maintenance():
    """Display all maintenance records."""
    
    user = g.user

    # user = User.query.filter_by(username="birel44").first()
    maintenance = user.maintenance

    return render_template("users/all_maintenance.html", maintenance=maintenance)


@app.route("/maintenance/new", methods=["GET", "POST"])
@login_required
def maintenance_form():
    """Display new maintenance event form."""

    form = MaintenanceForm()

    user = g.user

    # user = User.query.filter_by(username="birel44").first()

    logs = user.logs
    records = user.maintenance

    if form.validate_on_submit():

        mileage = request.form['mileage']
        location = request.form['location']
        title = request.form['title']
        description = request.form['description'] 
        date = request.form['date']


        f = request.files['photo']

        if f:
            if allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                # flash("File must be an image!!!", "danger")
                return redirect('/logs/new')
        else:
            filename = ""  

        existing_location = Location.query.filter_by(location=f"{location}").first()

        if existing_location:

            maintenance = Maintenance(user_id=user.id, date=date, mileage=mileage, location_id=existing_location.id, title=title, description=description, image_name=filename)

        else: 
        
            new_location = Location(location=location)

            db.session.add(new_location)
            db.session.commit()

            maintenance = Maintenance(user_id=user.id, date=date, mileage=mileage, location_id=new_location.id, title=title, description=description, image_name=filename)
        
        db.session.add(maintenance)
        db.session.commit()

        return redirect(f"/maintenance/{maintenance.id}")

    return render_template("/users/maintenance_form.html", form=form, logs=logs, maintenance=records)


@app.route("/maintenance/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_maintenance(id):
    """Edit a maintenance record."""

    user = g.user

    # username = "birel44"

    # user = User.query.filter_by(username=username).first()

    logs = user.logs
    records = user.maintenance

    maintenance = Maintenance.query.get(id)

    edit_form = MaintenanceForm(obj=maintenance)

    edit_form.location.data = maintenance.location.location

    if edit_form.validate_on_submit():

        # string from form in the form City, State
        location = request.form['location']

        # check if the submitted location is in the DB
        existing_location = Location.query.filter_by(location=f"{location}").first()
        
        # if it's there
        if existing_location:
            
            # the id is the found location's id (most likely not to change)
            loc_id = existing_location.id

        else: 
            # make a new location 
            new_location = Location(location=location)

            # and add it to the DB
            db.session.add(new_location)
            db.session.commit()

            # get the new location's id
            loc_id = new_location.id

        maintenance.title = request.form['title']
        maintenance.mileage = request.form['mileage']
        maintenance.location_id = loc_id
        maintenance.description = request.form['description']
        maintenance.date = request.form['date']

        f = request.files['photo']

        if f and allowed_file(f.filename):
            os.remove(f'static/images/{maintenance.image_name}')
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            maintenance.image_name=filename
        else:
            flash("Incompatible filetype", "danger")

        db.session.commit()

        return redirect(f"/maintenance/{id}")

    return render_template('/users/edit_maintenance.html', form=edit_form, logs=logs, maintenance=records)


@app.route("/maintenance/<int:id>/delete", methods=["POST"])
@login_required
def delete_maintenance(id):
    """Delete a maintenance record."""

    maintenance = Maintenance.query.get(id)

    if maintenance.image_name:
        os.remove(f"static/images/{maintenance.image_name}")

    db.session.delete(maintenance)
    db.session.commit()

    return redirect("/maintenance/new")






