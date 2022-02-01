import flask
from flask import Flask
import data_manager
import connection


app = Flask(__name__)

MIN_QUESTION_TITLE_LEN = 6
MIN_QUESTION_MESSAGE_LEN = 10


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list')
def list_all_questions():
    all_questions = data_manager.get_all_data('sample_data/question.csv')
    return flask.render_template('index.html',all_questions=all_questions)


def is_new_question_valid(question_title, question_message):
    if len(question_title) > MIN_QUESTION_TITLE_LEN and len(question_message) > MIN_QUESTION_MESSAGE_LEN:
        return True
    return False


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    all_question_data = data_manager.get_all_data('sample_data/question.csv')
    if flask.request.method == "POST":
        new_title = flask.request.form['title']
        new_message = flask.request.form['message']
        if is_new_question_valid(new_title, new_message):
            last_question_id = all_question_data[-1]["id"]
            new_id = 1 + int(last_question_id)
            new_view_number = "0"
            new_vote_number = "0"
            # submission_time =
            submission_time = "0"
            new_image = "future path for the image"
            # new_image =
            new_question = {"id": str(new_id), "submission_time": submission_time, "view_number": new_view_number,
                            "vote_number": new_vote_number, "title": new_title, "message": new_message, "image": new_image}
            all_question_data.append(new_question)
            data_manager.write_all_data("../ask-mate-1-python-KisLorand/sample_data/question.csv", all_question_data)
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
