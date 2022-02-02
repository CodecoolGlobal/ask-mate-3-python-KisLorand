import connection
import time

PATH_ANSWERS = "sample_data/answer.csv"
PATH_QUESTIONS = "sample_data/question.csv"


def add_new_answer(id_input, input_text, image_path=""):
    all_answers = connection.get_all_csv_data(PATH_ANSWERS)
    new_answer = {"id": str(len(all_answers)), "submission_time": time.time(), "vote_number": "1",
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
