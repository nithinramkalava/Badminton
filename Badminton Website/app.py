from models import db, User, Venue, BookingLog, Member, Sport
from views import AdminIndexView2, UserView, VenueView, LogView, MemberView, SportView

from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, get_flashed_messages,jsonify,flash
from flask_admin import Admin
from flask_admin.base import MenuLink
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
import os
from sqlalchemy import desc


app = Flask(__name__)
# instance

secret_key = os.urandom(48)
app.config["SECRET_KEY"] = secret_key
# protecting the app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finaleee.db' # name of database
db.init_app(app)
# connecting app and database


# with app.app_context():
#     if os.path.exists('/instance/finaleee.db'):
#         db.drop_all()
#         db.create_all()
#         db.session.commit()
#     else:
#         db.create_all()
#         db.session.commit()

app.config["FLASK_ADMIN_SWATCH"] = "cyborg"  # bootswatch theme

# Views and Links in Flask_admin
admin = Admin(app, name="Admin", template_mode="bootstrap4", index_view=AdminIndexView2(name='Home'))
admin.add_view(UserView(User, db.session))
admin.add_view(VenueView(Venue, db.session))
admin.add_view(SportView(Sport,db.session))
admin.add_view(LogView(BookingLog, db.session))
admin.add_view(MemberView(Member,db.session))
admin.add_link(MenuLink(name='Logout', url='/admin-logout'))

