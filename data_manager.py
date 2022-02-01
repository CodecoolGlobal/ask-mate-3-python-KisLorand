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
