import flask
from flask import Flask
import data_manager



app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list')
def list_all_questions():
    all_questions = data_manager.get_all_data('sample_data/question.csv')
    return flask.render_template('index.html',all_questions=all_questions)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if flask.request.method == "POST":
        title = flask.request.form['title']
        message = flask.request.form['message']

        return flask.redirect('/')
    return flask.render_template("add_question.html")


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def open_question(question_id):
    pass
    return flask.render_template("useless_main_page.html")


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    if flask.request.method == "POST":
        data_manager.add_new_answer(question_id, flask.request.form.get("message"))
        return flask.redirect('/question/<question_id>')
    return flask.render_template("add_answer.html")


if __name__ == "__main__":
    app.run(debug=True)
