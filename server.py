from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/add-question")
def add_question():
    pass


if __name__ == "__main__":
    app.run()
