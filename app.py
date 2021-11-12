import os, json, boto3
import re
import shutil
import functools
import requests
from flask import Flask, render_template, request, url_for, redirect, flash, session, g, jsonify
from sqlalchemy.sql.expression import delete
from forms import BusinessSearchForm, ChangePasswordForm, EditProfileForm, LogForm, MaintenanceForm, SignupForm, LoginForm, images
from models import db, Location, connect_db, User, Log, Maintenance, Place
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_uploads import configure_uploads
from s3_functions import load_image, upload_file, delete_image

load_dotenv() #take environmental API_KEY variable from .env

app = Flask(__name__)

# load information into app
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET')

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://api.yelp.com/v3/businesses"
UPLOAD_FOLDER = "uploads"
RATINGS = {
    "0": "regular_0.png",
    "1.0": "regular_1.png",
    "1.5": "regular_1_half.png",
    "2.0": "regular_2.png",
    "2.5": "regular_2_half.png",
    "3.0": "regular_3.png",
    "3.5": "regular_3_half.png",
    "4.0": "regular_4.png",
    "4.5": "regular_4_half.png",
    "5.0": "regular_5.png"
    }


#
# The following code provided by Heroku as a way of ensuring connection to sqlalchemy versions 1.4 and later
# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
#
uri = os.getenv('DATABASE_URL', 'postgresql:///greenflash')  
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///greenflash')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'CanadianGeese1195432')
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['UPLOADED_IMAGES_DEST'] = UPLOAD_FOLDER
os.environ.setdefault('S3_USE_SIGV4', 'True')


connect_db(app)

configure_uploads(app, (images))


##############################################################################
# User signup/login/logout

# LOGIN Decorator
def login_required(func):
    """Make sure user is logged in before proceeding."""
    @functools.wraps(func)
    def wrapper_login_required(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized - Please log in or sign up.", "danger")
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
                email=form.email.data)
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/signup.html", form=form)

        f = request.files['photo']
        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            upload_file(f"uploads/{filename}", S3_BUCKET)
            user.image_name=filename
            db.session.commit()

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

    if g.user:
        return redirect("/home")
    form = BusinessSearchForm()
    return render_template("home-anon.html", form=form)


@app.route("/home")
def home():
    """Home page which presents business search form."""

    form = BusinessSearchForm()
    return render_template('home.html', form=form)


@app.route("/users/profile")
def user_detail():
    """Show a user's credentials, bio, and profile image."""

    user = g.user

    image = user.image_name

    image_url = load_image(S3_BUCKET, image)

    return render_template("users/detail.html", user=user, url=image_url)


@app.route("/users/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    """Edit a user's credentials, bio, and profile image."""

    user = g.user
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        try: 
            form.populate_obj(user)
            f = request.files['photo']
            if f:
                if user.image_name:
                        profile_image = user.image_name
                        delete_image(S3_BUCKET, profile_image)

                filename = secure_filename(f.filename)
                f.save(os.path.join(UPLOAD_FOLDER, f'{filename}'))
                upload_file(f"uploads/{filename}", S3_BUCKET)
                user.image_name=filename
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/edit_profile.html", form=form)

        return redirect(url_for("user_detail"))
        
    return render_template("users/edit_profile.html", user=user, form=form)


@app.route("/users/change_password", methods=["GET", "POST"])
@login_required
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
                return redirect(url_for("user_detail"))
            else:
                flash("New Passwords Must Match", "danger")
                return render_template("users/password_form.html", form=form)
        else:
            flash("Current password is not correct.", "danger")
            return render_template("users/password_form.html", form=form)

    return render_template("users/password_form.html", form=form)


@app.route("/users/delete/confirm", methods=["GET"])
@login_required
def delete_confirm():
    """Confirm account deletion."""

    return render_template('users/account_delete.html')


@app.route("/users/delete", methods=["GET", "POST"])
@login_required
def delete_user():
    """Delete user."""

    do_logout()
    user = g.user
    logs = user.logs
    records = user.maintenance

    for log in logs:
        delete_image(S3_BUCKET, log.image_name)
    
    for record in records:
        delete_image(S3_BUCKET, record.image_name)

    profile_image = user.image_name
    delete_image(S3_BUCKET, profile_image)
    db.session.delete(user)
    db.session.commit()
    flash("Account successfully deleted.", "danger")
    return redirect(url_for("signup"))


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
        'Authorization' : (f'Bearer ' + app.config['API_KEY'])}
    results = requests.get(f"{API_BASE_URL}/search", headers=headers, params=params)
    resp = results.json()

    return resp


