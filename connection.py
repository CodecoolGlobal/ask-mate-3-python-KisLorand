import csv


def get_all_csv_data(path):
    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = []
        for row in csv_reader:
            data.append(row)
        return data
