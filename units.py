from decimal import Decimal
from otree.decimal import DecimalUnit
from otree.currency import RealWorldCurrency


class Points(DecimalUnit):
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


class EUR(DecimalUnit):
    storage_places = 3
    output_max_places = 2
    output_min_places = 2
    input_places = 2
    input_unit_label = "€"

    @staticmethod
    def output(formatted, raw):
        return f"€{formatted}"
