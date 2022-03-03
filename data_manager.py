from datetime import datetime

import connection
import time
import os
import flask
import datetime
from sql_connection import connection_handler
import bcrypt

from psycopg2.sql import SQL, Literal, Identifier

# image path
UPLOAD_FOLDER = 'static/images/'

# data path
PATH_ANSWERS = "sample_data/answer.csv"
PATH_QUESTIONS = "sample_data/question.csv"

MIN_QUESTION_TITLE_LEN = 3
MIN_QUESTION_MESSAGE_LEN = 5


@connection_handler
def update_table_single_col(cursor, table_name, col_name, id_number, vote_up):
    # query = f""" UPDATE {table_name} SET {col_name}={col_name}+{vote_up} WHERE id={id_number} """
    query = SQL('UPDATE {} SET {}={}+{} WHERE id={}')\
        .format(Identifier(table_name), Identifier(col_name), Identifier(col_name), Literal(vote_up), Literal(id_number) )
    cursor.execute(query)


@connection_handler
def add_new_answer(cursor, id_input, input_text, image_file, user_name):
    user_id = search_user_id(user_name)
    current_time: datetime = datetime.datetime.now()
    # query = f""" INSERT INTO answer (submission_time, vote_number, question_id, message, user_id)
    #             VALUES ('{current_time}', 0, '{id_input}', '{input_text}', {user_id}) """
    query = SQL('INSERT INTO answer (submission_time, vote_number, question_id, message, user_id) VALUES ({}, {}, {}, {}, {})')\
        .format(Literal(current_time), Literal(0), Literal(id_input), Literal(input_text), Literal(user_id))
    cursor.execute(query)
    select_query = f""" SELECT id FROM answer ORDER BY id DESC LIMIT 1 """
    cursor.execute(select_query)

    image_index = cursor.fetchone().get('id')
    image_path = upload_image(f"A_{image_index}", image_file)
    # new_answer_query = f""" UPDATE answer SET image='{image_path}' WHERE id='{image_index}' """
    new_answer_query = SQL(' UPDATE answer SET image={} WHERE id={} ').format(Literal(image_path), Literal(image_index))
    cursor.execute(new_answer_query)
    return True


@connection_handler
def get_all_data(cursor, table_name, order_type='submission_time', order_direction='DESC'):
    # query = f""" SELECT * FROM "{table_name}" ORDER BY {order_type} {order_direction} """
    query = SQL(' SELECT * FROM {} ORDER BY {} DESC ').format(Identifier(table_name), Identifier(order_type)) #, Literal(order_direction))
    cursor.execute(query)
    table_data = cursor.fetchall()
    return table_data


@connection_handler
def get_all_data_by_condition(cursor, table_name, column, col_value, order_type="submission_time", order_direction="ASC"):
    # query = f""" SELECT * FROM "{table_name}" WHERE {column}>={col_value} ORDER BY {order_type} {order_direction} """
    query = SQL(' SELECT * FROM {} WHERE {}>={} ORDER BY {} ASC ')\
        .format(Identifier(table_name), Identifier(column), Literal(col_value), Identifier(order_type)) #, Literal(order_direction))
    cursor.execute(query)
    table_data = cursor.fetchall()
    return table_data


@connection_handler
def question_opener(cursor, question_id):
    # question_query = f""" SELECT * FROM question WHERE id='{question_id}' """
    question_query = SQL(' SELECT * FROM question WHERE id={} ').format(Literal(question_id))
    cursor.execute(question_query)
    question_data = cursor.fetchone()

    # answer_query = f""" SELECT * FROM answer WHERE question_id = '{question_id}' """
    answer_query = SQL(' SELECT * FROM answer WHERE question_id={} ').format(Literal(question_id))
    cursor.execute(answer_query)
    answers = cursor.fetchall()

    return question_data, answers


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
def add_new_question(cursor, new_title, new_message, image_file, user_name):
    if is_new_question_valid(new_title, new_message):
        user_id = search_user_id(user_name)
        current_time = datetime.datetime.now()
        # insert_new_question = f""" INSERT INTO question (submission_time, view_number, vote_number, title, message, user_id)
        #                            VALUES ('{current_time}', 0, 0, '{new_title}', '{new_message}', {user_id}) """
        values = [current_time, 0, 0, new_title, new_message, user_id]
        insert_new_question =SQL(' INSERT INTO question (submission_time, view_number, vote_number, title, message, user_id) '
                                 'VALUES  {inserted_values}').format( inserted_values=SQL(', ').join([Identifier(value) for value in values]) )
        cursor.execute(insert_new_question)
        select_query = f""" SELECT id FROM question ORDER BY id DESC LIMIT 1 """
        cursor.execute(select_query)

        image_index = cursor.fetchone().get('id')
        image_path = upload_image(f"Q_{image_index}", image_file)
        # new_answer_query = f""" UPDATE question SET image='{image_path}' WHERE id='{image_index}' """
        new_answer_query = SQL(' UPDATE question SET image={} WHERE id={} ').format(Literal(image_path), Literal(image_index))
        cursor.execute(new_answer_query)
        return True


