import random
from pathlib import Path

from otree.api import ExtraModel, models, read_csv

DIR = Path(__file__).parent


class DataRow(ExtraModel):
    taskid = models.StringField()
    category = models.StringField()
    question = models.StringField()
    answer = models.StringField()
    option_1 = models.StringField()
    option_2 = models.StringField()
    option_3 = models.StringField()


def load_source(filename: str) -> list[dict]:
    return read_csv(str(DIR / filename), DataRow)


def filter_data(data: list[dict], **filters) -> list[dict]:
    def matching(rec):
        return all(rec[key] == val for key, val in filters.items())

    return list(filter(matching, data))


def sample_data(data: list[dict], count, **filters) -> list[dict]:
    return random.sample(filter_data(data, **filters), k=count)
