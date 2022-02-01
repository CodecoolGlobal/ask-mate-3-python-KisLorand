import csv

DATA_HEADER = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]


def get_all_csv_data(path='sample_data/question.csv'):
    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=DATA_HEADER)
        data = []
        for row in csv_reader:
            data.append(row)
        return data


def write_all_data_to_csv(path, all_data):
    with open(path, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=DATA_HEADER)
        print(all_data)
        for question_index in range(1, len(all_data)):
            csv_writer.writerow(all_data[question_index])