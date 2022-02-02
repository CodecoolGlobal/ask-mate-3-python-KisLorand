import flask
from flask import Flask
import data_manager
import connection


app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list', methods=['GET', 'POST'])
def list_all_questions(questions_order="by_submission_time"):
    all_questions = data_manager.get_all_data('questions')
    questions_order_val = "submission time"
    order_direction_val = "descending"
    if flask.request.method == "GET":

        questions_order_val = flask.request.args.get("questions_order")
        order_direction_val = flask.request.args.get("order_direction")

        all_questions_copy = all_questions[:]
        new_questions_list = []

        QUESTION_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
        for order_type in QUESTION_HEADERS
            if questions_order_val == order_type:
                while len(new_questions_list) != len(all_questions):

                    first_value = all_questions_copy[0]
                    for compared_question in all_questions_copy:
                        if first_value[order_type] > compared_question[order_type]:
                            first_value = compared_question
                    new_questions_list.append(first_value)

                    for question in all_questions_copy:
                        if question["id"] == first_value["id"]:
                            all_questions_copy.remove(question)

        print(new_questions_list)

    return flask.render_template('index.html',all_questions=new_questions_list, questions_order_val=questions_order_val, order_direction_val=order_direction_val)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if flask.request.method == "POST":
        data_manager.add_new_question()
        return flask.redirect('/list')
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
