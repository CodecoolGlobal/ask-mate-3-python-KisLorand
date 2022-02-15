import connection
import time
import os
import flask
import datetime
from sql_connection import connection_handler


# image path
UPLOAD_FOLDER = 'static/images'

# data path
PATH_ANSWERS = "sample_data/answer.csv"
PATH_QUESTIONS = "sample_data/question.csv"

MIN_QUESTION_TITLE_LEN = 6
MIN_QUESTION_MESSAGE_LEN = 10


@connection_handler
def add_new_answer(cursor, id_input, input_text, image_file):
    query = f"""INSERT INTO answer (vote_number, question_id, message) VALUES (0, '{id_input}', '{input_text}')"""
    cursor.execute(query)
    select_query = f"""SELECT id FROM answer ORDER BY id DESC LIMIT 1"""
    cursor.execute(select_query)
    image_index = cursor.fetchone().get('id')
    image_path = upload_image(f"A_{image_index}", image_file)
    new_answer_query = f"""UPDATE answer SET image='{image_path}' WHERE id='{image_index}'"""
    cursor.execute(new_answer_query)
    print("Uploaded")
    return True


@connection_handler
def get_all_data(cursor, table_name, order_type="submission_time", order_direction="DESC"):
    query = f"""SELECT * FROM "{table_name}" ORDER BY {order_type} {order_direction} """
    cursor.execute(query)
    table_data = cursor.fetchall()
    return table_data


@connection_handler
def question_opener(cursor, question_id):
    # question = get_all_data('question')
    # all_answers = get_all_data('answer')

    question_query = f"""SELECT * FROM question WHERE id='{question_id}' """
    cursor.execute(question_query)
    question_data = cursor.fetchone()

    # answer_query = f"""SELECT * FROM answer INNER JOIN question ON answer.question_id = question.id"""
    answer_query = f"""SELECT * FROM answer WHERE question_id = '{question_id}' """
    cursor.execute(answer_query)
    answers = cursor.fetchall()

    return question_data['title'], question_data['message'], question_data['image'], answers


def count_view_number(question_id):
    question = get_all_data('question')
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
    if data_type.upper() == "ANSWER":
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
    if data_type.upper() == "ANSWER":
        file_path = PATH_ANSWERS
    elif data_type.upper() == "QUESTION":
        file_path = PATH_QUESTIONS
        delete(input_id, "ANSWER", id_data_type="question_id")
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

