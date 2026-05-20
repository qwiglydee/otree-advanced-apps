import random
from asyncio import sleep

from units import Coins
from .conf import C
from .models import Trial, Response


async def make_proposal(trial: Trial, response: Response):
    # simulate thinking or a remote call
    await sleep(0.5 + random.random())

    response.p_proposal = Coins(random_proposal(int(trial.endowment)))


async def make_decision(trial: Trial, response: Response):
    # simulate thinking or a remote call
    await sleep(0.5 + random.random())

    response.r_decision = random_decision()


def random_proposal(endowment: int):
    proposal = round(random.gauss(0.5, 0.2) * endowment)
    proposal = min(endowment, max(0, proposal))
    return proposal


def random_decision():
    return random.choice(C.DECISIONS)
