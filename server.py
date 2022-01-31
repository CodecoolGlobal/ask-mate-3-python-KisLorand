import flask
from flask import Flask

app = Flask(__name__)


@app.route("/")
@app.route('/list')
def list_all():
    return flask.render_template()



@app.route("/add-question")
def add_question():
    pass


if __name__ == "__main__":
    app.run(debug=True)
