import csv

QUESTION_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWER_HEADERS = ["id", "submission_time", "vote_number", "question_id", "message", "image"]


def get_all_csv_data(path='sample_data/question.csv'):
    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = []
        for row in csv_reader:
            data.append(row)
        return data


def write_all_data_to_csv(path, all_data, type):
    HEADER = ""
    if type.upper() == "ANSWERS":
        HEADER = ANSWER_HEADERS
    elif type.upper() == "QUESTIONS":
        HEADER = QUESTION_HEADERS
    with open(path, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=HEADER)
        csv_writer.writeheader()
        for question_index in range(len(all_data)):
            csv_writer.writerow(all_data[question_index])