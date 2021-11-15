import os
from app import app
from models import db, User, Log, Location, Maintenance


db.drop_all()
db.create_all()

user = User.signup(
    username="MrTurtle",
    email="MrTurtle@gmail.com",
    password="whattheshell",
)

db.session.commit()

salt_lake_city = Location(
    location="Salt Lake City, UT")

las_vegas = Location(
    location="Las Vegas, NV")

sherman = Location(
    location="Sherman, CT")

ames = Location(
    location="Ames, IA")

db.session.add(salt_lake_city)
db.session.add(las_vegas)
db.session.add(sherman)
db.session.add(ames)
db.session.commit()

first_log = Log(
    user_id=user.id,
    date='2021-5-1',
    location_id=salt_lake_city.id,
    mileage=56000,
    title="Setting Off",
    text="Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit a.",
    image_name="")

second_log = Log(
    user_id=user.id,
    date='2020-6-9',
    location_id=las_vegas.id,
    mileage=58000,
    title="Lost it all in Vegas.",
    text="At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga.",
    image_name="")

third_log = Log(
    user_id=user.id,
    date='2020-8-9',
    location_id=sherman.id,
    mileage=56800,
    title="Second Log.",
    text="At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil imped.",
    image_name="")


fourth_log = Log(
    user_id=user.id,
    date='2020-9-9',
    location_id=ames.id,
    mileage=57500,
    title="Where the heck am I?",
    text="At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil.",
    image_name="")

db.session.add(first_log)
db.session.add(second_log)
db.session.add(third_log)
db.session.add(fourth_log)

db.session.commit()

first_maintenance = Maintenance(
    user_id=user.id,
    date="2021-10-12",
    mileage=56123,
    location_id=salt_lake_city.id,
    title="Oil",
    description="Changed oil to 5W30. Checked tire pressure.",
    image_name="")


second_maintenance = Maintenance(
    user_id=user.id,
    date="2021-10-14",
    mileage=57123,
    location_id=sherman.id,
    title="Elbow Grease.",
    description="Liberal application of elbow grease.",
    image_name="")

db.session.add(first_maintenance)
db.session.add(second_maintenance)
db.session.commit()

