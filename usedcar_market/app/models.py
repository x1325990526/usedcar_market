from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    username = db.Column(db.String(40), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    cars = db.relationship("Car", backref="seller", lazy=True)
    favorites = db.relationship("Favorite", backref="user", lazy=True)

    def set_password(self, pw: str):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password_hash, pw)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(40), index=True, nullable=False)
    model = db.Column(db.String(60), nullable=False)
    year = db.Column(db.Integer, index=True, nullable=False)
    mileage_km = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, index=True, nullable=False)
    city = db.Column(db.String(40), index=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)

    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    messages = db.relationship("Message", backref="car", lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="car", lazy=True, cascade="all, delete-orphan")

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "car_id", name="uq_user_car_fav"),)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User")
