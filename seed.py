"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Rating
from model import Movie

from model import connect_to_db, db
from server import app
import datetime



def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for i, row in enumerate(open("seed_data/u.user")):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

        if i % 100 == 0:
            print i

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    Movie.query.delete()

    for i, row in enumerate(open("seed_data/u.item")):
        row = row.strip()
        full_row = row.split("|")

        movie_id = full_row[0]
        title_ugly = full_row[1]
        title_ugly = title_ugly.split()
        if title_ugly[-1][-1] == ")":
            title_pretty = title_ugly[:-1]
            title =" ".join(title_pretty)
        else:
            title_pretty = title_ugly
            title =" ".join(title_pretty)

        release_ugly = full_row[2]
        if release_ugly:
            release_pretty = datetime.datetime.strptime(release_ugly, "%d-%b-%Y")
        else:
            release_pretty = None

        imdb = full_row[4]

        movie = Movie(movie_id=movie_id, title=title, release_at=release_pretty,
                      imdb_url=imdb)

        db.session.add(movie)

        if i % 100 == 0:
            print i

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    Rating.query.delete()

    # Read u.user file and insert data
    for i, row in enumerate(open("seed_data/u.data")):
        row = row.strip().split("\t")
        user_id = int(row[0])
        movie_id = int(row[1])
        score = int(row[2])

        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)

        # We need to add to the session or it won't ever be stored
        db.session.add(rating)

        if i % 100 == 0:
            print i

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
    
