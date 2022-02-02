import flask
import data_manager


def set_order_direction(order_direct, new_list_of_questions):
    if order_direct == "ascending":
        questions_set = new_list_of_questions[::-1]
    else:
        questions_set = new_list_of_questions
    return questions_set


def remove_none_value(checked_value, check_type):
    if checked_value == None:
        new_checked_value = check_type
    else:
        new_checked_value = checked_value
    return new_checked_value


def sort_main():
    all_questions = data_manager.get_all_data('questions')
    questions_order_val = flask.request.args.get("questions_order")
    order_direction_val = flask.request.args.get("order_direction")

    questions_order_val = remove_none_value(questions_order_val, "submission_time")
    order_direction_val = remove_none_value(order_direction_val, "descending")
    new_questions_list = all_questions

    if flask.request.method == "GET":

        if questions_order_val != "submission_time" or order_direction_val != "descending":
            questions_order_val = flask.request.args.get("questions_order")
            order_direction_val = flask.request.args.get("order_direction")
            print(questions_order_val)

        all_questions_copy = all_questions[:]
        new_questions_list = []

        QUESTION_HEADERS = ["submission_time", "view_number", "vote_number", "title", "message"]
        for order_type in QUESTION_HEADERS:
            if questions_order_val == order_type:

                while len(new_questions_list) != len(all_questions):
                    first_value = all_questions_copy[0]
                    for compared_question in all_questions_copy:

                        compared_order = compared_question[order_type]
                        if compared_order.isdigit():
                            if int(first_value[order_type]) < int(compared_question[order_type]):
                                first_value = compared_question
                        else:
                            if first_value[order_type] < compared_question[order_type]:
                                first_value = compared_question
                    new_questions_list.append(first_value)

                    for question in all_questions_copy:
                        if question["id"] == first_value["id"]:
                            all_questions_copy.remove(question)
                # break
        new_questions_list = set_order_direction(order_direction_val, new_questions_list)

        return new_questions_list, questions_order_val, order_direction_val