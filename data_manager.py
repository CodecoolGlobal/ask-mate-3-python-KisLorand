import connection
import time
import os
import flask


# image path
UPLOAD_FOLDER = 'static/images'

# data path
PATH_ANSWERS = "sample_data/answer.csv"
PATH_QUESTIONS = "sample_data/question.csv"

MIN_QUESTION_TITLE_LEN = 6
MIN_QUESTION_MESSAGE_LEN = 10


def add_new_answer(id_input, input_text, image_file):
    all_answers = connection.get_all_csv_data(PATH_ANSWERS)
    new_id = int(all_answers[-1].get("id"))+1
    image_path = upload_image(f"A_{new_id}", image_file)
    new_answer = {"id": str(new_id), "submission_time": time.time(), "vote_number": "1",
                  "question_id": id_input, "message": input_text, "image": image_path if image_path is not None else ""}
    all_answers.append(new_answer)
    connection.write_all_data_to_csv(all_answers, "ANSWERS")


def get_all_data(data_type):
    if data_type.upper() == "ANSWERS":
        return connection.get_all_csv_data(PATH_ANSWERS)
    elif data_type.upper() == "QUESTIONS":
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


def vote(id, data_type, up=False):
    datas = get_all_data(data_type)
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
    connection.write_all_data_to_csv(updated_datas, data_type)


def write_all_data(data_type, all_data):
    if data_type.upper() == "ANSWERS":
        return connection.write_all_data_to_csv(all_data, data_type)
    elif data_type.upper() == "QUESTIONS":
        return connection.write_all_data_to_csv(all_data, data_type)
    return None


def is_new_question_valid(question_title, question_message):
    if len(question_title) > MIN_QUESTION_TITLE_LEN and len(question_message) > MIN_QUESTION_MESSAGE_LEN:
        return True
    return False


def format_new_question(all_question_data, new_title, new_message, image_file):
    last_question_id = all_question_data[-1]["id"]
    new_id = 1 + int(last_question_id)
    submission_time = time.time()
    new_image = upload_image(f'Q_{new_id}', image_file)
    new_question = {"id": str(new_id), "submission_time": str(submission_time), "view_number": "0",
                    "vote_number": "0", "title": new_title, "message": new_message,
                    "image": new_image if new_image is not None else ""}
    return new_question


def add_new_question(new_title, new_message, image_file):
    all_question_data = get_all_data("QUESTIONS")
    if is_new_question_valid(new_title, new_message):
        new_question = format_new_question(all_question_data, new_title, new_message, image_file)
        all_question_data.append(new_question)
        write_all_data("QUESTIONS", all_question_data)


def delete_image(image_path):
    if image_path != "":
        correct_path = f"static/{image_path}"
        if os.path.exists(correct_path):
            os.remove(correct_path)


def delete(input_id, data_type, id_data_type="id"):
    if data_type.upper() == "ANSWERS":
        file_path = PATH_ANSWERS
    elif data_type.upper() == "QUESTIONS":
        file_path = PATH_QUESTIONS
        delete(input_id, "ANSWERS", id_data_type="question_id")
    all_datas = connection.get_all_csv_data(file_path)
    updated_datas = []
    for datas in all_datas:
        if datas.get(id_data_type) != input_id:
            updated_datas.append(datas)
        else:
            delete_image(datas.get("image"))
    connection.write_all_data_to_csv(updated_datas, data_type)


def upload_image(img_name, image_request):
    if image_request.filename == "":
        return None
    name_ext = image_request.filename.split('.')
    extension = name_ext[1]
    img_name = f'{img_name}.{extension}'
    image_request.save(os.path.join(UPLOAD_FOLDER, img_name))
    splitted_path = UPLOAD_FOLDER.split('/')
    return f'{splitted_path[1]}/{img_name}'


def get_entry_by_id(entry_id, answers, entry_post, message="", image_file=""):
    for row in answers:
        if row['id'] == entry_id:
            answer_message = row['message']
            question_id = row['question_id']
            if entry_post:
                row['message'] = message
                entry_editor(entry_id, message, image_file, 'answers')
            else:
                return answer_message, question_id


def entry_editor(id_input, message, image_file, data_type, question_title=""):
    data = get_all_data(data_type)
    for row in data:
        if data_type == "questions":
            if row['id'] == id_input:
                delete_image(row["image"])
                row["image"] = upload_image(f"Q_{row['id']}", image_file)
                row['title'] = question_title
                row['message'] = message
        elif data_type == "answers":
            if row['id'] == id_input:
                delete_image(row["image"])
                row["image"] = upload_image(f"A_{row['id']}", image_file)
                row['message'] = message
    connection.write_all_data_to_csv(data, data_type)

