from decimal import Decimal

from otree.decimal import DecimalUnit


class ScoreUnit(DecimalUnit):
    """Unit class with extended formatting (with/without units, with/without sign)

    - f"{value}" => "xx.xx units"
    - f"{value:+}" => "+xx.xx units"
    - f"{value:n}" => "xx.xx"
    - f"{value:+n}" => "+xx.xx"
    """

    output_max_places: int

    def __format__(self, spec):
        if spec == "":
            return self._format_for_display()
        if spec == "+":
            sgn = "+" if not self.is_signed() and not self.is_zero() > 0 else ""
            return sgn + self._format_for_display()
        if spec in ("n", "+n"):
            _sign, digits, exp = self.as_tuple()
            assert exp not in ("n", "N", "F")
            prc = max(0, len(digits) + exp) + self.output_max_places
            return Decimal.__format__(self, f"{spec[:-1]}.{prc}n")
        return Decimal.__format__(self, spec)
