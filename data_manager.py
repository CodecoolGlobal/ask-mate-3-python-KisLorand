import connection


def add_new_answer(id_input, input_text):
    all_answers = connection.get_all_csv_data("/sample_data/answer.csv")
    new_answer = {"id": "0", "submission_time": "0", "vote_number": "1", "question_id": id_input,
                  "message": input_text, "image": ""}
    all_answers.append(new_answer)


def get_all_data():
    return connection.get_all_csv_data()

