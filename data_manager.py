import connection
import time

PATH_ANSWERS = "sample_data/answer.csv"
PATH_QUESTIONS = "sample_data/question.csv"

def add_new_answer(id_input, input_text):
    all_answers = connection.get_all_csv_data(path="sample_data/answer.csv")
    new_answer = {"id": "0", "submission_time": time.time(), "vote_number": "1", "question_id": id_input,
                  "message": input_text, "image": ""}
    all_answers.append(new_answer)
    print(new_answer)

def get_all_data(type):
    if type.upper() == "ANSWERS":
        return connection.get_all_csv_data(PATH_ANSWERS)
    elif type.upper() == "QUESTIONS":
        return connection.get_all_csv_data(PATH_QUESTIONS)
    return None


def write_all_data(type, all_data):
    if type.upper() == "ANSWERS":
        return connection.write_all_data_to_csv(PATH_ANSWERS, all_data)
    elif type.upper() == "QUESTIONS":
        return connection.write_all_data_to_csv(PATH_QUESTIONS, all_data)
    return None
