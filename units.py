from otree.api import DecimalUnit

from _extras.score import ScoreUnit


class Points(ScoreUnit, DecimalUnit):
    storage_places = 4
    output_max_places = 2
    output_min_places = 2
    input_places = 2

    @staticmethod
    def output(formatted, raw):
        return f"{formatted} points"


class Coins(ScoreUnit, DecimalUnit):
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


class EUR(DecimalUnit):
    storage_places = 3
    output_max_places = 2
    output_min_places = 2
    input_places = 2
    input_unit_label = "€"

    @staticmethod
    def output(formatted, raw):
        return f"€{formatted}"
