import csv
import logging
import os

from flask import Blueprint, render_template, abort, url_for, current_app
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound
from sqlalchemy import func

from app.db import db
from app.db.models import Song, User
from app.songs.forms import csv_upload
from werkzeug.utils import secure_filename, redirect

songs = Blueprint('songs', __name__,
                  template_folder='templates')

@songs.route('/songs', methods=['GET'], defaults={"page": 1})
@songs.route('/songs/<int:page>', methods=['GET'])
def songs_browse(page):

    page = page
    per_page = 1000
    pagination = Song.query.paginate(page, per_page, error_out=False)
    data = pagination.items
    balance = current_user.balance
    try:
        return render_template('browse_songs.html', data=data, pagination=pagination, balance=balance)
    except TemplateNotFound:
        abort(404)


@songs.route('/songs/upload', methods=['POST', 'GET'])
@login_required
def songs_upload():
    form = csv_upload()
    if form.validate_on_submit():
        log = logging.getLogger("csvlog")
        log.info('csv upload done!')
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)
        # user = current_user
        balance = current_user.balance
        list_of_songs = []
        initial_balance = 0
        if current_user.balance is None:
            balance = initial_balance
        else:
            balance = current_user.balance
        log.info(balance)
        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                #row['\ufeffAMOUNT'].astype(int)
                #print(type(row['\ufeffAMOUNT']))
                transaction = Song(row['\ufeffAMOUNT'], row['TYPE'])
                #total = total + row['AMOUNT']
                list_of_songs.append(Song(row['\ufeffAMOUNT'], row['TYPE']))
                #db.session.add(transaction)
                balance = balance + float(row['\ufeffAMOUNT'])
        #average = db.session.query(func.avg(Song.AMOUNT).label('average'))
        #sum = Song.query.with_entities(func.sum(Song.AMOUNT).label('total')).first().total
        #print(total)
        #avg = Song.query.execute('SELECT SUM(amount) FROM songs')
        #total = db.session.execute(sum)
        #a = avg.first()[0]
        #t = total.first()[0]
        #print(a)
        #print(t)
        #print(Song.AMOUNT)
        current_user.songs = list_of_songs

        current_user.balance = balance
        #print(total)
        log = logging.getLogger("csvlogs")
        log.info('User Balance done!')
        db.session.commit()

        return redirect(url_for('songs.songs_browse'))

    try:
        return render_template('upload.html', form=form)
    except TemplateNotFound:
        abort(404)
