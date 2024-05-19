from sqlalchemy.sql import func
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from sqlalchemy import text
from flask_login import UserMixin

@login.user_loader
def load_student(id):
  return User.query.get(int(id))

class Tag(db.Model):
    __tablename__ = 'tags'
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag = db.Column(db.String(40), unique=True)
    category = db.Column(db.String(40))

    question_tags = db.relationship('Question_Tag', back_populates='tag', lazy=True)

    def __repr__(self):
        return '[<Tag_id {}> <Tag {}>]'.format(self.tag_id, self.tag)
    
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(12))
    about_me = db.Column(db.String(200), nullable=True)

    user_questions = db.relationship('Question', back_populates='user', lazy=True) 
    user_answers = db.relationship('Answer', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '[<User {}> <id {}> <Email {}> <Password {}>]'.format(self.username, self.id, self.email, self.password_hash)
    
    def to_dict_pfp(self):
        numQ = Question.query.filter_by(user_id=self.id).count()
        numA = Answer.query.filter_by(user_id=self.id).count()
        return {'id':str(self.id),'username':self.username, 'email':self.email, 'aboutme':self.about_me, 'numQ':numQ, 'numA':numA, 'pfp':self.profile_pic}
    
class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now())
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)

    user = db.relationship('User', back_populates='user_questions')
    tags = db.relationship('Question_Tag', back_populates='question', lazy=True)
    answers = db.relationship('Answer', back_populates='question', lazy=True)

    def __repr__(self):
        return f'''[
        User:{self.user_id} 
        Question:{self.question_id}, 
        Title:{self.title}, 
        Description:{self.description[:20]},
        Created:{self.date_created},
        Likes:{self.likes},
        Comments:{self.comments}
        ]'''
    def to_dict(self):
        return {
            'question_id': self.question_id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'username': self.user.username,
            'profile_photo': 'path_to_profile_photo',  # Modify this to use the actual profile photo path
            'votes': self.likes,
            'answers': [answer.to_dict() for answer in self.answers]
        }
    
    def associated_tags(self):
        return [itag.tag.tag for itag in self.tags]

    def to_dict(self):
        tagz = [itag.tag.tag for itag in self.tags]
        return {'question_id':self.question_id,'title':self.title,'description':self.description,'likes':self.likes,'comments':self.comments,'tags':tagz,'user':self.user.username,'profile_pic':self.user.profile_pic,'date':self.date_created.strftime('%Y-%m-%d')}
    
    def get_user(self):
        return self.user.username
    
class Question_Tag(db.Model):
    __tablename__ = 'question_tags'
    qt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id'))

    tag = db.relationship('Tag', back_populates='question_tags')
    question = db.relationship('Question', back_populates='tags')

    def __repr__(self):
        return '[<QT_id {}> <Tag_id {}> <Question_id {}>]'.format(self.qt_id ,self.tag_id, self.question_id)
    

class Answer(db.Model):
    __tablename__ = 'answers'
    ans_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer = db.Column(db.String(2000), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now())
    likes = db.Column(db.Integer)

    user = db.relationship('User', back_populates='user_answers')
    question = db.relationship('Question', back_populates='answers')

    def __repr__(self):
        return f'''
        [Answer:{self.ans_id}
        Question:{self.question_id},
        User:{self.user_id},
        Answer:{self.answer[:20]},
        Created:{self.date_created},
        Likes:{self.likes}
        ]'''
    def to_dict(self):
        return {
            'ans_id': self.ans_id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'username': self.user.username,
            'profile_photo': 'path_to_profile_photo',  # Modify this to use the actual profile photo path
            'answer': self.answer,
            'created': self.date_created,
            'likes': self.likes
        }