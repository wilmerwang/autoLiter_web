import datetime
import os 
from flask import Flask, current_app, render_template, request, redirect, url_for
from flask_login import current_user

from ..models import Note, Idea, Label, Paper
from .. import db
from . import main
from ..util.utils import metaExtracter, urlDownload, download

@main.before_request
def before_request():
    if not current_user.is_authenticated:
        url = request.path
        white_list = [url_for(i) for i in ["main.index"]]
        if url in white_list:
            pass 
        else:
            return redirect(url_for('auth.login'))
    else:
        if not current_user.confirmed and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/intensive')
def intensive_reading():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.notes.filter_by(intensive_reading=True).\
        order_by(Note.time_modify.desc()).paginate(
            page, per_page=current_app.config["AUTOLITER_NOTES_PER_PAGE"],
            error_out=False
    )
    notes = pagination.items
    return render_template('note.html', notes=notes, pagination=pagination)


@main.route('/skimming')
def skimming():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.notes.filter_by(intensive_reading=False).\
        order_by(Note.time_modify.desc()).paginate(
            page, per_page=current_app.config["AUTOLITER_NOTES_PER_PAGE"],
            error_out=False
    )
    notes = pagination.items
    return render_template('note.html', notes=notes, pagination=pagination)


@main.route('/conclusion')
def conclusion():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.ideas.filter_by(idea=False).\
        order_by(Idea.time_modify.desc()).paginate(
            page, per_page=current_app.config["AUTOLITER_NOTES_PER_PAGE"],
            error_out=False
    )
    ideas = pagination.items
    return render_template('post.html', ideas=ideas, pagination=pagination)


@main.route('/idea')
def idea():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.ideas.filter_by(idea=True).\
        order_by(Idea.time_modify.desc()).paginate(
            page, per_page=current_app.config["AUTOLITER_NOTES_PER_PAGE"],
            error_out=False
    )
    ideas = pagination.items
    return render_template('post.html', ideas=ideas, pagination=pagination)


#####################################################
# TODO
# @main.route('/archive')
# def archive():
#     return render_template('archive.html')

@main.route('/label/<name>')
def label(name):
    # 精读 略读
    print(Label.query.filter_by(name=name).first().note)
    notes = Label.query.filter_by(name=name).first().note\
        .filter(Note.user==current_user).order_by(Note.time_modify.desc()).all()
    
    return render_template('label.html', notes=notes)


@main.route('/search', methods=["GET", "POST"])
def search():
    keyword = request.args.get('keyword')
    
    # idea posts
    post_idea = Idea().find_by_keyword(idea=True, keyword=keyword, user=current_user)
    # conclusion posts
    post_conclusion = Idea().find_by_keyword(idea=False, keyword=keyword, user=current_user)
    
    # intensive
    note_intensive = Note.find_by_keyword(intensive=True, keyword=keyword, user=current_user)
    # sk
    note_skimming = Note.find_by_keyword(intensive=False, keyword=keyword, user=current_user)
    
    return render_template('search.html', keyword=keyword, ideas=post_idea,
                           conclusions=post_conclusion, intensives=note_intensive,
                           skimmings=note_skimming)
    
###################################################


@main.route('/prepost', methods=["GET", "POST"])
def pre_post():
    id = request.args.get("id")
    if id == None:
        return render_template('pre_post.html', post=None)
    else:
        post = Idea.query.get(id)
        return render_template('pre_post.html', post=post)


@main.route('/addpost', methods=['POST'])
def add_post():
    title = request.form.get("headline")
    content = request.form.get("content")
    postid = request.form.get('postid')
    
    if request.form.get('idea') == "1":
        idea = False
    else:
        idea = True 
    user = current_user
    
    if postid == "":
        # insert 
        post = Idea(title=title, content=content, idea=idea, user=user)
        post.insert()
    else:
        # modify
        post = Idea.query.get(postid)
        post.modified(title=title, content=content, idea=idea, user=user)
    
    if idea:
        return "idea"
    else:
        return "conclusion"



@main.route('/prenote', methods=["GET", "POST"])
def pre_note():
    id = request.args.get("id")
    if id == None:
        return render_template('pre_note.html', post=None)
    else:
        post = Note.query.get(id)
        return render_template('pre_note.html', post=post)
    
    
