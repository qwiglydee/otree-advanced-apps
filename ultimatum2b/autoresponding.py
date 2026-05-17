import random
from asyncio import sleep

from .conf import C
from .models import Trial, Response


async def autorespond_proposal(trial: Trial, response: Response):
    # simulate thinking or a remote call
    await sleep(0.5 + random.random())

    response.p_proposal = random_proposal(trial.endowment)


async def autorespond_decision(trial: Trial, response: Response):
    # simulate thinking or a remote call
    await sleep(0.5 + random.random())

    response.r_decision = random_decision()


def random_proposal(endowment: float):
    proposal = random.gauss(0.5, 0.2) * endowment
    proposal = min(endowment, max(0, proposal))
    return proposal


def random_decision():
    return random.choice(C.DECISIONS)
