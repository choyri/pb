from flask import *
from flask.ext.sqlalchemy import SQLAlchemy

from credentials import *

import datetime
from os import urandom
from base64 import b64encode

app = Flask(__name__)
connectionString = "mysql://%s:%s@%s:3306/%s" % (USERNAME, PASSWORD, HOSTNAME, DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)
app.secret_key = SECRET_KEY

class Paste(db.Model):
    __tablename__ = "paste"

    content = db.Column(db.Text(length=16777216, collation='utf8_general_ci'))
    date = db.Column(db.DateTime)
    id = db.Column(db.String(9), primary_key=True, unique=True)

    def __init__(self, content, date, id):
        self.content = content
        self.date = date
        self.id = id

db.create_all()
db.session.commit()

def make_id():
    while True:
        paste = b64encode(urandom(6))
        p = Paste.query.filter_by(paste=paste).all()
        if not p:
            return paste

@app.route('/', methods=['GET', 'POST'])
@app.route('/f', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template("form.html" if 'f' in request.path else "index.html")
    elif request.method == "POST":
        if 'content' in request.form:
            try:
                p = Paste(request.form['content'], datetime.datetime.now(), make_id())
                db.session.add(p)
                db.session.commit()
                db.session.refresh(p)
            except:
                return "Failed.", 500
            
            url = url_for('paste', id=p.id)
            return redirect(url, Response=Response("{}\n".format(url)))
    
    return "Nope.", 204

@app.route('/p/<id>', methods=['GET'])
def paste(id):
    if id:
        p = Paste.query.filter_by(id=id).first()
        if p:
            return render_template("paste.html", paste=p)

    return "Not found.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10002, debug=True)