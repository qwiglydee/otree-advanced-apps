from decimal import Decimal

from otree.decimal import DecimalUnit
from otree.currency import RealWorldCurrency

from _stuff.score import ScoreUnit


class Points(ScoreUnit):
    storage_places = 4
    output_max_places = 2
    output_min_places = 2
    input_places = 2

    @staticmethod
    def output(formatted, raw):
        return f"{formatted} points"

    def to_real_world_currency(self, session):
        rate = Decimal(session.config["real_world_currency_per_point"])
        return RealWorldCurrency(self * rate)  # converted to configured CURRENCY_UNIT


class Coins(ScoreUnit):
    storage_places = 0
    output_max_places = 0
    output_min_places = 0
    input_places = 0

    @staticmethod
    def output(formatted, raw):
        if raw == 0:
            return "no coins"
        elif raw == 1:
            return "a coin"
        else:
            return f"{formatted} coins"

    def to_real_world_currency(self, session):
        rate = Decimal(session.config["real_world_currency_per_point"])
        return RealWorldCurrency(self * rate)  # converted to configured CURRENCY_UNIT


class EUR(DecimalUnit):
    storage_places = 3
    output_max_places = 2
    output_min_places = 2
    input_places = 2
    input_unit_label = "€"

    @staticmethod
    def output(formatted, raw):
        return f"€{formatted}"
