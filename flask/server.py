from functions import *
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
url = "http://es01:9200"

UPLOAD_FOLDER = '../data/file'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

index_name = "df"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    import json
    word = request.args["item"]
    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = show_es(url, index_name, search_col = ["文"], search_word = word, size=10, from_ = (page - 1) * 10)
    pagination = Pagination(page=page, total=res["hits"]["total"]["value"], per_page=10, css_framework='bootstrap5')
    return render_template("search.html", hits = res["hits"]["hits"], value = word, pagination=pagination)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file_():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            upload_file(path, url, index_name)
            return render_template("uploaded.html", filename = filename)
    return render_template("upload.html")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)