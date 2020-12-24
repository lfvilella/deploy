from flask import Flask

from google.cloud import storage
from google.cloud import firestore
from google.cloud import ndb


class BookModel(ndb.Model):
    title = ndb.StringProperty()


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/ndb')
def ndb_handler():
    with ndb.Client().context():
        total = BookModel.query().count()
    return f'total books {total}'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
