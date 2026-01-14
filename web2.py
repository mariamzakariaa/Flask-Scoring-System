from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
#render_template grabs an html file and render it as our webpage -instead of writing html inline-
#that html file should be:
#1. in a folder named templates
#2. templates folder should be in the same folder as the flask python file

app = Flask(__name__)
app.secret_key = "mariam" #to save cookies
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3' #to save the data, users is the name of the table (this is for database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #to avoid a warning
app.permanent_session_lifetime = timedelta(minutes=1) #to make the session last for 1 day

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
#primary_key is a unique identifier for each row in the table so it is unique for each row 
#id is a column with an integer data type and it is the primary key
#name is a column with a string data type
#email is a column with a string data type

    def __init__(self, name, email): #this takes in variables as arguments and assigns them to the class attributes, variables that should be passed in users object to have an id
        self.name = name
        self.email = email


@app.route('/', defaults={'name': ""})
@app.route('/<name>')
def home(name=None):
    return render_template('index.html', name=name) #dont forget to type the variable name

@app.route('/test/')
def test():
    return render_template('test.html')

@app.route("/view")
def view(): #this page displays all values in db
    return render_template("view.html", values=users.query.all())

#http method used by default is  GET
#to get info from a form (get info in a login page then display this info in another redirected page):

@app.route('/login', methods=['POST', 'GET'])
def login():
    #first make sure it is a post request then take its value to start a session
    if request.method == 'POST':
        session.permanent = True
        user = request.form['nm'] #inside request.form: we enter the key of the info we want to get from the form (the key defined in the html form)
        session['user'] = user #this stored the value of user(from request.form) in a key named user
        
        found_user = users.query.filter_by(name=user).first()#.first() gives the first result 
        if found_user:
            session['email'] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()
        
        
        flash("logged in successfully")
        return redirect(url_for('user')) #user is what is given from the request.form
    else: #if no post request(so it is a get one bec they are only trying to access the login page):
        if "user" in session: #if already logged in:
            flash("already logged in")
            return redirect(url_for("user"))
        return render_template('login.html') #if no post request and no session

@app.route('/user', methods=["POST", "GET"])
def user(): #user is called an endpoint
    #this page should not be accessed without logging in, so before openening it we should make sure that THERE IS A SESSION 
    email = None
    if "user" in session: #check if logged in(if there is a session)
        user = session['user']
        
        if request.method == "POST": #if a form was submitted
            email = request.form["email"]#take the email from the form and store it in a variable
            session["email"] = email#save the email in the session dictionary
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("email saved successfully", "info") 
        else: #for GET requests (just visiting the page)
            if "email" in session: #if an email was already saved
                email = session["email"]#load it back from the session
        return render_template('user.html', email=email)
    else:
        flash("you are not logged in")
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    flash(f"logged out successfully ", "info")
    session.pop('user', None) #pop removes the last value in a dictionary (it removed used from the session dictionary so now it is logged out)
    session.pop("email", None)
    return redirect(url_for("login"))

"""
def home(name):
    return render_template('index.html', salut=name) #to make it use the html file
#the salut=name is passing a value of a variable here to a variable in html file

"""
if __name__ =="__main__":
    with app.app_context(): #VERY IMPORTANT!!!
        db.create_all() #creates all the tables in the database if fthey dont already exist when the program is run, should be above the app.run
    app.run(debug=True) #debug=True updates the webpage without having to restart the server every time you make a change