@app.route("/places/save", methods=["POST"])
def save_place():
    """Save a place for future reference.

    If the place's ID is not in the DB (most likely condition), it is known that it is not in the user's places. If so the place is then created, and added to the user's places. Otherwise, the place may be in the DB, but not the user's. If so, the place is simply added to the user's places. If the place is in the DB, and the user's places, then the save button was clicked in error, do nothing."""

    if not g.user:
        return jsonify(message="not added")
    user = g.user

    place_id = request.json["placeId"]
    existing_place = Place.query.get(place_id)

    if not existing_place:
        place = Place(id=place_id)
        db.session.add(place)
        db.session.commit()
        user.places.append(place)
        db.session.commit()
        return jsonify(message="added")
    if existing_place not in user.places:
        user.places.append(existing_place)
        db.session.commit()
        return jsonify(message="added")
    return jsonify(message="already saved")


@app.route("/places", methods=["GET"])
@login_required
def show_places():
    """Show a user's saved places."""

    place_ids = [place.id for place in g.user.places]
    places = []
    headers = {
        'Authorization' : (f'Bearer ' + app.config['API_KEY'])}
        
    for place_id in place_ids:
        res = requests.get(f"{API_BASE_URL}/{place_id}", headers=headers)

        business = res.json()
    
        name = business["name"]
        image_url = business["image_url"]
        category = (business["categories"])[0]["title"]
        address_0 = (business["location"])["display_address"][0]
        address_1 = (business["location"])["display_address"][1]
        url = business["url"]
        rating = business["rating"]
        image = RATINGS[f"{rating}"]
        path = f"static/images/stars/{image}"

        try:
            phone = business["phone"]
        except KeyError:
            phone = ""

        try:
            price = business["price"]
        except KeyError:
            price = ""

        placeDict = {
            "place_id" : place_id,
            "name": name,
            "image_url" : image_url,
            "category" : category,
            "price": price,
            "phone" : phone,
            "address_0": address_0,
            "address_1" : address_1,
            "url": url,
            "rating": path
        }

        places.append(placeDict)

    return render_template('/users/places.html', places=places)


@app.route("/places/<id>/delete", methods=["POST"])
@login_required
def remove_place(id):
    """Remove a place from a user's saved places."""

    user = g.user
    place = Place.query.get_or_404(id)
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
    log_ids = [log.id for log in user.logs]

    if id not in log_ids:
        flash("UNAUTHORIZED.", "danger")
        return redirect("/logs/new")

    logs = Log.query.filter_by(user_id=g.user.id).order_by(desc(Log.date)).limit(5)
    maintenance = Maintenance.query.filter_by(user_id=user.id).order_by(desc(Maintenance.date)).limit(5)
    log = Log.query.filter_by(id=id).first()
    image = log.image_name
    if image:
        image_url = load_image(S3_BUCKET, image)

    return render_template("users/log.html", user=user, log=log, logs=logs, maintenance=maintenance, url=image_url)


@app.route("/logs/all")
@login_required
def all_logs():
    """Display a list of all of user's logs."""

    user = g.user
    logs = user.logs
    return render_template("users/all_logs.html", logs=logs)


@app.route("/logs/new", methods=["GET", "POST"])
@login_required
def new_log():
    """Show user new log form."""

    form = LogForm()
    user = g.user
    maintenance = Maintenance.query.filter_by(user_id=user.id).order_by(desc(Maintenance.date)).limit(5)
    logs = Log.query.filter_by(user_id=g.user.id).order_by(desc(Log.date)).limit(5)

    if form.validate_on_submit():
        title = request.form['title']
        location = request.form['location']
        mileage = request.form['mileage']
        body = request.form['text']
        date = request.form['date']
        f = request.files['photo']

        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, f'{filename}'))
            upload_file(f"uploads/{filename}", S3_BUCKET)

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
    log_ids = [log.id for log in user.logs]

    if id not in log_ids:
        flash("UNAUTHORIZED.", "danger")
        return redirect("/logs/new")

    logs = Log.query.filter_by(user_id=g.user.id).order_by(desc(Log.date)).limit(5)
    maintenance = Maintenance.query.filter_by(user_id=user.id).order_by(desc(Maintenance.date)).limit(5)
    log = Log.query.get_or_404(id)
    edit_form = LogForm(obj=log)
    edit_form.location.data = log.location.location

    if edit_form.validate_on_submit():
        location = request.form['location']
        existing_location = Location.query.filter_by(location=f"{location}").first()
        if existing_location:
            loc_id = existing_location.id
        else: 
            new_location = Location(location=location)
            db.session.add(new_location)
            db.session.commit()
            loc_id = new_location.id

        log.title = request.form['title']
        log.mileage = request.form['mileage']
        log.location_id = loc_id
        log.text = request.form['text']
        log.date = request.form['date']
        f = request.files['photo']

        if f:
            if log.image_name:
                delete_image(S3_BUCKET, log.image_name)
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, f'{filename}'))
            upload_file(f"uploads/{filename}", S3_BUCKET)
            log.image_name=filename

        db.session.commit()

        return redirect(url_for("log_detail", id=id))

    return render_template('/users/edit_log.html', form=edit_form, logs=logs, maintenance=maintenance)


