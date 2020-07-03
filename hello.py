from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask import render_template
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask import url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail
from flask_mail import Message
from threading import Thread
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sadzczxcsfewsscassfasd'
app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_SERVER'] = 'smtp.126.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'OrchidRock <orchidrock@126.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


manager = Manager(app)
bootstrap = Bootstrap(app)
monment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


def make_shell_context():
    """TODO: Docstring for make_shell_context.
    :returns: TODO

    """
    return dict(app=app, db=db, User=User, Role=Role)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """TODO: Docstring for send_email.
    :returns: TODO

    """
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, 
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])    
    msg.body = render_template(template + '.txt', **kwargs)    
    msg.html = render_template(template + '.html', **kwargs)    
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.route('/', methods=['GET', 'POST'])
def index():
    
    # user_agent = request.headers.get('User-Agent')

    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    
    # name = None
    form = NameForm()
    if form.validate_on_submit():
        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flash('Looks like you have changed your name!')
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                # print(app.config['MAIL_USERNAME'])
                # print(app.config['MAIL_PASSWORD'])
                send_email(app.config['FLASKY_ADMIN'],
                          'New User',
                          'mail/new_user', user=user)

        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
        # name = form.name.data
        # form.name.data = ''
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known', False))

    # return render_template('index.html', current_time=datetime.utcnow())
    # return redirect('http://localhost:5000/user/rock')
    # return response
    # return '<h1>Bad Request</h1>', 400
    # return '<p>Your browser is %s</p>' % user_agent
    # return '<h1>Hello World!</h1>'


@app.route('/index')
def index_templete():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    # return render_template('user.html', name='<h2>{}</h2>'.format(name))
    return render_template('user.html', name=name)

@app.route('/user/<name>')
def hello(name):
    """TODO: Docstring for hello.
    :returns: TODO

    """
    # return '<h1>Hello, %s!</h1>' % name


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class Role(db.Model):    
    
    __tablename__ = 'roles'    
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(64), unique=True)
    
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
class User(db.Model):    
    
    __tablename__ = 'users'    
    id = db.Column(db.Integer, primary_key=True)    
    username = db.Column(db.String(64), unique=True, index=True)
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' % self.username


if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()