@main.route('/addnote', methods=['POST'])
def add_note():
    title = request.form.get("headline")
    content = request.form.get("content")
    postid = request.form.get('postid')
    labels = request.form.get('labels')
    
    if request.form.get('intensive') == "1":
        intensive = True
    else:
        intensive = False 
    user = current_user
    
    labels = [i for i in labels.split(';') if i != '']
    labels_sql = []
    for l in labels:
        lb = Label.query.filter_by(name=l).first()
        if not lb:
            lb = Label(name=l)
            db.session.add(lb)
        labels_sql.append(lb)
    db.session.commit()
    
    if postid == "":
        # insert 
        paper = Paper.query.filter_by(paper_id=title).first()
        post = Note(content=content, intensive_reading=intensive, user=user, 
                    paper=paper)
        # post.labels.append()
        post.labels.extend(labels_sql)
        post.insert()
    else:
        # modify
        post = Note.query.get(int(postid))
        for i in post.labels.all(): 
            post.labels.remove(i)
        post.labels.extend(labels_sql)
        post.modified(content=content, intensive=intensive, user=user)

    if intensive:
        return "intensive"
    else:
        return "skimming"
    
    
@main.route('/delpost', methods=["GET", "POST"])
def del_post():
    id = request.args.get('id')
    post = Idea.query.get(int(id))
    idea = post.idea
    
    db.session.delete(post)
    db.session.commit()
    
    if idea:
        return redirect(url_for("main.idea"))
    else:
        return redirect(url_for("main.conclusion"))


@main.route('/delnote', methods=["GET", "POST"])
def del_note():
    id = request.args.get('id')
    note = Note.query.get(int(id))
    intensive = note.intensive_reading
    
    paper = note.paper
    if paper:
        if len(paper.notes.all()) > 1:
            pass 
        else:
            db.session.delete(paper)
            if os.path.exists("app"+paper.pdf_link):
                os.remove("app"+paper.pdf_link)
    
    db.session.delete(note)
    db.session.commit()
    
    if intensive:
        return redirect(url_for('main.intensive_reading'))
    else:
        return redirect(url_for('main.skimming'))
    

##################################
# 下载文献信息
@main.route('/addpaper', methods=["GET", "POST"])
def add_paper():
    paper_id = request.form.get('DoiArxivId')
    download_pdf = request.form.get('pdf')
    
    paper = Paper.query.filter_by(paper_id=paper_id).first()
    if paper:
        note = paper.notes.filter_by(user=current_user).first()
        
        if paper.pdf_link:
            if note:
                return str(note.id)
            else:
                return "exist_paper_pdf"
        else:
            bib_dict = download(paper_id, download_pdf)
            if "pdf_path" in bib_dict.keys():
                paper.pdf_link = bib_dict['pdf_path']
                db.session.add(paper)
                db.session.commit()
            if note:
                return str(note.id)
            else:
                return "exist_paper_not_pdf"
    
        # if note:
        #     return str(note.id)
        # else:
        #     if paper.pdf_link:
        #         print("")
        #         return "exist_paper_pdf"
        #     else:
        #         bib_dict = download(paper_id, download_pdf)
        #         if "pdf_path" in bib_dict.keys():
        #             paper.pdf_link = bib_dict['pdf_path']
        #             db.session.add(paper)
        #             db.session.commit()
        #         return "exist_paper_not_pdf"
    else:
        bib_dict = download(paper_id, download_pdf)
        # insert paper
        split_date = bib_dict['year'].split('-')
        if len(split_date) > 1:
            date_ = datetime.datetime(int(split_date[0]), int(split_date[1]), 1)
        else:
            date_ = datetime.datetime(int(split_date[0]), 1, 1)
        if "pdf_path" in bib_dict.keys():
            paper_ = Paper(title=bib_dict['title'], journal=bib_dict['journal'],
                        paper_link=bib_dict["url"], paper_id=paper_id,
                        pdf_link=bib_dict['pdf_path'], date=date_)
        else:
            paper_ = Paper(title=bib_dict['title'], journal=bib_dict['journal'],
                        paper_link=bib_dict["url"], paper_id=paper_id,date=date_)
        db.session.add(paper_)
        db.session.commit()
        
        return "addpaper"
    
@main.route('/pdf/<pdf_name>')
def pdf_view(pdf_name):
    return render_template('pdf_view.html', pdf_name=pdf_name)
##################################