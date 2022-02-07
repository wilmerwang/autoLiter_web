import os 
import base64
import datetime
import random
from flask import jsonify, render_template, request, url_for
from . import ueditor 

def tid_maker():
    return '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())+''.join([str(random.randint(1,10)) for i in range(5)])

@ueditor.route('/', methods=['GET', 'POST'], strict_slashes=False)
def index():
    param = request.args.get('action')
    if request.method == 'GET' and param == 'config':
        return render_template('config.json')
    
    elif request.method == 'POST' and request.args.get('action') == 'uploadimage':
        f = request.files['upfile']
        filename = f.filename
        save_path = "app/static/upload/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        f.save(save_path + filename)
        
        result = {
            'state': 'SUCCESS',
            'url': f'../static/upload/{filename}',
            'title': filename,
            'original': filename
        }
        return jsonify(result)
    
    elif request.method == 'POST' and request.args.get('action') == 'uploadfile':
        f = request.files['upfile']
        filename = f.filename
        save_path = "app/static/upload/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        f.save(save_path + filename)
        
        result = {
            'state': 'SUCCESS',
            'url': f'../static/upload/{filename}',
            'title': filename,
            'original': filename
        }
        return jsonify(result) 
    
    elif request.method == 'POST' and request.args.get('action') == 'uploadscrawl':
        base64data = request.form['upfile']
        img = base64.b64decode(base64data)
        filename = tid_maker() + '.png'
        save_path = "app/static/upload/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with open(os.path.join(save_path, filename), 'wb') as fp:
            fp.write(img)
        
        result = {
            'state': 'SUCCESS',
            'url': f'../static/upload/{filename}',
            'title': filename,
            'original': filename
        }
        return jsonify(result) 
