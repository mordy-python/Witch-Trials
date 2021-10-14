import os
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash
from flask_mail import Mail, Message
import jinja2
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MAIL_SERVER"] = "smtp.sendgrid.net"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "apikey"
app.config["MAIL_PASSWORD"] = os.environ.get("SENDGRID_API_KEY")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("EMAIL_ADDR")
mail = Mail(app)

chars = [{'img':'danforth.jpg', 'name':'Judge Danforth', 'bio':'lorem ipsum yada yada'}]

@app.route("/")
def index():
    return render_template("index.html", title="Home")

@app.route("/characters")
def characters():
    return render_template("character.html", title="People Involved", characters=chars)

@app.route("/tweets")
def tweets():
    tweet_file = open("tweets.json")
    tweets = json.loads(tweet_file.read())
    tweet_file.close()
    twee = []
    for tweet in tweets:
        twee.append(tweets[tweet])
    return render_template("tweets.html", title=os.environ['SECRET_KEY'], tweets=twee)


@app.route("/witch-report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        your_name = request.form["name"]
        email = request.form["email"]
        witch = request.form["witch"]
        evidence = request.form["evidence"]
        msg = Message(f"Suspect confirmation for {witch.capitalize()}", recipients=[email])
        msg.body = (
            f"You reported {witch.capitalize()} for witchcraft."
            "This is a serious accusation. Please make sure you posses concrete evidence."
            "If you have doubts about your claim, you have two hours to revoke this accusation."
        )
        with open("email.html") as email_msg:
            html = email_msg.read()
            email_content = jinja2.Template(html)
            fina_html = email_content.render(witch=witch, name=your_name, evidence=evidence)
        msg.html = fina_html
        mail.send(msg)
        flash(f"{witch} was reported.\nLook for a confirmation email.")
        return redirect(url_for("index"))
    return render_template("report.html", title="Report A Witch")


if __name__ == "__main__":
    app.run(debug=True)
