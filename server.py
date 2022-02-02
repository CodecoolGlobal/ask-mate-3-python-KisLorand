import flask
from flask import Flask
import data_manager
import connection
import time


app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list')
def list_all_questions():
    all_questions = data_manager.get_all_data('questions')

    return flask.render_template('index.html',all_questions=all_questions)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if flask.request.method == "POST":
        data_manager.add_new_question()
        return flask.redirect('/')
    return flask.render_template("add_question.html")


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def open_question(question_id):
    data_manager.count_view_number(question_id)
    question_title,question_message,question_image, answers = data_manager.question_opener(question_id)
    return flask.render_template("questions.html", question_title=question_title, question_message=question_message, answers=answers, question_image=question_image, question_id=question_id)


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    if flask.request.method == "POST":
        data_manager.add_new_answer(question_id, flask.request.form.get("message"))
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template("add_answer.html", question_id=question_id)


@app.route('/question/<question_id>/vote_up')
def question_vote_up(question_id):
    data_manager.vote(question_id, "questions", up=True)
    return flask.redirect('/list')


@app.route('/question/<question_id>/vote_down')
def question_vote_down(question_id):
    data_manager.vote(question_id, "questions", up=False)
    return flask.redirect('/list')


@app.route("/answer/<answer_id>/vote_up", methods=["GET"])
def vote_answer_up(answer_id):
    question_id = flask.request.args.get("question_id")
    data_manager.vote(answer_id, "answers", up=True)
    return flask.redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/vote_down", methods=["GET"])
def vote_answer_down(answer_id):
    question_id = flask.request.args.get("question_id")
    data_manager.vote(answer_id, "answers", up=False)
    return flask.redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    question_id = flask.request.args.get("question_id")
    data_manager.delete(answer_id, "ANSWERS")
    return flask.redirect(f'/question/{question_id}')


if __name__ == "__main__":
    app.run(debug=True)
