from app import app
from models import db, User, Log, Location, Maintenance, Image, Place, UsersPlaces
from datetime import datetime


db.drop_all()
db.create_all()

me = User(
    username="birel44",
    first_name="Peter",
    last_name="Darinzo"
)

db.session.add(me)
db.session.commit()

salt_lake_city = Location(
    location="Salt Lake City, UT"
)
las_vegas = Location(
    location="Las Vegas, NV"
)
sherman = Location(
    location="Sherman, CT"
)

ames = Location(
    location="Ames, IA"
)

db.session.add(salt_lake_city)
db.session.add(las_vegas)
db.session.add(sherman)
db.session.add(ames)
db.session.commit()


first_log = Log(
    user_id=me.id,
    date=datetime.now(tz=None),
    location_id=salt_lake_city.id,
    mileage=56000,
    title="Setting Off",
    text="Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit a."
)

third_log = Log(
    user_id=me.id,
    date=datetime.now(tz=None),
    location_id=sherman.id,
    mileage=56800,
    title="Second Log.",
    text="At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil imped."
)


fourth_log = Log(
    user_id=me.id,
    date=datetime.now(tz=None),
    location_id=ames.id,
    mileage=57500,
    title="Where the heck am I?",
    text="At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil."
)


second_log = Log(
    user_id=me.id,
    date=datetime.now(tz=None),
    location_id=las_vegas.id,
    mileage=58000,
    title="Lost it all in Vegas.",
    text="At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga."
)



db.session.add(first_log)
db.session.add(second_log)
db.session.add(third_log)
db.session.add(fourth_log)

db.session.commit()

first_maintenance = Maintenance(
    user_id=me.id,
    date="Oct 12 2021",
    mileage=56123,
    location_id=salt_lake_city.id,
    title="Oil",
    description="Changed oil to 5W30. Checked tire pressure."
)


second_maintenance = Maintenance(
    user_id=me.id,
    date="Oct 15, 2021",
    mileage=57123,
    location_id=sherman.id,
    title="Elbow Grease.",
    description="Liberal application of elbow grease."
)

db.session.add(first_maintenance)
db.session.add(second_maintenance)
db.session.commit()

