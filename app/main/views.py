import datetime
from fileinput import filename
import os
from flask import Flask, current_app, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
import logging 
logging.basicConfig()
logger = logging.getLogger('view')
logger.setLevel(logging.INFO)

from ..models import Note, Post, Label, Paper
from .. import db
from . import main
from ..util.downloads import get_paper_info_from_paperid, get_paper_pdf_from_paperid

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
    pagination = current_user.posts.filter_by(post_type="conclusion").\
        order_by(Post.time_modify.desc()).paginate(
            page, per_page=current_app.config["AUTOLITER_NOTES_PER_PAGE"],
            error_out=False
    )
    conclusions = pagination.items
    return render_template('post.html', posts=conclusions, pagination=pagination)


@main.route('/idea')
def idea():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.posts.filter_by(post_type='idea').\
        order_by(Post.time_modify.desc()).paginate(
            page, per_page=current_app.config["AUTOLITER_NOTES_PER_PAGE"],
            error_out=False
    )
    ideas = pagination.items
    return render_template('post.html', posts=ideas, pagination=pagination)


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
    post_idea = Post().find_by_keyword(post_type="idea", keyword=keyword, user=current_user)
    # conclusion posts
    post_conclusion = Post().find_by_keyword(post_type="conclusion", keyword=keyword, user=current_user)
    
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
        post = Post.query.get(int(id))
        return render_template('pre_post.html', post=post)


@main.route('/addpost', methods=['POST'])
def add_post():
    title = request.form.get("headline")
    content_md = request.form.get("content_md")
    content_html = request.form.get("content_html")
    postid = request.form.get('postid')
    post_type = request.form.get('post_type')
    
    user = current_user
    if not postid:
        # insert 
        post = Post(title=title, content=content_md, content_html=content_html, post_type=post_type, user=user)
        post.insert()
    else:
        # modify
        post = Post.query.get(postid)
        post.modified(title=title, content=content_md, content_html=content_html, post_type=post_type, user=user)
    
    return post_type



@main.route('/prenote', methods=["GET", "POST"])
def pre_note():
    id = request.args.get("id")
    if id == None:
        return render_template('pre_note.html', note=None, label=None, paper=None)
    else:
        note = Note.query.get(int(id))
        paper = note.paper
        labels = [i.name for i in note.labels.all()]
        labels = ';'.join(labels)
        return render_template('pre_note.html', note=note, label=labels, paper=paper)
    
    
@main.route('/addnote', methods=['POST'])
def add_note():
    title = request.form.get("headline")
    content_md = request.form.get("content_md")
    content_html = request.form.get("content_html")
    note_id = request.form.get('notetid')
    note_type = request.form.get('note_type')
    labels = request.form.get('labels')
    
    if note_type == "intensive":
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
    
    if not note_id:
        # insert 
        paper = Paper.query.filter_by(paper_id=title).first()
        post = Note(content=content_md, content_html=content_html, intensive_reading=intensive,
                    user=user, paper=paper)
        # post.labels.append()
        post.labels.extend(labels_sql)
        post.insert()
    else:
        # modify
        post = Note.query.get(int(note_id))
        for i in post.labels.all(): 
            post.labels.remove(i)
        post.labels.extend(labels_sql)
        post.modified(content=content_md, content_html=content_html, intensive=intensive, user=user)

    return note_type
    
    
@main.route('/delpost', methods=["GET", "POST"])
def del_post():
    id = request.args.get('id')
    post = Post.query.get(int(id))
    post_type = post.post_type
    
    db.session.delete(post)
    db.session.commit()
    
    if post_type == "idea":
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
            logger.info(paper.pdf_link)
            if paper.pdf_link:
                if os.path.exists(paper.pdf_link):
                    os.remove(paper.pdf_link)
    
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
    paper_id = request.form.get('paperId')
    
    paper = Paper.query.filter_by(paper_id=paper_id).first()
    if paper:
        note = paper.notes.filter_by(user=current_user).first()
        
        if note:
            return jsonify({"code": "exist_note",
                            "paper_id": paper_id,
                            "paper_pdf_link_online": paper.pdf_link_online,
                            "paper_pdf_link": paper.pdf_link,
                            "other_info": str(note.id)})
        else:
            return jsonify({"code": "exist_paper",
                            "paper_id": paper_id,
                            "paper_pdf_link_online": paper.pdf_link_online,
                            "paper_pdf_link": paper.pdf_link,
                            "other_info": ""})
    else:
        try:
            bib_dict = get_paper_info_from_paperid(paper_id)
            split_date = bib_dict['year'].split('-')
            if len(split_date) > 1:
                date_ = datetime.datetime(int(split_date[0]), int(split_date[1]), 1)
            else:
                date_ = datetime.datetime(int(split_date[0]), 1, 1)
            
            paper_ = Paper(title=bib_dict['title'], journal=bib_dict['journal'],
                        paper_link=bib_dict["url"], paper_id=paper_id,
                        pdf_link_online=bib_dict['pdf_link'], date=date_)
            paper_.insert()
            
            return jsonify({"code": "addpaper",
                    "paper_id": paper_.paper_id,
                    "paper_pdf_link_online": paper_.pdf_link_online,
                    "paper_pdf_link": paper_.pdf_link,
                    "other_info": ""})
        except:
            return jsonify({"code": "addpaper_failed"})


