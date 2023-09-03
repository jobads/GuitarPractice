from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
#from flask_plots import Plots
from sqlalchemy import desc, func
from datetime import datetime
from matplotlib.figure import Figure
import matplotlib.dates as mdates

app = Flask(__name__)
#plots = Plots(app)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.app_context().push()


class tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    target_bpm = db.Column(db.Integer)
    complete = db.Column(db.Boolean)

class sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    bpm = db.Column(db.Integer)
    duration = db.Column(db.Time)


db.create_all()


@app.get("/")
def home():

    max_bpms = db.session.query(sessions.task_id, func.max(sessions.bpm).label("bpm")).group_by(sessions.task_id).subquery()
    last_session = db.session.query(sessions.task_id, func.max(sessions.date).label("last_session_date")).group_by(sessions.task_id).subquery()
    task_list = db.session.query(tasks.id, tasks.title, tasks.target_bpm, tasks.complete) \
            .outerjoin(max_bpms, tasks.id == max_bpms.c.task_id) \
            .outerjoin(last_session, tasks.id == last_session.c.task_id) \
            .add_entity(max_bpms.c.bpm) \
            .add_entity(last_session.c.last_session_date) \
            .order_by(last_session.c.last_session_date) \
            .all()
    return render_template("base.html", task_list=task_list)

# @app.route("/add", methods=["POST"])
@app.post("/add")
def add():
    title = request.form.get("title")
    target_bpm = request.form.get("target_bpm")
    new_task = tasks(title=title, target_bpm = target_bpm, complete=False)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

@app.post("/addsession")
def addsession():
    date = request.form.get("date")
    bpm = request.form.get("bpm")
    task_id = request.form.get("task_id")
    new_session = sessions(task_id=int(task_id), bpm=int(bpm), date=datetime.strptime(date, "%Y-%m-%d"))
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for("task", task_id=task_id))

@app.post("/delete")
def delete():
    task_id = request.form.get("task_id")
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.delete(task)
    db.session.commit()
    session = db.session.query(sessions).filter(sessions.task_id == task_id).all()
    for item in session:
        db.session.delete(item)
    db.session.commit()   

    return redirect(url_for("home"))

@app.post("/deletesession")
def deletesession():
    task_id = request.form.get("task_id")
    session_id = request.form.get("session_id")
    # todo = Todo.query.filter_by(id=todo_id).first()
    session = db.session.query(sessions).filter(sessions.id == session_id).first()
    db.session.delete(session)
    db.session.commit()
    session_list = db.session.query(sessions).filter(sessions.task_id == task_id).all()
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.commit()
    last_session = db.session.query(sessions).filter(sessions.task_id == task_id).order_by(desc(sessions.bpm)).first()

    today = datetime.today().strftime("%Y-%m-%d")
    #return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session)
    return redirect(url_for("task", task_id = task_id))


@app.get("/task/<int:task_id>")
def task(task_id):
    # todo = Todo.query.filter_by(id=todo_id).first()
    session_list = db.session.query(sessions).filter(sessions.task_id == task_id).order_by(desc(sessions.date)).all()
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.commit()
    last_session = db.session.query(sessions).filter(sessions.task_id == task_id).order_by(desc(sessions.date)).first()

    today = datetime.today().strftime("%Y-%m-%d")

    try:
        lst_bpm = [r.bpm for r in session_list]
        lst_date = [r.date for r in session_list]

        fig = Figure(figsize=(6,3), dpi = 200)
        fig
        axis = fig.add_subplot(1, 1, 1)
        xs = lst_date
        ys = lst_bpm
        axis.plot(xs, ys)
        locator = mdates.AutoDateLocator()
        formatter = mdates.AutoDateFormatter(locator)

        axis.xaxis.set_major_locator(locator)
        axis.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate(rotation=45)

        #axis.set_xticklabels(axis.get_xticks(), rotation = 45)
        axis.hlines(y = task.target_bpm, xmin = min(lst_date), xmax=max(lst_date), color = "green")
        axis.set_ylim(bottom=0, top= task.target_bpm * 1.2)
        fig.tight_layout()
        print("file wll be saved now")
        #fig.savefig("/home/moritzinho/mysite/static/session_plot.png", transparent=True)
        fig.savefig("static/session_plot.png", transparent=True)
        print("file saved")


        return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session, url = "session_plot.png")
        #return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session, url = "/static/session_plot.png")
    except Exception as e: 
        print(e)
        return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session, url = "empty.png")
        return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session, url = "/static/empty.png")
