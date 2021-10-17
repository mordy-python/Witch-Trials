import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import jinja2
import json
from deta import Deta
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MAIL_SERVER"] = "smtp.sendgrid.net"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "apikey"
app.config["MAIL_PASSWORD"] = os.environ.get("SENDGRID_API_KEY")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("EMAIL_ADDR")
mail = Mail(app)
key = os.environ.get("DETA_PROJECT_KEY")
deta = Deta(key)
suspects = deta.Base("suspected_witches")
chars = [
    {
        "img": "danforth.jpg",
        "name": "Judge Danforth",
        "bio": "Judge Danforth was deputy governor of Salem and the lead judge in the Salem Witch Trials. He sent 19 people to the gallows in the time he presided over the Trials.",
    },
    {
        "img": "abigail.jpg",
        "name": "Abigail Williams",
        "bio": "Abigail Williams was one of the driving forces in the Witch Trials. She accused women in Salem who she didn't like or did something to displease her. When she walked through Salem people would avoid her and attempt to stay on her good side. She ran away with her friend, Mercy Lewis and the Witch Trials died down once she left Salem.",
    },
    {
        "img": "tituba.jpg",
        "name": "Tituba",
        "bio": "Tituba was a witch in Salem. She was accused of witchcraft when she confessed she was a witch, she was given the chance to redeem herself if she told Rev. Hale who else she saw with the Devil. She said she saw Goody Good and Goody Osborne with the Devil.",
    },
    {
        "img": "putnam.png",
        "name": "Thomas Putnam",
        "bio": "Thomas Putnam was a very influential figure in Salem. He accused many members of the rival Porter Family. He was responsible for the accusations against 43 people. He also accused some of his neighbors so that he could take their land. His daughter Ruth accused 62 people.",
    },
    {
        "img": "mercy.png",
        "name": "Mercy Lewis",
        "bio": "Mercy Lewis was Abigail's friend and another principal accuser in the Witch Trials. She accused George Burroughs of beating her because she refused to sign his Book of The Devil.",
    },
    {
        "img": "parris.jpg",
        "name": "Reverend Parris",
        "bio": 'Reverend Samuel Parris was the minister in Salem. He had a strained relationship with the townspeople, he wanted more pay and more money for the church. He was a strong proponent of the Witch Trials and his niece was the main accuser in the Witch Trials. At one point he gave a sermon titled "Christ Knows How Many Devils There Are."',
    },
    {
        "img": "hale.jpeg",
        "name": "Reverend Hale",
        "bio": "Reverend John Hale was a minister in nearby Beverly. He was invited to Salem by Rev. Parris to help with finding witches. When he realized how the town was losing its head he left the court and denounced the Witch Trials.",
    },
    {
        "img": "proctor.jpg",
        "name": "John Proctor",
        "bio": "John Proctor was married to Elizabeth Proctor. He was arrested and accused of witchcraft when he tried to defend his wife in court. He was given the chance to save himself from hanging if he wrote a confession and signed it. He refused to sign it and ruin his name; he was hung alongside Martha Corey and Rebecca Nurse.",
    },
    {
        "img": "corey.jpg",
        "name": "Giles Corey",
        "bio": "He was an farmer in Salem. He and his wife Martha were accused of witchcraft. He was asked to plead either Guilty or Not Guilty but he refused to plea either way. He was pressed with heavy stones and still refused to answer. He died after three days of pressing. His wife Martha refused to confess and was hanged alongside John Proctor and Rebecca Nurse.",
    },
]


@app.route("/")
def index():
    return render_template("index.html", title="Home")


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for('admin'))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "RevParris" and password == "w1tchtr14l5":
            session["username"] = "RevParris"
            return redirect(url_for("admin"))
    return render_template("login.html")


@app.route("/characters")
def characters():
    return render_template("characters.html", title="People Involved", characters=chars)


@app.route("/characters/<name>")
def character_stuff(name):
    for c in chars:
        for person in c:
            if c["name"] == name:
                ch = c
                break
            continue
    return render_template("character.html", title=name.capitalize(), character=ch)


@app.route("/tweets")
def tweets():
    tweet_file = open("tweets.json")
    tweets = json.loads(tweet_file.read())
    tweet_file.close()
    twee = []
    for tweet in tweets:
        twee.append(tweets[tweet])
    return render_template("tweets.html", title="Tweets", tweets=twee)


@app.route("/witch-report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        your_name = request.form["name"]
        email = request.form["email"]
        witch = request.form["witch"]
        evidence = request.form["evidence"]
        suspects.insert(
            {
                "name": your_name,
                "email": email,
                "witch": witch,
                "evidence": evidence,
            }
        )
        msg = Message(
            f"Suspect confirmation for {witch.capitalize()}", recipients=[email]
        )
        msg.body = (
            f"You reported {witch.capitalize()} for witchcraft."
            "This is a serious accusation. Please make sure you posses concrete evidence."
            "If you have doubts about your claim, you have two hours to revoke this accusation."
        )
        with open("email.html") as email_msg:
            html = email_msg.read()
            email_content = jinja2.Template(html)
            fina_html = email_content.render(
                witch=witch, name=your_name, evidence=evidence
            )
        msg.html = fina_html
        mail.send(msg)
        flash(f"{witch} was reported.\nLook for a confirmation email.")
        return redirect(url_for("index"))
    return render_template("report.html", title="Report A Witch")

@app.route("/admin")
def admin():
    if "username" in session:
        witches = suspects.fetch()
        return render_template("admin.html", suspects=witches.items)
    return redirect(url_for("login"))
@app.route('/delete-witch')
def delete_witch():
    if "username" in session:
        key = request.args.get('key')
        suspects.delete(key)
        flash('Deleted Witch')
        return redirect(url_for('admin'))
if __name__ == "__main__":
    app.run(debug=True)