def delete_images(image_paths=[]):
    for image_path in image_paths:
        if image_path.get("image"):
            correct_path = f"static/{image_path.get('image')}"
            if os.path.exists(correct_path):
                os.remove(correct_path)


@connection_handler
def delete(cursor, question_id=None, answer_id=None):
    if question_id:
        # delete_query = f""" DELETE FROM answer WHERE question_id={question_id} RETURNING image"""
        delete_query = SQL(' DELETE FROM answer WHERE question_id=%s RETURNING image ')
        cursor.execute(delete_query, [question_id])
        images_for_delete = cursor.fetchall()
        # delete_query = f""" DELETE FROM question WHERE id={question_id} RETURNING image """
        delete_query = SQL(' DELETE FROM question WHERE id=%s RETURNING image ')
        cursor.execute(delete_query, [question_id])
        images_for_delete.extend(cursor.fetchall())
    elif answer_id:
        # delete_query = f""" DELETE FROM answer WHERE id={answer_id} RETURNING image"""
        delete_query = SQL(' DELETE FROM answer WHERE id=%s RETURNING image ')
        cursor.execute(delete_query, [question_id])
        images_for_delete= cursor.fetchall()
    delete_images(images_for_delete)


def upload_image(img_name, image_request):
    if image_request.filename == "":
        return None
    name_ext = image_request.filename.split('.')
    extension = name_ext[1]
    img_name = f'{img_name}.{extension}'
    image_request.save(os.path.join(UPLOAD_FOLDER, img_name))
    splitted_path = UPLOAD_FOLDER.split('/')
    return f'{splitted_path[1]}/{img_name}'


@connection_handler
def get_entry_by_id(cursor, entry_id, table_name, entry_post=0, message="", image_file=""):
    # query = f"""SELECT * FROM {table_name} WHERE id={entry_id}"""
    query = SQL(' SELECT * FROM {} WHERE id={} ').format(Identifier(table_name), Literal(entry_id))
    cursor.execute(query)
    return cursor.fetchone()


@connection_handler
def entry_editor(cursor, table_name, data_id, message):
    # query = f""" UPDATE {table_name} SET message='{message}' WHERE id={data_id}
    # """
    query = SQL(' UPDATE {} SET message={} WHERE id={} ').format(Identifier(table_name), Literal(message), Literal(data_id))
    cursor.execute(query)


@connection_handler
def question_editor(cursor, title, message, question_id):
    # query = f""" UPDATE question SET title='{title}', message='{message}' WHERE id={question_id}
    #     """
    query = SQL(' UPDATE question SET title={}, message={} WHERE id={} ').format(Literal(title), Literal(message), Literal(question_id))
    cursor.execute(query)


@connection_handler
def get_question_titles_and_messages(cursor, search_phrase):
    # query = f"""SELECT  id ,title, message
    #             FROM question
    #             WHERE title LIKE '%{search_phrase}%'; """
    joined_search_phrase = '%' + search_phrase + '%'
    query = SQL(' SELECT  id ,title, message FROM question WHERE title LIKE {} ')\
        .format( Literal(joined_search_phrase) )
    cursor.execute(query)
    return cursor.fetchall()


@connection_handler
def get_answers_by_id(cursor, id):
    query = SQL(' SELECT message FROM answer WHERE  question_id = {} ').format(Literal(id))
    cursor.execute(query)
    result = []
    for x in (cursor.fetchall()):
        result.append(x['message'])
    return result


@connection_handler
def image_editor(cursor, table_name, data_id, image):
    query = SQL(' UPDATE {} SET image ={} WHERE id={} ').format(Identifier(table_name), Literal(image), Literal(data_id))
    cursor.execute(query)


@connection_handler
def add_new_tag(cursor, new_tag):
    query = SQL(' INSERT INTO tag(name) SELECT {} WHERE NOT EXISTs (SELECT name FROM tag WHERE name={}) ')\
        .format(Identifier(new_tag), Identifier(new_tag))
    cursor.execute(query)
    query = SQL(' SELECT id FROM tag WHERE name={} ').format(Identifier(new_tag))
    cursor.execute(query)
    return cursor.fetchone().get("id")


@connection_handler
def add_tag_to_question(cursor, added_tag_id, question_id):
    query = SQL(' INSERT INTO question_tag(question_id,tag_id) VALUES({inserted_values}) ')\
        .format( inserted_values=SQL(', ').join( [Literal(question_id), Literal(added_tag_id)] ) )
    cursor.execute(query)


## refactor this to one function
@connection_handler
def add_new_comment_q(cursor, question_id, added_message, user_name):
    user_id = search_user_id(user_name)
    submission_time = datetime.datetime.now()
    values = [question_id, added_message, submission_time, 0, user_id]
    comment_query = SQL(' INSERT INTO comment (question_id, message, submission_time, edited_count, user_id) VALUES ({inserted_values}) ')\
        .format( inserted_values=SQL(', ').join([Literal(value) for value in values]) )
    cursor.execute(comment_query)


