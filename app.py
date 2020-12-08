from flask import Flask, render_template, redirect, url_for, session, request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '123412341234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from model import User, Review, FavouriteSport, Town, Sport, Event
from model import SearchEvent, SignInForm, SignUpForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    search_event_form = SearchEvent()
    towns = Town.query.all()
    sports = Sport.query.all()
    if search_event_form.is_submitted():
        session['town_id'] = search_event_form.town.data
        session['sport_id'] = search_event_form.sport.data
        return redirect("events")
    return render_template('index.html', search_event_form=search_event_form, towns=towns, sports=sports)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    sign_in_form = SignInForm()
    if sign_in_form.validate_on_submit():
        user_info = User.query.filter(User.email == sign_in_form.email.data).first()
        if user_info and bcrypt.check_password_hash(user_info.password, sign_in_form.password.data):
            session['user_id'] = user_info.id
            session['user_name'] = user_info.name
            session['user_surname'] = user_info.surname
            session['user_email'] = user_info.email
            if user_info.profile_pic is None:
                session['user_pic'] = "img/users/null.png"
            else:
                session['user_pic'] = "img/users/" + user_info.profile_pic
            if not sign_in_form.remember.data:
                session['clear'] = True
            return redirect(url_for('index'))

    return render_template('signin.html', sign_in_form=sign_in_form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    sign_up_form = SignUpForm()
    if sign_up_form.validate_on_submit():
        password = bcrypt.generate_password_hash(sign_up_form.password.data).encode('utf-8')
        new_user = User(email=sign_up_form.email.data,
                        password=password,
                        name=sign_up_form.name.data,
                        surname=sign_up_form.surname.data,
                        role_id=1)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('signup.html', sign_up_form=sign_up_form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/handle_sports_form', methods=['GET', 'POST'])
def handle_sports_form():
    if FavouriteSport.query.filter(FavouriteSport.user_id == session['user_id']).delete() > 0:
        FavouriteSport.query.filter(FavouriteSport.user_id == session['user_id']).delete()
        db.session.commit()
    for temp in request.form.getlist('sports_checkbox'):
        new_fav_sport = FavouriteSport(user_id=session['user_id'], sport_id=temp)
        db.session.add(new_fav_sport)
        db.session.commit()
    return redirect(url_for("myaccount"))


@app.route('/myaccount', methods=['GET', 'POST'])
def myaccount():
    if session.get('user_id'):
        sports = Sport.query.all()

        favourite_sports = FavouriteSport.query.filter(FavouriteSport.user_id == session['user_id']).all()
        if len(favourite_sports) == 0:
            favourite_sports = None

        skills = 0
        sportsmanship = 0
        willingness = 0
        reliability = 0
        punctuality = 0
        reviews = Review.query.filter(Review.reviewed_id == session['user_id']).all()
        if len(reviews) > 0:
            for review in reviews:
                skills = skills + review.skills
                sportsmanship = sportsmanship + review.sportsmanship
                willingness = willingness + review.willingness
                reliability = reliability + review.reliability
                punctuality = punctuality + review.punctuality
            skills = skills / len(reviews)
            sportsmanship = sportsmanship / len(reviews)
            willingness = willingness / len(reviews)
            reliability = reliability / len(reviews)
            punctuality = punctuality / len(reviews)
            player_score = (skills + sportsmanship + willingness + reliability + punctuality) / 5

            return render_template('myaccount.html', player_score=player_score, skills=skills,
                                   sportsmanship=sportsmanship, willingness=willingness,
                                   reliability=reliability, punctuality=punctuality,
                                   favourite_sports=favourite_sports, sports=sports)
        else:
            return render_template('myaccount.html', player_score="n.a.", skills="n.a.",
                                   sportsmanship="n.a.", willingness="n.a.",
                                   reliability="n.a.", punctuality="n.a.",
                                   favourite_sports=favourite_sports, sports=sports)
    else:
        return redirect(url_for('signin'))


@app.route('/reviews')
def reviews():
    if session.get('user_id'):
        users = User.query.all()
        reviews_made = Review.query.filter(Review.reviewer_id == session['user_id']).order_by(Review.date_added.desc()).all()
        reviews_received = Review.query.filter(Review.reviewed_id == session['user_id']).order_by(Review.date_added.desc()).all()
        return render_template('reviews.html', users=users, reviews_made=reviews_made, reviews_received=reviews_received)
    else:
        return redirect(url_for('signin'))


@app.route('/myevents')
def myevents():
    if session.get('user_id'):
        return render_template('myevents.html')
    else:
        return redirect(url_for('signin'))


@app.route('/messages')
def messages():
    if session.get('user_id'):
        return render_template('messages.html')
    else:
        return redirect(url_for('signin'))


@app.route('/events', methods=['GET', 'POST'])
def events():
    towns = Town.query.all()
    sports = Sport.query.all()
    events = Event.query.order_by(Event.date_start.asc()).all()

    if session.get('town_id') and session.get('sport_id'):
        if session['sport_id'] == "all":
            events = Event.query.filter(Event.town_id == session['town_id']).order_by(Event.date_start.asc()).all()
        else:
            events = Event.query.filter(Event.town_id == session['town_id'], Event.sport_id == session['sport_id']).order_by(Event.date_start.asc()).all()

    filter_event_form = SearchEvent()
    if filter_event_form.is_submitted():
        session['town_id'] = filter_event_form.town.data
        session['sport_id'] = filter_event_form.sport.data
        return redirect("events")

    print session.get('town_id')
    print session.get('sport_id')
    return render_template('events.html', filter_event_form=filter_event_form, towns=towns, sports=sports, events=events)


@app.before_first_request
def setup():
    db.create_all()
    db.session.commit()


@app.before_request
def make_session_permanent():
    if session.get('clear'):
        if session['clear']:
            session.permanent = False
    else:
        session.permanent = True


if __name__ == '__main__':
    app.run()
