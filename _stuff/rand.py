""" Some utils to generate random numbers from distributions
by qwiglydee@gmail.com

Generic usage:
    rnd_distrib = Something(params)
    rnd_value = rnd_distrib.sample()

The distributions are compatible with Constants and can be passed as vars or jsvars
"""

from collections import namedtuple
import random


class Bernoulli(namedtuple('Bernoulli', ['p'])):
    """Bernoulli distribution defined by probability (float)"""

    def sample(self) -> bool:
        return random.random() <= self.p


class BernoulliF(namedtuple('BernoulliF', ['nom', 'den'])):
    """Bernoulli distribution defined by rational"""

    def sample(self) -> bool:
        return random.randint(1, self.den) <= self.nom


class Uniform(namedtuple('Uniform', ['min', 'max'])):
    """Uniform distribution defined by range on floats or ints"""

    def sample(self) -> int | float:
        if isinstance(self.min, int) and isinstance(self.max, int):
            return random.randint(self.min, self.max)
        else:
            return random.uniform(self.min, self.max)


class Normal(namedtuple('Normal', ['mean', 'std'])):
    """Normal distribution on integers or floats"""

    def sample(self) -> int | float:
        val = random.gauss(self.mean, self.std)
        if isinstance(self.mean, int):
            return round(val)
        else:
            return val


class Discrete(namedtuple('Discrete', ['outcomes', 'weights'])):
    """Discrete distribution defined by outcomes and weights"""

    def __new__(cls, *args):
        return super().__new__(cls, tuple(a[0] for a in args), tuple(a[1] for a in args))

    def __repr__(self):
        args = tuple(zip(self.outcomes, self.weights))
        return f"Discrete{args}"

    def sample(self):
        val, = random.choices(self.outcomes, self.weights, k=1)
        return val


class Outcomes(namedtuple('Outcomes', ['outcomes', 'weights'])):
    """Discrete distribution defined as dict of key=weight"""

    def __new__(cls, **kwargs):
        return super().__new__(cls, tuple(kwargs.keys()), tuple(kwargs.values()))

    def __repr__(self):
        args = ", ".join(f"{k}={v}" for k, v in zip(self.outcomes, self.weights))
        return f"Outcomes({args})"

    def sample(self):
        val, = random.choices(self.outcomes, self.weights, k=1)
        return val


class Choices(namedtuple('Choices', ['outcomes'])):
    """Discrete distribution with equal weights"""

    def __new__(cls, *args):
        return super().__new__(cls, args)

    def __repr__(self):
        return f"Choices{self.outcomes}"

    def sample(self):
        return random.choice(self.outcomes)


class Const(namedtuple('Const', ['value'])):
    def sample(self):
        return self.value
