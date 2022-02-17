from datetime import datetime

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
def update_table_single_col(cursor, table_name, col_name, id_number, vote_up):
    query = f""" UPDATE {table_name} SET {col_name}={col_name}+{vote_up} WHERE id={id_number} """
    cursor.execute(query)


@connection_handler
def add_new_answer(cursor, id_input, input_text, image_file):
    current_time: datetime = datetime.datetime.now()
    query = f""" INSERT INTO answer (submission_time, vote_number, question_id, message) VALUES ('{current_time}', 0, '{id_input}', '{input_text}') """
    cursor.execute(query)
    select_query = f""" SELECT id FROM answer ORDER BY id DESC LIMIT 1 """
    cursor.execute(select_query)

    image_index = cursor.fetchone().get('id')
    image_path = upload_image(f"A_{image_index}", image_file)
    new_answer_query = f""" UPDATE answer SET image='{image_path}' WHERE id='{image_index}' """
    cursor.execute(new_answer_query)
    return True


@connection_handler
def get_all_data(cursor, table_name, order_type="submission_time", order_direction="DESC"):
    query = f""" SELECT * FROM "{table_name}" ORDER BY {order_type} {order_direction} """
    cursor.execute(query)
    table_data = cursor.fetchall()
    return table_data


@connection_handler
def question_opener(cursor, question_id):
    question_query = f""" SELECT * FROM question WHERE id='{question_id}' """
    cursor.execute(question_query)
    question_data = cursor.fetchone()

    answer_query = f""" SELECT * FROM answer WHERE question_id = '{question_id}' """
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


@connection_handler
def add_new_question(cursor, new_title, new_message, image_file):
    if is_new_question_valid(new_title, new_message):
        current_time = datetime.datetime.now()
        insert_new_question = f""" INSERT INTO question (submission_time, view_number, vote_number, title, message) 
                                   VALUES ('{current_time}', 0, 0, '{new_title}', '{new_message}') """
        cursor.execute(insert_new_question)
        select_query = f""" SELECT id FROM question ORDER BY id DESC LIMIT 1 """
        cursor.execute(select_query)

        image_index = cursor.fetchone().get('id')
        image_path = upload_image(f"Q_{image_index}", image_file)
        new_answer_query = f""" UPDATE question SET image='{image_path}' WHERE id='{image_index}' """
        cursor.execute(new_answer_query)
        return True


def delete_image(image_path):
    if image_path != "":
        correct_path = f"static/{image_path}"
        if os.path.exists(correct_path):
            os.remove(correct_path)


@connection_handler
def delete(cursor, input_id, table_name, id_data_type="id"):
    delete_query = f""" DELETE FROM {table_name} WHERE id={input_id} RETURNING image """
    cursor.execute(delete_query)
    # delete_image(cursor.fetchone())


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


@connection_handler
def get_question_titles_and_messages(cursor, search_phrase):
    query = f"""SELECT question.title, question.message as "Question message",  answer.message as "Answer message"
                FROM answer, question 
                WHERE title LIKE '%{search_phrase}%' AND answer.question_id = question.id ; """
    cursor.execute(query)
    return cursor.fetchall()
