import connection
import time
import flask

PATH_ANSWERS = "sample_data/answer.csv"
PATH_QUESTIONS = "sample_data/question.csv"

MIN_QUESTION_TITLE_LEN = 6
MIN_QUESTION_MESSAGE_LEN = 10


def add_new_answer(id_input, input_text, image_path=""):
    all_answers = connection.get_all_csv_data(PATH_ANSWERS)
    new_answer = {"id": all_answers[-1].get("id"), "submission_time": time.time(), "vote_number": "1",
                  "question_id": id_input, "message": input_text, "image": image_path}
    all_answers.append(new_answer)
    connection.write_all_data_to_csv(all_answers, "ANSWERS")


def get_all_data(type):
    if type.upper() == "ANSWERS":
        return connection.get_all_csv_data(PATH_ANSWERS)
    elif type.upper() == "QUESTIONS":
        return connection.get_all_csv_data(PATH_QUESTIONS)
    return None


def question_opener(question_id):
    question = get_all_data('questions')
    all_answers = get_all_data('answers')
    for row in question:
        if row['id'] == question_id:
            question_title = row['title']
            question_message = row['message']
            question_image = row['image']
    answers = []
    for answer in all_answers:
        if answer['question_id'] == question_id:
            answers.append(answer)
    return question_title,question_message,question_image, answers


def count_view_number(question_id):
    question = get_all_data('questions')
    for row in question:
        if row['id'] == question_id:
            old_view_number = int(row['view_number'])
            old_view_number += 1
            row['view_number'] = str(old_view_number)
    connection.write_all_data_to_csv(question, 'questions')


def vote(id, type, up=False):
    datas = get_all_data(type)
    updated_datas = []
    for data in datas:
        if data['id'] == id:
            old_vote_number = int(data['vote_number'])
            if up:
                old_vote_number += 1
            else:
                old_vote_number -= 1
            data['vote_number'] = str(old_vote_number)
        updated_datas.append(data)
    print(updated_datas)
    connection.write_all_data_to_csv(updated_datas, type)


def write_all_data(type, all_data):
    if type.upper() == "ANSWERS":
        return connection.write_all_data_to_csv(all_data, type)
    elif type.upper() == "QUESTIONS":
        return connection.write_all_data_to_csv(all_data, type)
    return None


def is_new_question_valid(question_title, question_message):
    if len(question_title) > MIN_QUESTION_TITLE_LEN and len(question_message) > MIN_QUESTION_MESSAGE_LEN:
        return True
    return False

def add_new_question():
    all_question_data = get_all_data("QUESTIONS")
    new_title = flask.request.form['title']
    new_message = flask.request.form['message']
    if is_new_question_valid(new_title, new_message):
        last_question_id = all_question_data[-1]["id"]
        new_id = 1 + int(last_question_id)
        new_view_number = "0"
        new_vote_number = "0"
        submission_time = time.time()
        new_image = ""
        new_question = {"id": str(new_id), "submission_time": str(submission_time), "view_number": new_view_number,
                        "vote_number": new_vote_number, "title": new_title, "message": new_message, "image": new_image}
        all_question_data.append(new_question)
        write_all_data("QUESTIONS", all_question_data)


def delete(input_id, type):
    if type.upper() == "ANSWERS":
        file_path = PATH_ANSWERS
    elif type.upper() == "QUESTION":
        file_path = PATH_QUESTIONS
    all_datas = connection.get_all_csv_data(file_path)
    updated_datas = [data for data in all_datas if data.get("id") != input_id]
    connection.write_all_data_to_csv(updated_datas, type)


def question_editor(question_id, question_title, question_message):
    question = get_all_data('questions')
    for row in question:
        if row['id'] == question_id:
            row['title'] = question_title
            row['message'] = question_message
    connection.write_all_data_to_csv(question, 'questions')
