from flask import Blueprint, render_template, request, redirect, url_for
import nltk
from nltk.corpus import wordnet
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

bp = Blueprint('intbot', __name__)

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

@bp.route('/', methods=('GET', 'POST'))
def index():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        print(name)
        intellectualify(name)
    return render_template('intbot/index.html', form=form)


def intellectualify(input_word):
    for ss in wn.synsets(input_word):
        print(wordnet.synsets(input_word)[0].hypernyms()[0].lemma_names())
