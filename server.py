import flask
from flask import Flask, request, redirect
import data_manager
import connection


app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list')
def list_all_questions():
    all_questions = connection.get_all_csv_data('sample_data/question.csv')
    return flask.render_template('index.html',all_questions=all_questions)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if request.method == "POST":
        title = request.form['title']
        message = request.form['message']

        return redirect('/')
    return flask.render_template("add_question.html")


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
