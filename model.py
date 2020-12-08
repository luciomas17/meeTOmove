from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email

from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    profile_pic = db.Column(db.String(255))
    reviews = db.relationship('Review', backref='reviewed')
    created_events = db.relationship('Event', backref='creator')
    joined_events = db.relationship('JoinedEvent', backref='user')
    favourite_sports = db.relationship('FavouriteSport', backref='user')

    def __repr__(self):
        return '<User %r>' % self.name


class JoinedEvent(db.Model):
    __tablename__ = 'joined_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return '<Joined Event %r>' % self.id


class FavouriteSport(db.Model):
    __tablename__ = 'favourite_sports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'))

    def __repr__(self):
        return '<Favourite Sport %r>' % self.id


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    town_id = db.Column(db.Integer, db.ForeignKey('towns.id'))
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'))
    place = db.Column(db.String(255), nullable=False)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    wanted_players_number = db.Column(db.Integer, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_added = db.Column(db.Date, nullable=False)
    reviews = db.relationship('Review', backref='event')
    joined_users = db.relationship('JoinedEvent', backref='event')

    def __repr__(self):
        return '<Event %r>' % self.id


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewer_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    skills = db.Column(db.Float, nullable=False)
    sportsmanship = db.Column(db.Float, nullable=False)
    willingness = db.Column(db.Float, nullable=False)
    reliability = db.Column(db.Float, nullable=False)
    punctuality = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(255))
    date_added = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return '<Review %r>' % self.id


class Town(db.Model):
    __tablename__ = 'towns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    events = db.relationship('Event', backref='town')

    def __repr__(self):
        return '<Town %r>' % self.name


class Sport(db.Model):
    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(255))
    events = db.relationship('Event', backref='sport')
    users = db.relationship('FavouriteSport', backref='sport')

    def __repr__(self):
        return '<Sport %r>' % self.name


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return "<Role %r>" % self.name


class SearchEvent(FlaskForm):
    town = SelectField()
    sport = SelectField()
    submit = SubmitField('Search')


class SignInForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired(), Length(min=3, max=255)])
    remember = BooleanField()
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    surname = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired(), Length(min=3, max=255)])
    submit = SubmitField('Sign Up')
