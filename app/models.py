from datetime import datetime
from flask import current_app 
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_ 

from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    notes = db.relationship('Note', backref="user", lazy='dynamic')
    ideas = db.relationship('Idea', backref="user", lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False 
        self.confirmed = True 
        db.session.add(self)
        return True 
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')
    
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False 
        user = User.query.get(data.get('reset'))
        if user is None:
            return False 
        user.password = new_password
        db.session.add(user)
        return True 



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


note_label = db.Table("note_label", 
                    db.Column("note_id", db.Integer, db.ForeignKey("notes.id")),
                    db.Column("label_id", db.Integer, db.ForeignKey("labels.id")))


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    intensive_reading = db.Column(db.Boolean, default=False)
    time_create = db.Column(db.DateTime, default=datetime.utcnow)
    time_modify = db.Column(db.DateTime, default=datetime.utcnow)
    # paper_pdf = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    paper_id = db.Column(db.Integer, db.ForeignKey("papers.id"))
    labels = db.relationship('Label', secondary=note_label, 
                             backref=db.backref('note', lazy='dynamic'), lazy='dynamic')
    
    
    def insert(self):
        self.time_create = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        
    def modified(self, **kwargs):
        self.intensive_reading = kwargs["intensive"]
        self.content = kwargs["content"]
        self.time_modify = datetime.utcnow()
        self.user = kwargs['user']
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def find_by_keyword(intensive, keyword, user):
        notes = Note.query.filter_by(intensive_reading=intensive, user=user).filter(
            or_(Note.content.like(("%" + keyword + "%") if id is not None else "")
                )
        ).order_by(Note.time_modify.desc()).all()
        
        return notes 


class Label(db.Model):
    __tablename__ = "labels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    

class Idea(db.Model):
    __tablename__ = "ideas"
    id = db.Column(db.Integer, primary_key=True)
    # True --> idea, False --> conclusion
    idea = db.Column(db.Boolean, default=True)
    title = db.Column(db.String(512), unique=True)
    content = db.Column(db.Text)
    time_create = db.Column(db.DateTime, default=datetime.utcnow)
    time_modify = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def insert(self):
        self.time_create = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        
    def modified(self, **kwargs):
        self.idea = kwargs["idea"]
        self.title = kwargs["title"] 
        self.content = kwargs["content"]
        self.time_modify = datetime.utcnow()
        self.user = kwargs['user']
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def find_by_keyword(idea, keyword, user):
        posts = Idea.query.filter_by(idea=idea, user=user).filter(
            or_(Idea.content.like(("%" + keyword + "%") if id is not None else ""),
                Idea.title.like(("%" + keyword + "%") if id is not None else "")
                )
        ).order_by(Idea.time_modify.desc()).all()
        
        return posts 

        


class Paper(db.Model):
    __tablename__ = "papers"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), unique=True)
    journal = db.Column(db.String(256))
    # journal_abb = db.Column(db.String(128))
    paper_link = db.Column(db.String(128), unique=True)
    # DOI = db.Column(db.String(128), unique=True)
    # Arx_id = db.Column(db.String(128), unique=True)
    paper_id = db.Column(db.String(256), unique=True)
    pdf_link = db.Column(db.String(512), unique=True)
    date = db.Column(db.Date)
    notes = db.relationship('Note', backref="paper", lazy='dynamic')



