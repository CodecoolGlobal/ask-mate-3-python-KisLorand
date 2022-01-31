import flask
from flask import Flask, request, redirect

app = Flask(__name__)


@app.route("/")
def main_page():
    return flask.render_template("useless_main_page.html")


@app.route('/list')
def list_all():
    return flask.render_template('index.html')


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
    return "new_answer"


if __name__ == "__main__":
    app.run(debug=True)
