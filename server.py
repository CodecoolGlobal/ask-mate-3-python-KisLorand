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
    all_question_data = data_manager.get_all_data("QUESTIONS")
    if flask.request.method == "POST":
        new_title = flask.request.form['title']
        new_message = flask.request.form['message']
        if data_manager.is_new_question_valid(new_title, new_message):
            last_question_id = all_question_data[-1]["id"]
            new_id = 1 + int(last_question_id)
            new_view_number = "0"
            new_vote_number = "0"
            submission_time = time.time()
            new_image = ""
            new_question = {"id": str(new_id), "submission_time": str(submission_time), "view_number": new_view_number,
                            "vote_number": new_vote_number, "title": new_title, "message": new_message, "image": new_image}
            all_question_data.append(new_question)
            data_manager.write_all_data("QUESTIONS", all_question_data)
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
    data_manager.delete(answer_id, "ANSWER")
    return flask.redirect(f'/question/{question_id}')


if __name__ == "__main__":
    app.run(debug=True)
