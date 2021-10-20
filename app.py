from flask import Flask, render_template, request, url_for, redirect, flash, session, g, jsonify
from forms import BusinessSearchForm, LogForm, MaintenanceForm
from key import API_KEY
import requests
from datetime import datetime

import functools

from models import db, Location, connect_db, User, Log, Maintenance, Place

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://api.yelp.com/v3/businesses"

app = Flask(__name__)

app.config['SECRET_KEY'] = "CanadianGeese1195432"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///greenflash'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)


##############################################################################
# User signup/login/logout

# LOGIN Decorator
# def login_required(func):
#     """Make sure user is logged in before proceeding."""
#     @functools.wraps(func)
#     def wrapper_login_required(*args, **kwargs):
#         if not g.user:
#             flash("Access unauthorized.", "dange
#             return redirect(url_for("login", next=request.url))
#         return func(*args, **kwargs)
#     return wrapper_login_required

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

    user = User.query.filter_by(username=f"{username}").first()

    form = LogForm()

    logs = user.logs

    maintenance=user.maintenance

    return render_template("users/detail.html", user=user, logs=logs, form=form, maintenance=maintenance)



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
def save_place():
    """Save a place for future reference."""

    user = User.query.filter_by(username="birel44").first()

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
def show_places():
    """Show a user's saved places."""

    user = User.query.filter_by(username="birel44").first()

    places = user.places

    return render_template('/users/places.html', places=places)


@app.route("/places/<id>/delete", methods=["POST"])
def remove_place(id):
    """Remove a place from a user's saved places."""

    user = User.query.filter_by(username="birel44").first()

    place = Place.query.get(id)

    user.places.remove(place)

    db.session.commit()

    return jsonify(message="deleted")


######################################################
# Log Routes
######################################################

@app.route("/logs/<int:id>")
def log_detail(id):
    """Display a full log."""

    user = User.query.filter_by(username="birel44").first()

    logs = user.logs

    maintenance = user.maintenance

    log = Log.query.filter_by(id=id).first()

    return render_template("users/log.html", log=log, logs=logs, maintenance=maintenance)


@app.route("/logs/all")
def all_logs():
    """Display a list of all logs."""

    user = User.query.filter_by(username="birel44").first()

    logs = user.logs

    return render_template("users/all_logs.html", logs=logs)


@app.route("/logs/new", methods=["GET", "POST"])
def new_log():
    """Show user new log form."""

    form = LogForm()

    username = "birel44"

    user = User.query.filter_by(username="birel44").first()

    maintenance = user.maintenance

    logs = user.logs

    if form.validate_on_submit():

        title = request.form['title']
        location = request.form['location']
        mileage = request.form['mileage']
        body = request.form['text']
        date=datetime.now(tz=None)

        existing_location = Location.query.filter_by(location=f"{location}").first()

        if existing_location:

            log = Log(user_id=user.id, title=title, location_id=existing_location.id, mileage=mileage, text=body,date=date)

        else: 
        
            new_location = Location(location=location)

            db.session.add(new_location)
            db.session.commit()

            log = Log(user_id=user.id, title=title, location_id=new_location.id, mileage=mileage, text=body,date=date)
        
        db.session.add(log)
        db.session.commit()

        return redirect(f"/logs/{log.id}/edit")

    return render_template("users/log_form.html", form=form, logs=logs, maintenance=maintenance)


@app.route("/logs/<int:id>/edit", methods=["GET", "POST"])
def edit_log(id):
    """Edit a log."""

    username = "birel44"

    user = User.query.filter_by(username=username).first()

    logs = user.logs
    maintenance=user.maintenance


    log = Log.query.get(id)

    # loc = Location.query.get(log.location.id)

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
        log.date = datetime.now(tz=None)

        # db.session.add(log)
        db.session.commit()

        return redirect(f"/logs/{id}/edit")

    return render_template('/users/edit_log.html', form=edit_form, logs=logs, maintenance=maintenance)


@app.route("/logs/<int:id>/delete", methods=["POST"])
def delete_log(id):
    """Delete a log."""

    log = Log.query.get(id)

    db.session.delete(log)

    db.session.commit()

    return redirect('/users/birel44')