@main.route('/addpdf', methods=["GET", "POST"])
def add_pdf():
    paper_id = request.form.get('paperId')
    
    paper = Paper.query.filter_by(paper_id=paper_id).first()
    if paper:
        note = paper.notes.filter_by(user=current_user).first()
        pdf_link = "_".join(paper.title.split(" ")) + ".pdf"
        pdf_link = "app" + os.path.join(url_for("static", filename="pdf"), pdf_link)
        if not os.path.exists(pdf_link):
            get_paper_pdf_from_paperid(paper_id, pdf_link, direct_url=paper.pdf_link_online)
            if os.path.exists(pdf_link):
                paper.insert_pdf_link(pdf_link)
                if note:
                    return jsonify({"code": "exist_note",
                                    "paper": "exist", 
                                    "pdf": "add", 
                                    "other_info": str(note.id)})
                else:
                    return jsonify({"code": "not_note",
                                    "paper": "exist", 
                                    "pdf": "add"})
            else:
                if note:
                    return jsonify({"code": "exist_note",
                                    "paper": "exist", 
                                    "pdf": "failed",
                                    "other_info": str(note.id)})
                else:
                    return jsonify({"code": "not_note",
                                    "paper": "exist", 
                                    "pdf": "failed"})
        else:
            paper.insert_pdf_link(pdf_link)
            if note:
                return jsonify({"code": "exist_note",
                                "paper": "exist", 
                                "pdf": "exist",
                                "other_info": str(note.id)})
            else:
                return jsonify({"code": "not_note",
                                "paper": "exist", 
                                "pdf": "exist"})
    else:
        try:
            bib_dict = get_paper_info_from_paperid(paper_id)
            split_date = bib_dict['year'].split('-')
            if len(split_date) > 1:
                date_ = datetime.datetime(int(split_date[0]), int(split_date[1]), 1)
            else:
                date_ = datetime.datetime(int(split_date[0]), 1, 1)
                            
            paper_ = Paper(title=bib_dict['title'], journal=bib_dict['journal'],
                        paper_link=bib_dict["url"], paper_id=paper_id,
                        pdf_link_online=bib_dict['pdf_link'], date=date_)
            paper_.insert()
            
            pdf_link = "_".join(paper.title.split(" ")) + ".pdf"
            pdf_link = "app" + os.path.join(url_for("static", filename="pdf"), pdf_link)
            get_paper_pdf_from_paperid(paper_id, pdf_link, direct_url=paper.pdf_link_online)
            if os.path.exists(pdf_link):
                paper_.insert_pdf_link(pdf_link)
                code_ = "add"
            else:
                code_ = "failed"
            
            return jsonify({"code": "not_note",
                            "paper": "add", 
                            "pdf": code_})
        except:
            return jsonify({"code": "not_note",
                            "paper": "failed", 
                            "pdf": "failed"})

                

    
@main.route('/pdf/<pdf_name>')
def pdf_view(pdf_name):
    return render_template('pdf_view.html', pdf_name=pdf_name)
##################################

@main.route('/hand_addpaper', methods=["GET", "POST"])
def hand_addpaper():
    title = request.form.get('title')
    journal = request.form.get('journal')
    paper_link = request.form.get('paper_link')
    paper_id = request.form.get('paper_id')
    # athours = request.form.get('Athours')
    pdf_link_online = request.form.get('pdf_link_online')
    # pdf_link_paper = request.form.get('pdf_link')
    date_ = request.form.get('Date')
    
    paper = Paper.query.filter_by(paper_id=paper_id).first()
    if not paper:
        if date_:
            date_ = date_.split("-")
            date_ = datetime.datetime(int(date_[0]), int(date_[1]), int(date_[2]))
        else:
            date_ = datetime.datetime.utcnow()
        
        pdf_name = title + '.pdf'
        pdf_path = "app" + os.path.join(url_for("static", filename="pdf"), pdf_name)
        if pdf_link_online:
            
            paper = Paper(title=title, journal=journal, paper_link=paper_link,
                    paper_id=paper_id, pdf_link_online=pdf_link_online,
                    date=date_)
            paper.insert()
            get_paper_pdf_from_paperid(paper_id, pdf_path, pdf_link_online)
        else:
            paper = Paper(title=title, journal=journal, paper_link=paper_link,
                    paper_id=paper_id, date=date_)
            paper.insert()
        
        if os.path.exists(pdf_path):
            paper.insert_pdf_link(pdf_path)
            code = "add"
        else:
            code = "notadd"
        
        return jsonify({
            "pdf":code,
            "paper": "add"
        })
    else:
        pdf_name = title + '.pdf'
        pdf_path = "app" + os.path.join(url_for("static", filename="pdf"), pdf_name)
        if pdf_link_online:
            get_paper_pdf_from_paperid(paper_id, pdf_path, pdf_link_online)
    
        if os.path.exists(pdf_path):
            paper.insert_pdf_link(pdf_path)
            code = "add"
        else:
            code = "notadd"
            
        return jsonify({
            "pdf":code,
            "paper": "add"
        })
            