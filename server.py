import flask
from flask import Flask
import data_manager
import sort


app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("main_page.html")


@app.route('/list', methods=['GET', 'POST'])
def list_all_questions():
    questions_order = flask.request.args.get('questions_order')
    order_direction = flask.request.args.get('order_direction')
    if questions_order and order_direction:
        all_questions = data_manager.get_all_data('question', questions_order, order_direction)
    else:
        all_questions = data_manager.get_all_data('question')
    return flask.render_template('index.html', all_questions=all_questions,
                                 questions_order_val=questions_order, order_direction_val=order_direction)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if flask.request.method == "POST":
        new_title = flask.request.form['title']
        new_message = flask.request.form['message']
        image_file = flask.request.files.get('image')
        data_manager.add_new_question(new_title, new_message, image_file)
        return flask.redirect('/list')
    return flask.render_template("add_question.html")


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def open_question(question_id):
    data_manager.count_view_number(question_id)
    question_title, question_message, question_image, answers = data_manager.question_opener(question_id)
    return flask.render_template("questions.html", question_title=question_title, question_message=question_message,
                                 answers=answers, question_image=question_image, question_id=question_id)


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    if flask.request.method == "POST":
        file = flask.request.files.get("image")
        new_message = flask.request.form.get("message")
        data_manager.add_new_answer(question_id, new_message, file)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template("add_answer.html", question_id=question_id)


# @app.route('/question/<question_id>/vote_up/<questions_order_val>/<order_direction_val>')
# def question_vote_up(question_id, questions_order_val, order_direction_val):
#     data_manager.vote(question_id, "questions", up=True)
#     return flask.redirect(f'/list?questions_order={ questions_order_val }&order_direction={ order_direction_val }')
#
#
# @app.route('/question/<question_id>/vote_down/<questions_order_val>/<order_direction_val>')
# def question_vote_down(question_id, questions_order_val, order_direction_val):
#     data_manager.vote(question_id, "questions", up=False)
#     return flask.redirect(f'/list?questions_order={ questions_order_val }&order_direction={ order_direction_val }')


@app.route("/question/<id_number>/vote", methods=["GET"])
@app.route("/answer/<id_number>/vote", methods=["GET"])
def vote_answer_up(id_number):
    table_name = flask.request.args.get("table")
    vote_up = flask.request.args.get("vote-up")
    data_manager.update_table_single_col(table_name, "vote_number", id_number, vote_up)
    if table_name == "answer":
        question_id = flask.request.args.get("question_id ")
        return flask.redirect(f'/question/{question_id}')
    else:
        return flask.redirect(f'/list')


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
    question_title, message, question_image, answers = data_manager.question_opener(question_id)
    if flask.request.method == 'POST':
        question_title = flask.request.form.get("title")
        image_file = flask.request.files.get('image')
        message = flask.request.form.get("message")
        data_manager.entry_editor(question_id, message, image_file, 'questions', question_title)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_question.html', question_title=question_title, message=message, question_id=question_id)


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    answers = data_manager.get_all_data('answer')
    image_file = flask.request.files.get("image")
    answer_message, question_id = data_manager.get_entry_by_id(answer_id, answers, False)
    if flask.request.method == 'POST':
        message = flask.request.form.get("message")
        data_manager.get_entry_by_id(answer_id, answers, True, message, image_file)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_answer.html', answer_message=answer_message, answer_id=answer_id, question_id=question_id)


if __name__ == "__main__":
    app.run(debug=True)
