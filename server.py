import flask
import requests.cookies
import requests.sessions
from flask import Flask, session
import data_manager
import random


app = Flask(__name__)
# app.secret_key = str(random.randint(0, 16))
# app.secret_key = b'_5#y2L"F4Q8z\xec]/'
app.secret_key = b'_5#y2L"F4Q8z/n&nx7c]/'


@app.route("/")
def main_page():
    questions = data_manager.latest_questions()
    return flask.render_template("main_page.html", questions=questions)


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
    print(session)
    if not check_session():
        return flask.redirect('/login')
    if flask.request.method == "POST":
        user_name = session.get('user_name')
        new_title = flask.request.form['title']
        new_message = flask.request.form['message']
        image_file = flask.request.files.get('image')
        data_manager.add_new_question(new_title, new_message, image_file, user_name)
        return flask.redirect('/list')
    return flask.render_template("add_question.html")


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def open_question(question_id):
    question_comments = data_manager.get_all_data_by_condition('comment', "question_id", 0)
    answer_comments = data_manager.get_all_data_by_condition('comment', "answer_id", 0)
    # question_tags = data_manager.get_all_data_by_condition('question_tag', "question_id", 0)
    data_manager.update_table_single_col("question", "view_number", question_id, 1)
    question_title, question_message, question_image, answers = data_manager.question_opener(question_id)
    return flask.render_template("questions.html", question_title=question_title, question_message=question_message,
                                 answers=answers, question_image=question_image, question_id=question_id,
                                 question_comments=question_comments, answer_comments=answer_comments, comment_condition=int(question_id))


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def new_answer(question_id):
    if not check_session():
        return flask.redirect('/login')
    if flask.request.method == "POST":
        user_name = session.get('user_name')
        file = flask.request.files.get("image")
        new_message = flask.request.form.get("message")
        data_manager.add_new_answer(question_id, new_message, file, user_name)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template("add_answer.html", question_id=question_id)


@app.route("/question/<id_number>/vote", methods=["GET"])
@app.route("/answer/<id_number>/vote", methods=["GET"])
def vote_answer_up(id_number):
    table_name = flask.request.args.get("table")
    vote_up = flask.request.args.get("vote-up")
    data_manager.update_table_single_col(table_name, "vote_number", id_number, vote_up)
    if table_name == "answer":
        question_id = flask.request.args.get("question_id")
        return flask.redirect(f'/question/{question_id}')
    else:
        return flask.redirect(f'/list')


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    question_id = flask.request.args.get("question_id")
    data_manager.delete(answer_id=answer_id)
    return flask.redirect(f'/question/{question_id}')


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data_manager.delete(question_id=question_id)
    return flask.redirect('/list')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    question_title, message, question_image, answers = data_manager.question_opener(question_id)
    if flask.request.method == 'POST':
        question_title = flask.request.form.get("title")
        image = flask.request.files.get('image')
        image_file = data_manager.upload_image(f"Q_{question_id}", image)
        data_manager.image_editor("question", question_id, image_file)
        message = flask.request.form.get("message")
        data_manager.question_editor(question_title, message, question_id)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_question.html', question_title=question_title, message=message,
                                 question_id=question_id)


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    answer_data = data_manager.get_entry_by_id(answer_id, "answer")
    answer_message = answer_data.get("message")
    question_id = answer_data.get("question_id")
    if flask.request.method == 'POST':
        message = flask.request.form.get("message")
        image = flask.request.files.get('image')
        image_file = data_manager.upload_image(f"A_{answer_id}", image)
        data_manager.image_editor("answer", answer_id, image_file)
        data_manager.entry_editor("answer", answer_id, message)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_answer.html', answer_message=answer_message, question_id=question_id,
                                 answer_id=answer_id)


@app.route('/search')
def search_question():
    search_phrase = flask.request.args.get('search-phrase')
    search = data_manager.get_question_titles_and_messages(search_phrase)
    search_result = []
    for result in search:
        result_dict = {}
        for key, value in result.items():
            result_dict[key] = value
        result_dict['answer_message'] = list(data_manager.get_answers_by_id(result['id']))
        search_result.append(result_dict)
    return flask.render_template('search.html', search_results=search_result, search_phrase=search_phrase)


@app.route("/question/<question_id>/new-tag", methods=["GET", "POST"])
def add_new_tag(question_id):
    if flask.request.method == "POST":
        added_tag_id = flask.request.form.get("tag-id")
        new_tag_name = flask.request.form.get("new-tag-name")
        if new_tag_name:
            added_tag_id = data_manager.add_new_tag(new_tag_name)
        data_manager.add_tag_to_question(added_tag_id, question_id)
        return flask.redirect(f"/question/{question_id}")
    tags = data_manager.get_all_data("tag", order_type="name", order_direction="ASC")
    return flask.render_template('new_tag.html', tags=tags, question_id=question_id)


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if not check_session():
        return flask.redirect('/login')
    if flask.request.method == 'POST':
        user_name = session.get('user_name')
        comment_message = flask.request.form.get('comment-message')
        data_manager.add_new_comment_q(question_id, comment_message, user_name)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('new_comment.html', question_id=question_id)


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    question_id = flask.request.args.get('question_id')
    if not check_session():
        return flask.redirect('/login')
    if flask.request.method == 'POST':
        user_name = session.get('user_name')
        comment_message = flask.request.form.get('comment-message')
        data_manager.add_new_comment_a(answer_id, comment_message, user_name)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('new_comment_A.html', question_id=question_id, answer_id=answer_id)


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment_data = data_manager.get_entry_by_id(comment_id, "comment")
    comment_message = comment_data.get("message")
    question_id = flask.request.args.get('question_id')
    if flask.request.method == 'POST':
        message = flask.request.form.get("message")
        data_manager.update_table_single_col("comment", "edited_count", comment_id, 1)
        data_manager.entry_editor("comment", comment_id, message)
        return flask.redirect(f'/question/{question_id}')
    return flask.render_template('edit_comment.html', comment_message=comment_message, comment_id=comment_id, question_id=question_id)


@app.route('/comment/<comment_id>/delete', methods=['GET', 'POST'])
def delete_comment(comment_id):
    question_id = flask.request.args.get('question_id')
    data_manager.delete_comment("comment", "id", comment_id)
    return flask.redirect(f'/question/{question_id}')


@app.route('/registration', methods=['GET', 'POST'])
def registration_page():
    if flask.request.method == "POST":
        new_user_name = flask.request.form.get("new-user-name")
        new_password = flask.request.form.get("new-password")
        data_manager.add_new_user(new_user_name, new_password)
        return flask.redirect('/')
    return flask.render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if flask.request.method == "POST":
        input_email = flask.request.form.get('new-user-name')
        input_password = flask.request.form.get('new-password')
        valid_password = data_manager.get_user_password(input_email).get("user_password")
        if data_manager.validate_login(input_password, valid_password):
            session['user_name'] = input_email
            return flask.redirect('/')
    return flask.render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout_user():
    session.clear()
    return flask.redirect('/')


def check_session():
    if 'user_name' in session:
        return True
    return False


if __name__ == "__main__":
    app.run(debug=True)