######################################################
# Maintenance Record Routes
######################################################

@app.route("/maintenance/<int:id>")
def maintenance_detail(id):
    """Display a maintenance record."""

    user = User.query.filter_by(username="birel44").first()

    logs = user.logs

    maintenance = user.maintenance

    record = Maintenance.query.filter_by(id=id).first()

    return render_template("users/maintenance.html", record=record, logs=logs, maintenance=maintenance)


@app.route("/maintenance/all")
def all_maintenance():
    """Display all maintenance records."""

    user = User.query.filter_by(username="birel44").first()
    maintenance = user.maintenance

    return render_template("users/all_maintenance.html", maintenance=maintenance)


@app.route("/maintenance/new", methods=["GET", "POST"])
def maintenance_form():
    """Display new maintenance event form."""

    form = MaintenanceForm()

    user = User.query.filter_by(username="birel44").first()

    logs = user.logs
    records = user.maintenance

    if form.validate_on_submit():

        date = request.form['date']
        mileage = request.form['mileage']
        location = request.form['location']
        title = request.form['title']
        description = request.form['description']   

        existing_location = Location.query.filter_by(location=f"{location}").first()

        if existing_location:

            maintenance = Maintenance(user_id=user.id, date=date, mileage=mileage, location_id=existing_location.id, title=title, description=description)

        else: 
        
            new_location = Location(location=location)

            db.session.add(new_location)
            db.session.commit()

            maintenance = Maintenance(user_id=user.id, date=date, mileage=mileage, location_id=new_location.id, title=title, description=description)
        
        db.session.add(maintenance)
        db.session.commit()

        return redirect("/users/birel44")

    return render_template("/users/maintenance_form.html", form=form, logs=logs, maintenance=records)


@app.route("/maintenance/<int:id>/edit", methods=["GET", "POST"])
def edit_maintenance(id):
    """Edit a maintenance record."""

    username = "birel44"

    user = User.query.filter_by(username=username).first()

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

        db.session.commit()

        return redirect("/users/birel44")

    return render_template('/users/edit_maintenance.html', form=edit_form, logs=logs, maintenance=records)


@app.route("/maintenance/<int:id>/delete", methods=["POST"])
def delete_maintenance(id):
    """Delete a maintenance record."""

    maintenance = Maintenance.query.get(id)

    db.session.delete(maintenance)
    db.session.commit()

    return redirect("/users/birel44")





# @app.before_request
# def add_user_to_g():
#     """If logged in, add current user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id

# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]

# @app.route('/signup', methods=["GET", "POST"])
# def signup():
#     """Handle user signup.

#     Create new user and add to DB. Redirect to home page.

#     If form not valid, present form.

#     If there is already a user with that username: flash message
#     and re-present form.
#     """

#     form = UserAddForm()

#     if form.validate_on_submit():
#         try: 
#             user = User.signup(
#                 username=form.username.data,
#                 password=form.password.data,
#                 first_name=form.first_name.data,
#                 last_name=form.last_name.data
#                 )
#             db.session.commit()
        
#         except IntegrityError:
#             flash("Username already taken", "danger")
#             return render_template("users/signup.html", form=form)

#         do_login(user)

#         return redirect(url_for("home"))

#     else:
#         return render_template('user/signup.html', form=form)

# @app.route('/login', methods=["POST", "GET"])
# def login():
#     """Handle user login."""

#     form = LoginForm()

#     if form.validate_on_submit():
#         user = User.authenticate(form.username.data,
#                                 form.password.data)

#         next_url = request.form.get('next')

#         if user:
#             do_login(user)
#             flash(f"Hello, {user.username}!", "success")

#             if next_url:
#                 return redirect(next_url)

#             else:
#                 return redirect(url_for("home"))

#         flash("Invalid credentials.", "danger")

#     return render_template('users/login.html', form=form)

# @app.route('/logout')
# def logout():
#     """Handle user logout."""

#     do_logout()

#     flash("Logout successful!", 'success')

#     return redirect(url_for("login"))
    
