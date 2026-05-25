"""Some utils to generate random numbers from distributions
by qwiglydee@gmail.com

Generic usage:
    rnd_distrib = Something(params)
    rnd_value = rnd_distrib.sample()
    rnd_values = rnd_distrib.samples(5)

The distributions are compatible with Constants and can be passed as vars or jsvars
"""

from typing import Any
from dataclasses import dataclass
import random


@dataclass(slots=True)
class Bernoulli:
    """Bernoulli distribution defined by probability (float)"""

    p: float

    def sample(self) -> bool:
        return random.random() <= self.p

    def samples(self, n):
        return tuple(self.sample() for _ in range(n))


@dataclass(slots=True)
class BernoulliF:
    """Bernoulli distribution defined by rational"""

    nom: int
    den: int

    def sample(self) -> bool:
        return random.randint(1, self.den) <= self.nom

    def samples(self, n):
        return tuple(self.sample() for _ in range(n))


@dataclass(slots=True)
class Uniform:
    """Uniform distribution defined by range on floats or ints"""

    min: int | float
    max: int | float

    def sample(self) -> int | float:
        if isinstance(self.min, int) and isinstance(self.max, int):
            return random.randint(self.min, self.max)
        else:
            return random.uniform(self.min, self.max)

    def samples(self, n):
        return tuple(self.sample() for _ in range(n))


@dataclass(slots=True)
class Normal:
    """Normal distribution on integers or floats"""

    mean: int | float
    std: int | float

    def sample(self) -> int | float:
        val = random.gauss(self.mean, self.std)
        if isinstance(self.mean, int):
            return round(val)
        else:
            return val

    def samples(self, n):
        return tuple(self.sample() for _ in range(n))


@dataclass(slots=True)
class Discrete:
    """Discrete distribution defined by outcomes and weights"""

    outcomes: tuple
    weights: tuple

    def __init__(self, *args):
        self.outcomes = tuple(a[0] for a in args)
        self.weights = tuple(a[1] for a in args)

    def __repr__(self):
        args = tuple(zip(self.outcomes, self.weights))
        return f"Discrete{args}"

    def sample(self):
        return self.samples(1)[0]

    def samples(self, n):
        return tuple(self.sample() for _ in range(n))


def Outcomes(**kwargs):
    """Discrete distribution by kwargs notation (outcome=weight, ...)"""
    return Discrete(*kwargs.items())


@dataclass(slots=True)
class Choices:
    """Equally distributed choices"""

    outcomes: tuple

    def __init__(self, *args):
        self.outcomes = args

    def __repr__(self):
        return f"Choices{repr(self.outcomes)}"

    def sample(self):
        return random.choice(self.outcomes)

    def samples(self, n):
        return tuple(self.sample() for _ in range(n))


@dataclass(slots=True)
class Const:
    """Just a constant value
    added for interchangability with other distributions
    """

    value: Any

    def __init__(self, arg):
        self.value = arg

    def __repr__(self):
        return f"Const({self.value})"

    def sample(self):
        return self.value

    def samples(self, n):
        return tuple(self.value for _ in range(n))