@app.route("/logs/<int:id>/delete/confirm")
@login_required
def delete_log_confirm(id):
    """Confirm log deletion."""

    log = Log.query.get_or_404(id)
    return render_template('/users/log_delete.html', log=log)


@app.route("/logs/<int:id>/delete", methods=["POST"])
@login_required
def delete_log(id):
    """Delete a log."""

    user = g.user
    log_ids = [log.id for log in user.logs]
    if id not in log_ids:
        flash("UNAUTHORIZED.", "danger")
        return redirect("/logs/new")
    log = Log.query.get_or_404(id)
    if log.image_name:
        delete_image(S3_BUCKET, log.image_name)
    db.session.delete(log)
    db.session.commit()
    return redirect("/logs/new")



######################################################
# Maintenance Record Routes
######################################################

@app.route("/maintenance/<int:id>")
@login_required
def maintenance_detail(id):
    """Display a maintenance record."""

    user = g.user
    maintenance_ids = [record.id for record in user.maintenance]

    if id not in maintenance_ids:
        flash("UNAUTHORIZED.", "danger")
        return redirect("/maintenance/new")

    logs = Log.query.filter_by(user_id=user.id).order_by(desc(Log.date)).limit(5)
    maintenance = Maintenance.query.filter_by(user_id=user.id).order_by(desc(Maintenance.date)).limit(5)
    record = Maintenance.query.filter_by(id=id).first()
    image = record.image_name
    if image:
            image_url = load_image(S3_BUCKET, image)

    return render_template("users/maintenance.html", user=user, record=record, logs=logs, maintenance=maintenance, url=image_url)


@app.route("/maintenance/all")
@login_required
def all_maintenance():
    """Display all maintenance records."""
    
    user = g.user
    maintenance = user.maintenance
    return render_template("users/all_maintenance.html", maintenance=maintenance)


@app.route("/maintenance/new", methods=["GET", "POST"])
@login_required
def maintenance_form():
    """Display new maintenance event form."""

    form = MaintenanceForm()
    user = g.user
    logs = Log.query.filter_by(user_id=g.user.id).order_by(desc(Log.date)).limit(5)
    records = Maintenance.query.filter_by(user_id=user.id).order_by(desc(Maintenance.date)).limit(5)

    if form.validate_on_submit():
        mileage = request.form['mileage']
        location = request.form['location']
        title = request.form['title']
        description = request.form['description'] 
        date = request.form['date']
        f = request.files['photo']

        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, f'{filename}'))
            upload_file(f"uploads/{filename}", S3_BUCKET)

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
    maintenance_ids = [record.id for record in user.maintenance]

    if id not in maintenance_ids:
        flash("UNAUTHORIZED.", "danger")
        return redirect("/maintenance/new")

    logs = Log.query.filter_by(user_id=g.user.id).order_by(desc(Log.date)).limit(5)
    records = Maintenance.query.filter_by(user_id=user.id).order_by(desc(Maintenance.date)).limit(5)
    maintenance = Maintenance.query.get_or_404(id)
    edit_form = MaintenanceForm(obj=maintenance)
    edit_form.location.data = maintenance.location.location

    if edit_form.validate_on_submit():
        location = request.form['location']
        existing_location = Location.query.filter_by(location=f"{location}").first()
        if existing_location:
            loc_id = existing_location.id
        else: 
            new_location = Location(location=location)
            db.session.add(new_location)
            db.session.commit()
            loc_id = new_location.id

        maintenance.title = request.form['title']
        maintenance.mileage = request.form['mileage']
        maintenance.location_id = loc_id
        maintenance.description = request.form['description']
        maintenance.date = request.form['date']
        f = request.files['photo']

        if f:
            if maintenance.image_name:                                
                delete_image(S3_BUCKET, maintenance.image_name)
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, f'{filename}'))
            upload_file(f"uploads/{filename}", S3_BUCKET)
            maintenance.image_name=filename

        db.session.commit()

        return redirect(f"/maintenance/{id}")

    return render_template('/users/edit_maintenance.html', form=edit_form, logs=logs, maintenance=records)


@app.route("/maintenance/<int:id>/delete/confirm")
@login_required
def delete_maintenance_confirm(id):
    """Confirm log deletion."""

    maintenance = Maintenance.query.get_or_404(id)
    return render_template('/users/maintenance_delete.html', maintenance=maintenance)


@app.route("/maintenance/<int:id>/delete", methods=["POST"])
@login_required
def delete_maintenance(id):
    """Delete a maintenance record."""

    user = g.user
    maintenance_ids = [record.id for record in user.maintenance]

    if id not in maintenance_ids:
        flash("UNAUTHORIZED.", "danger")
        return redirect("/maintenance/new")

    maintenance = Maintenance.query.get_or_404(id)

    if maintenance.image_name:
        delete_image(S3_BUCKET, maintenance.image_name)
    db.session.delete(maintenance)
    db.session.commit()

    return redirect("/maintenance/new")



# Main code
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
