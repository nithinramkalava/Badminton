Project: Online Sport Venue Slot Booking

Details about the project: <br>
The project is a well developed website for online slot booking system for sport venues which registers users, logs them in, creates data for the website, handles bookings and shows the user their booked slots. 
It is a proper CRUD - CREATE READ UPDATE DELETE application which was enabled by using Flask_admin and SQLite3 relational database model.
 
Methodology: <br>
Used a website to create an online slot booking system for sport venues. Used Flask because of its useful properties: template inheritance, loops, and if statements in HTML files. Used an in-built flask-admin interface for database management because of its ease of implementation. We segregated admins and users using the is_admin attribute to prevent the creation of new tables and also established a many-to-one relationship between the sports model and the venues model to make implementation on the /admin/ route easier. Along with it, we created a specific model, BookingLog, to keep track of all the data from every booking made by every possible user of the website. This was the motive behind the structure of our database design. 

Tools, technologies, and frameworks used: <br>
Flask is a micro-web framework based on Python, which is known for its freedom.
HTML, CSS and JavaScript: Famous Languages used to create websites
SQLITE3 database: relational database used to keep track of data involved in the website

Data Collection and Storage method: <br>
HTML forms that send data through POST, which can be later used to store it in a database, which in turn is used to create a dynamic website was used as data collection method.
We have used a relational database (SQLite3) employed using FlaskSQLAlchemy as our storage method.

How to run? <br>
Create a venv:
```
py -3 -m venv .venv
```
If not working then you need to go to powershell using administrator privileges and set execution policy to RemoteSigned:
```
Set-ExecutionPolicy RemoteSigned
```

Activate it:
```
.venv\Scripts\activate    
```

To deactivate in future:
```
deactivate
```

Now install all the dependencies and packages in venv in /justnow folder using: 
```
pip install -r requirements.txt   
```

Now get into Badminton Folder using:
```
cd Badminton Website
```

And can run the Flask application using:
```
flask --app app.py run
```

To run in debug mode:
```
flask --app app.py run --debug    
```

