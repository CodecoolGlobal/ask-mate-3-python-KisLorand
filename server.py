import flask
from flask import Flask
import data_manager

app = Flask(__name__)


@app.route("/")
@app.route('/list')
def list_all():
    return flask.render_template('index.html')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def open_question(question_id):
    pass
    return flask.render_template()


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    if flask.request.method == "POST":
        data_handler.add_new_answer(question_id, flask.request.form.get("message"))
        return flask.redirect('/question/<question_id>')
    return flask.render_template("new_answer.html")


if __name__ == "__main__":
    app.run(debug=True)
