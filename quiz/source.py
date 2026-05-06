import random
from pathlib import Path

from otree.database import ExtraModel
from otree import database
from otree.read_csv import read_csv

DIR = Path(__file__).parent


class DataRow(ExtraModel):
    taskid = database.StringField()
    category = database.StringField()
    question = database.StringField()
    answer = database.StringField()
    option_1 = database.StringField()
    option_2 = database.StringField()
    option_3 = database.StringField()


def load_source(filename: str) -> list[dict]:
    return read_csv(DIR / filename, DataRow)


def filter_data(data: list[dict], **filters) -> list[dict]:
    def matching(rec):
        return all(rec[key] == val for key, val in filters.items())
    return list(filter(matching, data))


def sample_data(data: list[dict], count, **filters) -> list[dict]:
    return random.sample(filter_data(data, **filters), k=count)
