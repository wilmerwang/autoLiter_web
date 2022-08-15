from random import randint
import random
import sys 
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import Post, User, Note, Label, Paper, note_label


def users(count=2):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='cat',
                 confirmed=True)
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            # pass 
            db.session.rollback()


def labels(count=20):
    fake = Faker()
    i = 0
    while i < count:
        la = Label(name=fake.word())
        db.session.add(la)
        try:
            db.session.commit()
            i += 1
        except:
            pass 
    
def papers(count=50):
    fake = Faker()
    i = 0
    while i < count:
        p = Paper(title=fake.file_name(),
                  journal=fake.company(),
                  paper_id=fake.url(),
                  paper_link=fake.url(),
                  pdf_link=fake.uri_extension(),
                  date=fake.date_time())
        db.session.add(p)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            # pass 
            db.session.rollback()

def notes(count=50):
    fake = Faker()
    user_count = User.query.count()
    paper_count = Paper.query.count()
    i = 0
    while i < count:
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Paper.query.offset(randint(0, paper_count - 1)).first()
        note = Note(content=fake.paragraph(),
                    content_html=fake.paragraph(),
                    intensive_reading=fake.boolean(),
                    time_create=fake.past_date(),
                    time_modify=fake.past_date(),
                    user=u,
                    paper=p)
        db.session.add(note)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            # pass 
            db.session.rollback()
            
def note_labels():
    label_count = Label.query.count()
    note_count = Note.query.count()
    for i in range(note_count):
        n = Note.query.get(i+1)
        l_ids = random.sample(range(1, label_count), int(label_count/2))
        for j in l_ids:
            l = Label.query.get(j+1)
            n.labels.append(l)
        db.session.add(n)
    db.session.commit()

            
def posts(count=100):
    fake = Faker()
    post_types = ['idea', 'conclusion']
    user_count = User.query.count()
    i = 0
    while i < count:
        u = User.query.offset(randint(0, user_count - 1)).first()
        post = Post(post_type=post_types[random.randint(0,1)],
                    title=fake.words(),
                    content=fake.paragraphs(),
                    content_html=fake.paragraphs(),
                    time_create=fake.past_date(),
                    time_modify=fake.past_date(),
                    user=u)
        db.session.add(post)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            # pass 
            db.session.rollback()


if __name__ == "__main__":

    from app import db 
    db.create_all() 
    from app.fake import *
    users()
    labels()
    papers()
    notes()
    note_labels()
    posts()
        