@connection_handler
def add_new_comment_a(cursor, answer_id, added_message, user_name):
    user_id = search_user_id(user_name)
    submission_time = datetime.datetime.now()
    a_values = [answer_id, added_message, submission_time, 0, user_id]
    comment_query = SQL(' INSERT INTO comment (answer_id, message, submission_time, edited_count, user_id) VALUES ({inserted_values}) ')\
        .format( inserted_values=SQL(', ').join([Literal(value) for value in a_values]) )
    cursor.execute(comment_query)
## refactor this to one function


@connection_handler
def delete_comment(cursor, table_name, column_type, column_value):
    delete_comment_query =  SQL(' DELETE FROM {} WHERE {}={} ')\
        .format(Identifier(table_name), Identifier(column_type), Literal(column_value))
    cursor.execute(delete_comment_query)


@connection_handler
def latest_questions(cursor):
    query = f""" SELECT * FROM question ORDER BY submission_time DESC  LIMIT 5"""
    cursor.execute(query)
    table_data = cursor.fetchall()
    return table_data


@connection_handler
def get_user_password(cursor, email):
    query = SQL(' SELECT user_password FROM users WHERE user_name = {} ').format(Literal(email))
    cursor.execute(query)
    table_data = cursor.fetchone()
    return table_data


def validate_login(input_password, valid_password):
    hashed_password = valid_password.encode('UTF-8')
    hashed_input = input_password.encode('UTF-8')
    return bcrypt.checkpw(hashed_input, hashed_password)


@connection_handler
def add_new_user(cursor, name, password):
    hashed_password = convert_to_hash(password)
    values = [name, hashed_password, datetime.datetime.now()]
    query = SQL(' INSERT INTO users (user_name, user_password, registration_date) VALUES ({}) ').format( inserted_values=SQL(', ').join([Literal(value) for value in values]))
    cursor.execute(query)


def convert_to_hash(input_string):
    hashed_bytes = bcrypt.hashpw(input_string.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


@connection_handler
def search_user_id(cursor, user_name):
    # query = f"""SELECT * FROM users
    #             Where user_name = '{user_name}'
    #     """
    query = SQL(' SELECT * FROM users WHERE user_name={} ').format(Literal(user_name))
    cursor.execute(query)
    user_id = cursor.fetchone().get('id')
    return user_id


@connection_handler
def search_user_data(cursor, user_name):
    query = SQL(' SELECT * FROM users WHERE user_name={} ').format(Literal(user_name))
    select_by = {'user_name':user_name}
    cursor.execute(query,select_by)
    user_data = cursor.fetchone()
    return user_data


@connection_handler
def get_user_blog_info(cursor, user_id):
    query = SQL(' SELECT  distinct user_name, '
                'a.message as answer, '
                'a.id as answer_id, '
                'q.message as question, '
                'c.message as comment, '
                'c.question_id, '
                'c.answer_id as comment_answer_id '
                'FROM users '
                'inner join answer a on users.id = a.user_id '
                'inner join comment c on users.id = c.user_id '
                'inner join question q on users.id = q.user_id '
                'WHERE users.id = {} ').format(Literal(user_id))
    select_by = {'user_id': user_id}
    cursor.execute(query,select_by)
    return cursor.fetchall()


@connection_handler
def get_answer_comment_by_id(cursor, id):
    query = SQL(' SELECT * FROM comment WHERE answer_id={} ').format(Literal(id))
    select_by = {'id': id}
    cursor.execute(query, select_by)
    return cursor.fetchone()


def change_answer_accept_to(cursor, answer_id, value):
    query = f"""UPDATE answer SET accepted='{value}' WHERE id = '{answer_id}'
    """
    cursor.execute(query)


@connection_handler
def reputation_editor(cursor, user_id, reputation_value):
    query = f""" UPDATE users SET reputation =reputation + {reputation_value} WHERE id={user_id} """
    cursor.execute(query)


@connection_handler
def search_table_user_id(cursor, data_id, table_name):
    query = f"""SELECT user_id FROM {table_name}
                Where id = {data_id}
        """
    cursor.execute(query)
    user_id = cursor.fetchone().get('user_id')
    return user_id

@connection_handler
def get_question_tag_by_id(cursor, question_id):
    query = f"""SELECT tag.name FROM question_tag  
    JOIN tag ON question_tag.tag_id = tag.id 
    WHERE question_id='{question_id}'
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection_handler
def get_all_tags(cursor):
    query = f"""SELECT tag.name, count(question_tag.tag_id) as questions FROM tag
    LEFT JOIN question_tag ON tag.id = question_tag.tag_id
    GROUP BY tag.name ORDER BY count(question_tag.tag_id) DESC
    """
    cursor.execute(query)
    return cursor.fetchall()