#For Login Management
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class UserLogin(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Admin Register may use later on
# @app.route('/admin-register', methods=['GET', 'POST'])
# def adminregister():
#     if request.method == 'POST':
#         name = request.form['name']
#         username = request.form['username']
#         # Check if - username already exists
#         existing_user = User.query.filter_by(Username=username).first()
#         if existing_user:
#             flash('Username already exists. Please choose a different username.', 'error')
#         else: 
#             password = request.form['password']
#             hashedpassword = generate_password_hash(password)
#             new_user = User(Name=name, Username=username, HashedPassword=hashedpassword, is_admin=True)
#             db.session.add(new_user)
#             db.session.commit()
#             flash('Admin registered successfully. You can now log in.', 'success')
#             return redirect(url_for("userlogin"))
#     return render_template('AdminRegister.html')


#User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("User has successfully logged out","error")
    return redirect(url_for("userlogin"))

#Admin Logout
@app.route('/admin-logout')
@login_required
def adminlogout():
    logout_user()
    flash("Admin has successfully logged out","error")
    return redirect(url_for("userlogin"))

#For Login
@app.route("/", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        user = User.query.filter_by(Username=request.form['username']).first()
        if not user:
            flash("Username does not exist","error")
        elif user and check_password_hash(user.HashedPassword, request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for("home"))
        else:
            flash('Password is incorrect', 'error')
    return render_template("Index.html",messages=get_flashed_messages())


#For Registration
@app.route('/user-register', methods=['GET', 'POST'])
def userregister():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        # Check if the username already exists
        existing_user = User.query.filter_by(Username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
        else: 
            password = request.form['password']
            if password != request.form["confirmpassword"]:
                flash('Passwords do not match',"error")
            else:
                hashedpassword = generate_password_hash(password)
                new_user = User(Name=name, Username=username, HashedPassword=hashedpassword, is_admin=False)
                db.session.add(new_user)
                db.session.commit()
                flash('User registered successfully. You can now log in.', 'success')
                return redirect(url_for("userlogin"))
                
    return render_template('Register.html',messages=get_flashed_messages())


# For Venues page
@app.route("/venues")
def venue():
    venues = Venue.query.all()
    return render_template('Venues.html', venues=venues)


# For Home page
@app.route("/home")
def home():
    members = Member.query.all()
    return render_template("Home.html", members=members)

#Booking-Page
@app.route("/venues/<venuename>", methods=['GET', 'POST'])
def booking_page(venuename):
    venue = Venue.query.filter_by(VenueName=venuename).first()
    if request.method == "POST": 
        if current_user.is_authenticated:
            return redirect(url_for("book_venue",venuename=venuename))
        else:
            flash("You have not Logged In","error")
            return redirect(url_for("userlogin"))
    return render_template("Booking_page.html", venue=venue ,messages=get_flashed_messages(), avail_sports=venue.Sports)

# to generate time slots based on venue first and last slot
def generate_time_slots(venue):
    start_hour = venue.FirstSlot.hour
    end_hour = venue.LastSlot.hour
    time_slots = []

    current_hour = start_hour
    while current_hour <= end_hour:
        time_slots.append(f'{current_hour}:00')
        current_hour += 1
    return time_slots

# Logic to fetch available slots for a given venue
def generate_available_slots(venue,sport,date):
    existing_bookings = BookingLog.query.filter_by(VenueID=venue.VenueID,SportID=sport.SportID,Date=date).all()
    all_slots = generate_time_slots(venue)
    avail_slots = list(all_slots)

    i = 0
    while i < len(all_slots):
        slot = all_slots[i]
        next_slot = all_slots[i + 1] if i + 1 < len(all_slots) else None

        for booking in existing_bookings:
            if booking.Slot == slot:
                if booking.Duration == '1hr':
                    avail_slots.remove(slot)
                    break
                elif booking.Duration == '2hr':
                    avail_slots.remove(slot)
                    if i != len(all_slots)-1:
                        avail_slots.remove(next_slot)
                    break
        i += 1

    return avail_slots


# Booking Form
@app.route('/venues/<venuename>/book', methods=["GET","POST"])
def book_venue(venuename):
    venue = Venue.query.filter_by(VenueName=venuename).first()
    
    # Handle form submission (POST request)
    if request.method == 'POST' and current_user.is_authenticated:
        sport = request.form['sports']
        date = request.form['date']
        time_slot = request.form['time-slot']
        duration = request.form['duration']

        ssport = Sport.query.filter_by(SportName=sport).first()

        venueid = venue.VenueID
        sportid = ssport.SportID

        new_booking = BookingLog(
            UserID= int(current_user.get_id()),
            VenueID=venueid,
            SportID=sportid,
            Slot= time_slot,
            Duration=duration,
            Date= str(date)
        )

        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for("record"))

    elif request.method == "GET":
        return render_template("Booking_form.html",venuename=venuename,avail_sports=venue.Sports)
    
    else:
        flash("Login is pending", "error")
        return redirect(url_for("userlogin"))

# Route To Handle availability using json and javascript ajax
@app.route('/venues/<venuename>/availability', methods=['GET'])
def get_available_slots(venuename):
    date = request.args.get('date')
    sport = request.args.get('sport')

    # Fetch available slots based on the provided parameters
    venue = Venue.query.filter_by(VenueName=venuename).first()
    ssport = Sport.query.filter_by(SportName=sport).first()

    if venue and ssport and date:
        available_slots = generate_available_slots(venue, ssport, date)
        return jsonify({'availableSlots': available_slots})

    return jsonify({'error': 'Invalid parameters'}), 400

# For Record to show all the booked records from BookingLog for a given user
@app.route("/records")
def record():
    logs = BookingLog.query.filter_by(UserID=current_user.get_id()).order_by(desc(BookingLog.BookingTime)).all()

    venues = []
    sports = []
    dates = []
    starts = []
    durations = []
    BookingTimes= []

    for log in logs:
        venue = Venue.query.get(log.VenueID)
        sport = Sport.query.get(log.SportID)
        
        venues.append(venue)
        sports.append(sport)
        dates.append(log.Date)
        starts.append(log.Slot)
        durations.append(log.Duration)
        BookingTimes.append(log.BookingTime)

    return render_template("Records.html", logs=logs, venues=venues, sports=sports, dates=dates, starts=starts, durations=durations, BookingTimes=BookingTimes)

