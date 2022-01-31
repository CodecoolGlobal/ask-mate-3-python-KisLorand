import flask
from flask import Flask

app = Flask(__name__)


@app.route("/")
@app.route('/list')
def list_all():
    return flask.render_template()


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def open_question(quiestion_id):
    pass
    return flask.render_template()


if __name__ == "__main__":
    app.run(debug=True)
