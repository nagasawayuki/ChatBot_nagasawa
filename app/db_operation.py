from .db import db
from .models.review import *
from .models.user import *


def message_upload(message):
    db.session.add(message)
    db.session.commit()


def message_filter_get(sender_id, limit):
    return db.session.query(Message.user_message, Message.ai_response).filter(Message.sender_id == sender_id).order_by(Message.timestamp.desc()).limit(limit).all()


def review_upload(review):
    db.session.add(review)
    db.session.commit()


def review_delate(message_id):
    db.session.query(Review).filter(Review.message_id == message_id).delete()
    db.session.commit()


def user_get(username):
    return User.query.filter_by(username=username).first()


def user_all_delete():
    db.session.query(User).delete()
    db.session.commit()


def user_upload(user):
    db.session.add(user)
    db.session.commit()
