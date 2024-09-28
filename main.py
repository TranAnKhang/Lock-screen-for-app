from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"


app.config["SQLALCHEMY_DATABASE_URI" ]= 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#model
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    password_hash = db.Column(db.String(30), nullable = False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content =  db.Column(db.String(100), nullable = False)
    status =  db.Column(db.Integer, default = 0 )
    creation =  db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f"Task {self.id}"


@app.route("/")
def home():

    if "username" in session:
        tasks = Task.query.order_by(Task.date_creation).all()
        return render_template('dashboard.html', username = session["username"], tasks = tasks)
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username = username).first()
    if user and user.check_password(password):
        session["username"] = username
        return redirect(url_for("dashboard"))
    else:
        flash("Your ass aint in here")
        return render_template('index.html', error = "YOU AINT ON THIS WORLD")
    

@app.route("/register", methods = ["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username = username).first()

    if user:
        flash("There ain't enough space for 2 of your fatass")
        return render_template("index.html", error = "username already exists")
    else:
        new_user = User(username = username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("dashboard"))

@app.route("/", methods = ["POST", "GET"])
def add():
    if request.method == "POST":
        task_content = request.form["content"]
        new_task = Task(content = task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error: {e}")
            return redirect('/')
        
   


@app.route("/delete/<int:id>")

def delete(id):
    task_delete = Task.query.get_or_404(id)
    try:
        db.session.delete(task_delete)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        print(f"Error:{e}")



@app.route("/update/<int:id>", methods = ["GET", "POST"])

def update(id):
    task_update = Task.query.get_or_404(id)
    if request.method == "POST":
        task_update.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error: {e}")
    else:
        return render_template("update.html", task=task_update)




@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        tasks = Task.query.order_by(Task.date_creation).all()
        return render_template('dashboard.html', username = session["username"], tasks = tasks)
    return redirect(url_for('home'))



app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True)