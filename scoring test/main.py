from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import json, os


app = Flask(__name__)
app.secret_key = "mariam"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///competition.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#questions
with open(os.path.join(os.path.dirname(__file__), "data","questions.json"), "r") as f:
    questions = json.load(f)

    
r1mcq = questions["round1"]["mcq"]
r1_tf = questions["round1"]["true_false"]
r1_bank = questions["round1"]["bank"]

#models:
class participant(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    scores = db.relationship(
        "Score",
        backref="participant",
        cascade="all, delete-orphan"
    )
class Score(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participant.id")) #links this column to the id column of the Participant table.
    value = db.Column(db.Integer, nullable=False)
    
#routes:
@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        participant = participant.query.filter_by(name=name).first()
        if participant:
            flash("You are already registered")
        else:
            db.session.add(participant(name=name))
            db.session.commit()
            flash("You are now registered")
        return redirect(url_for("leaderboard"))
    return render_template("login.html")

@app.route("/reset_competition", methods=["POST"])
def reset_competition():
    # Reset each participant's score to 0
    for p in participant.query.all():
        p.score = 0
    db.session.commit()
    flash("Competition has been reset. All scores cleared.")
    return redirect(url_for("leaderboard"))


@app.route("/leaderboard")
def leaderboard():
    participants = participant.query.all()
    leaderboard = []
    for p in participants:
        scores = [s.value for s in Score.query.filter_by(participant_id=p.id)]
        total_score = sum(s.value for s in Score.query.filter_by(participant_id=p.id))
   # cumulative total
        leaderboard.append({
            "id": p.id,
            "name": p.name,
            "score": total_score
        })
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    return render_template("index.html", leaderboard=leaderboard)



@app.route("/", methods=["GET", "POST"])
@app.route("/add_participant", methods=["GET", "POST"])
def add_participant():
    if request.method == "POST":
        name =request.form["name"]
        existing_participant = participant.query.filter_by(name=name).first() #checks 
        if existing_participant: #if the name is already in the database
            flash("Participant already exists")
            return redirect(url_for("add_participant"))
        db.session.add(participant(name=name))
        db.session.commit()
        return redirect(url_for("leaderboard"))
    return render_template("add_participant.html")

@app.route("/delete/<int:participant_id>", methods=["POST"])#means the route expects a number (the id)
def delete_participant(participant_id):
    participant_object = participant.query.get_or_404(participant_id) #get the participant with the id  
    db.session.delete(participant_object)
    db.session.commit()
    flash(f"Deleted {participant_object.name}")
    return redirect(url_for("leaderboard"))

"""@app.route("/add_score", methods=["GET", "POST"])
def add_score():
    participants = participant.query.all()
    if request.method == "POST":
        participant_id = request.form["participant_id"] #who is being scored
        value = int(request.form["value"]) #int score value
        db.session.add(Score(participant_id=participant_id, value=value))
        db.session.commit()
        return redirect(url_for("leaderboard"))
    return render_template("add_score.html", participants=participants)"""

@app.route("/rounds", methods=["POST"])
def rounds():
    team_ids = request.form.getlist("teams")
    if len(team_ids) != 2:
        flash("Select exactly 2 teams.")
        return redirect(url_for("leaderboard"))

    teams = participant.query.filter(participant.id.in_(team_ids)).all()
    if len(teams) != 2:
        flash("Error fetching teams.")
        return redirect(url_for("leaderboard"))

    session["team_ids"] = team_ids
    return render_template("rounds.html", teams=teams)



@app.route("/r1questions", methods=["POST"])
def r1questions():
    team_ids = request.form.getlist("team_ids")
    round_num = request.form.get("round")

    if not team_ids or not round_num:
        flash("Missing info.")
        return redirect(url_for("leaderboard"))

    session["team_ids"] = team_ids
    session["round"] = round_num

    teams = participant.query.filter(participant.id.in_(team_ids)).all()

    if round_num == "1":
        return render_template("r1questions.html", teams=teams, round_num=1)
    else:
        return f"<h2>Round {round_num} questions not ready yet.</h2>"


@app.route("/choose_questions", methods=["POST"])
def choose_questions():
    team_ids = request.form.getlist("team_ids")
    round_num = request.form.get("round")
    q_type = request.form.get("question_type")

    if not team_ids or not round_num or not q_type:
        flash("Missing info. Please select question type again.")
        return redirect(url_for("leaderboard"))

    # Store info in session
    session["team_ids"] = team_ids
    session["round"] = round_num
    session["q_type"] = q_type
    session["current_q_index"] = 0
    session["current_team_index"] = 0

    return redirect(url_for("questions"))



@app.route("/questions", methods=["GET", "POST"])
def questions():
    # Retrieve session info
    team_ids = session.get("team_ids")
    round_num = session.get("round")
    q_type = session.get("q_type")
    current_q_index = session.get("current_q_index", 0)
    current_team_index = session.get("current_team_index", 0)

    if not team_ids or not q_type or not round_num:
        flash("Session expired or invalid. Go back to leaderboard.")
        return redirect(url_for("leaderboard"))

    teams = participant.query.filter(participant.id.in_(team_ids)).all()
    current_team = teams[current_team_index]

    # Load questions
    with open(os.path.join(os.path.dirname(__file__), "data", "questions.json")) as f:
        all_questions = json.load(f)

    team_key = f"team{current_team_index + 1}"
    question_list = all_questions[f"round{round_num}"][q_type][team_key]

    if current_q_index >= len(question_list):
        flash(f"All {q_type} questions done for Round {round_num}")
        return redirect(url_for("leaderboard"))

    current_question = question_list[current_q_index]

    if request.method == "POST":
        user_answer = request.form.getlist("answer")

        if q_type == "mcq":
            correct_answer = [str(a).strip() for a in current_question["answer"]]
            user_answer = [str(a).strip() for a in request.form.getlist("answer")]
            score_value = 5 if set(user_answer) == set(correct_answer) else 0

        elif q_type == "true_false":
            correct_answer = str(current_question["answer"]).strip().lower()
            user_answer = [a.strip().lower() for a in request.form.getlist("answer")]
            score_value = 5 if user_answer and user_answer[0] == correct_answer else 0

            score_value = 0

        # Save score
        new_score = Score(participant_id=current_team.id, value=score_value)
        db.session.add(new_score)
        db.session.commit()

        # Switch team turn
        session["current_team_index"] = (current_team_index + 1) % 2

        # Increment question index after both teams answered
        if session["current_team_index"] == 0:
            session["current_q_index"] = current_q_index + 1

        return redirect(url_for("questions"))

    return render_template(
        "question_display.html",
        question=current_question,
        current_team=current_team,
        q_index=current_q_index + 1,
        total=len(question_list),
        round_num=round_num,
        q_type=q_type,
        teams=teams
    )



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
        