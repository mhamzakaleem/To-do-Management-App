from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/todo_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(15), default="pending")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)



@app.route("/")
def home():
    if "user_id" in session:
        user_id = session["user_id"]
        query = request.args.get("search", "").lower()
        tasks = Task.query.filter_by(user_id=user_id).all()
        if query:
            tasks = [
                task
                for task in tasks
                if query in task.title.lower()
                or query in task.description.lower()
                or query in task.status.lower()
            ]
        return render_template(
            "index.html", tasks=tasks, username=session.get("username", "")
        )
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "Username already exists. Please choose another one."

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("home"))
        return "Invalid credentials. Please try again."
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" in session:
        title = request.form["title"]
        description = request.form["description"]
        status = request.form["status"]
        user_id = session["user_id"]

        if len(title) > 15:
            return "Title length must be 15 characters or fewer."

        new_task = Task(
            title=title, description=description, status=status, user_id=user_id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    if "user_id" in session:
        task = Task.query.get(task_id)
        if task and task.user_id == session["user_id"]:
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/update_task/<int:task_id>", methods=["POST"])
def update_task(task_id):
    if "user_id" in session:
        task = Task.query.get(task_id)
        if task and task.user_id == session["user_id"]:
            title = request.form["title"]
            description = request.form["description"]
            status = request.form["status"]

            if len(title) > 15:
                return "Title length must be 15 characters or fewer."

            task.title = title
            task.description = description
            task.status = status
            db.session.commit()
        return redirect(url_for("home"))
    return redirect(url_for("login"))


# if __name__ == '__main__':
#     db.create_all()
#     app.run(debug=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This should now run within the application context
    app.run(debug=True)
