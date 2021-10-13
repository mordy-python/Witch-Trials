import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_ADDR')
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html', title='Home')
@app.route('/tweets')
def tweets():
    tweet_file = open('tweets.json')
    tweets = json.loads(tweet_file.read())
    tweet_file.close()
    twee = []
    for tweet in tweets:
        twee.append(tweets[tweet])
    return render_template('tweets.html', title='Tweets', tweets=twee)
# TODO: Complete this route and method
@app.route('/send-confirm', methods=['POST'])
def send_confirm():
    recipient = request.form['recipient']
    msg = Message('Twilio SendGrid Test Email', recipients=[recipient])
    msg.body = ('Congratulations! You have sent a test email with '
                'Twilio SendGrid!')
    msg.html = ('<h1>Twilio SendGrid Test Email</h1>'
                '<p>Congratulations! You have sent a test email with '
                '<b>Twilio SendGrid</b>!</p>')
    mail.send(msg)
    flash(f'A test message was sent to {recipient}.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)