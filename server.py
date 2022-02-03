import flask
from flask import Flask, url_for
import data_manager
import connection
import sort


app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list', methods=['GET', 'POST'])
def list_all_questions():
    all_questions = data_manager.get_all_data('questions')
    questions_order_val = sort.get_order_value("questions_order", "submission_time")
    order_direction_val = sort.get_order_value("order_direction", "descending")
    display_questions_list = all_questions
    if flask.request.method == "GET":
        display_questions_list, questions_order_val, order_direction_val = sort.sort_main(all_questions, questions_order_val,
                                                                                      order_direction_val)
    return flask.render_template('index.html', all_questions=display_questions_list,
                                 questions_order_val=questions_order_val, order_direction_val=order_direction_val)


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
    return flask.render_template("questions.html", question_title=question_title, question_message=question_message,
                                 answers=answers, question_image=question_image, question_id=question_id)


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    if flask.request.method == "POST":
        file = flask.request.files.get("image")
        data_manager.add_new_answer(question_id, flask.request.form.get("message"), file)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template("add_answer.html", question_id=question_id)


@app.route('/question/<question_id>/vote_up/<questions_order_val>/<order_direction_val>')
def question_vote_up(question_id, questions_order_val, order_direction_val):
    data_manager.vote(question_id, "questions", up=True)
    return flask.redirect(f'/list?questions_order={ questions_order_val }&order_direction={ order_direction_val }')


@app.route('/question/<question_id>/vote_down/<questions_order_val>/<order_direction_val>')
def question_vote_down(question_id, questions_order_val, order_direction_val):
    data_manager.vote(question_id, "questions", up=False)
    return flask.redirect(f'/list?questions_order={ questions_order_val }&order_direction={ order_direction_val }')


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


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data_manager.delete(question_id, "QUESTIONS")
    return flask.redirect('/list')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    question_title,message,question_image, answers = data_manager.question_opener(question_id)
    if flask.request.method == 'POST':
        question_title = flask.request.form.get("title")
        message = flask.request.form.get("message")
        data_manager.question_editor(question_id, question_title, message, 'questions')
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_question.html', question_title=question_title, message=message, question_id=question_id)


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    answers = data_manager.get_all_data('answers')
    question_title = ""
    for row in answers:
        if row['id'] == answer_id:
            answer_message = row['message']
    if flask.request.method == 'POST':
        message = flask.request.form.get("message")
        for row in answers:
            if row['id'] == answer_id:
                question_id = row['question_id']
                row['message'] = message
                data_manager.question_editor(question_id, question_title, message, 'answers')
                return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_answer.html', answer_message=answer_message, answer_id=answer_id)


if __name__ == "__main__":
    app.run(debug=True)
