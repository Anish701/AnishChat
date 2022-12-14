from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Table
from datetime import datetime

#table of followers, used to determine friends
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#Read Times table, used to determine msg notifications and times msgs were last opened btwn users
class ReadTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer)
    readDate = db.Column(db.DateTime)

#Not Applicable//Only used as Template
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#Messages, id of itself, sender, and recipient, with text body, and timestamp
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)

#Users and all information associated with them, ex: unique ID
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    #creates relationship between User and ReadTime
    readTimes = db.relationship('ReadTime')

    followed = db.relationship('User', 
                               secondary=followers, 
                               primaryjoin=(followers.c.follower_id == id), 
                               secondaryjoin=(followers.c.followed_id == id), 
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')

    #MESSAGES
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    #FRIEND FUNCTIONS
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    #MESSAGES FUNCTION
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()
    
    #determines number of unseen messages for given user, with a particular recipient
    def new_msgs(self):
        newMsgs = 0
        for person in self.followed:
            if person.is_following(self):
                txmp = ReadTime.query.filter_by(recipient_id=self.id, sender_id=person.id).first()
                for msg in self.messages_received:
                    if msg.sender_id == person.id and msg.timestamp > txmp.readDate:
                        newMsgs += 1
        return newMsgs