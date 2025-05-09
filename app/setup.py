from app import db
from app import create_app  # if you're using an app factory
from app.models import *    # make sure your User model is imported

app = create_app()
with app.app_context():
    db.create_all()
