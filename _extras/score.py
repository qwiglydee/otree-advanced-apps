from decimal import Decimal, ROUND_HALF_UP

from otree.api import DecimalUnit
from otree.currency import RealWorldCurrency
from otree.i18n import convert_decimal_separator


class ScoreUnit(DecimalUnit, Decimal):
    """Unit class with extended formatting (with/without units, with/without sign)
    given that cls.output() returns `{formatted} units`:

    - f"{value}" => "xx.xx units"
    - f"{value:+}" => "+xx.xx units"
    - f"{value:n}" => "xx.xx"
    - f"{value:+n}" => "+xx.xx"
    """

    output_max_places: int

    @staticmethod
    def output(formatted: str, raw: Decimal):
        return formatted

    def __requantize(self, postdigits: int):
        assert postdigits >= 0
        qstr = "1." + ("0" * postdigits) if postdigits > 0 else "1"
        return self.quantize(Decimal(qstr), rounding=ROUND_HALF_UP)

    def __format__(self, fmt: str):
        q = self.__requantize(self.output_max_places)
        sgn = "+" if fmt.startswith("+") and self > 0 else ""
        formatted = sgn + convert_decimal_separator(str(q))
        if fmt == "" or fmt == "+":
            return self.output(formatted, self)
        elif fmt == "n" or fmt == "+n":
            return formatted
        else:
            return super().__format__(fmt)

    def _format_for_display(self):
        return self.__format__("")


def score_to_currency(score: Decimal, session):
    """Converting points to real world currency
    using session parameter `real_world_currency_per_point`
    casting to configured CURRENCY_UNIT
    """
    rate = Decimal(session.config["real_world_currency_per_point"])
    return RealWorldCurrency(score * rate)
