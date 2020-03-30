from datetime import datetime

from flask import url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin
from werkzeug.utils import redirect


def like_hit():
    print("hello world")
    return 0


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    follows = db.Column(db.String(20), unique=True, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    #likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


@app.route('/like/<int:post_id>/<action>')

def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        post.likes = post.likes +1
        db.session.commit()
    if action == 'unlike':
        #current_user.unlike_post(post)
        db.session.commit()
    #return render_template('home.html', posts=posts)
     #renturn render_template('liked.html', title='Liked')
    return redirect(url_for('home'))
    #return f"This is not where it needs to go. Also you must go back then refresh page to see new amount of likes"
    #return redirect(request.referrer)


@app.route('/follow/<int:logged_user>/<int:user_id>/<action>')

def follow_action(logged_user, user_id, action):
    user = User.query.filter_by(id=user_id).first_or_404()
    current = User.query.filter_by(id=logged_user).first_or_404()
    if current.id == user.id:
        return redirect(url_for('home'))
    if action == 'follow':
        current.follows = user.username
        db.session.commit()
    return redirect(url_for('home'))