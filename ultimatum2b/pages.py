from decimal import Decimal
from otree.api import Page, WaitPage

from _stuff.livepage import LivePage, LivePayload, AsyncLiveResponding, LiveResponding
from units import Coins

from . import progress
from .conf import C
from .models import Player, Trial, evaluate, setup_group
from .progress import Progress


def get_template_rolename(page: Page):
    # different page templates by players role: `Pagename_ROLE.html`
    pagename = page.__class__.__name__
    role: str = page.player.role  # type: ignore
    return f"{__package__}/{pagename}_{role}.html"


class Gather(WaitPage):
    template_name = "WaitPage.html"
    group_by_arrival_time = True
    after_all_players_arrive = setup_group


class Main(LivePage):
    get_template_name = get_template_rolename
    page_styles = ["ot-progress.css", "ot-pulse.css"]
    page_scripts = ["ot-progress.js", "ot-pulse.js"]

    @classmethod
    async def live_load(page, player: Player) -> AsyncLiveResponding:
        current = progress.current(page, player)

        if current.trial is None:
            async for r in page.live_iterate(player):
                yield r
        else:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)

    @classmethod
    async def live_iterate(page, player: Player) -> AsyncLiveResponding:
        current = progress.current(page, player)
        current = progress.advance(current)
        group = current.group
        assert current.iteround

        if current.trial is None:
            # no more trials
            yield group, "progress", page.output_progress(current)
        elif not current.trial.is_running:
            # pending state
            yield player, "progress", page.output_progress(current)
        else:
            yield group, "progress", page.output_progress(current)
            yield group, "trial", page.output_trial(current.trial)

            if current.iteround.autorespond_role == "P":
                async for r in page.auto_proposal(current):
                    yield r

    @classmethod
    async def live_proposal(page, player: Player, trialid: int, proposal: str, time: int) -> AsyncLiveResponding:
        current = progress.current(page, player)
        group = current.player.group
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        progress.respond_proposal(current, Coins(proposal), response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)

        if current.iteround.autorespond_role == "R":
            async for r in page.auto_decision(current):
                yield r

    @classmethod
    async def auto_proposal(page, current: Progress) -> AsyncLiveResponding:
        assert current.trial is not None

        await progress.autorespond_proposal(current)

        yield "progress", page.output_progress(current)
        yield "update", page.output_trial(current.trial)

    @classmethod
    async def live_decision(page, player: Player, trialid: int, decision: str, time: int) -> AsyncLiveResponding:
        current = progress.current(page, player)
        group = current.player.group
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        assert decision in C.DECISIONS
        progress.respond_decision(current, decision, response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield group, "result", page.output_result(current.trial)

    @classmethod
    async def auto_decision(page, current: Progress) -> AsyncLiveResponding:
        assert current.trial is not None

        await progress.autorespond_decision(current)

        yield "progress", page.output_progress(current)
        yield "update", page.output_trial(current.trial)
        yield "result", page.output_result(current.trial)

    @classmethod
    async def live_timeout(page, player: Player, trialid: int) -> AsyncLiveResponding:
        current = progress.current(page, player)
        assert current.iteround is not None and current.trial is not None
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        progress.timeout(current)

        [other] = player.get_others_in_group()
        yield other, "progress", {"terminated": True}  # closes the page if still open

        if current.iteround.autorespond_role == "P":
            async for r in page.auto_proposal(current):
                yield r

        if current.iteround.autorespond_role == "R":
            async for r in page.auto_decision(current):
                yield r

    @classmethod
    def output_progress(page, progr: Progress) -> LivePayload:
        pagename, player, iteround, trial = progr
        assert iteround is not None
        return {
            "total": C.NUM_TRIALS,
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "pending": not progr.is_running,
            "current": trial.iteration if trial else None,
            "turn": progr.turn if progr.is_running else None,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "endowment": str(trial.endowment),
            "proposal": str(trial.proposal) if trial.proposal is not None else None,
            "decision": trial.decision,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        scores = trial.scores
        return page.output_shares(scores)

    @classmethod
    def live_evaluate(page, player: Player, proposal: int, decision: bool) -> LiveResponding:
        """Online payoff calculator (with proper score fomatting)"""
        current = progress.current(page, player)
        assert current.trial is not None
        shares = evaluate(current.trial.endowment, Decimal(proposal), decision)
        yield player, "evaluation", page.output_shares(shares)

    @classmethod
    def output_shares(page, shares: dict[str, Decimal]) -> LivePayload:
        """Format scores according to the unit config"""
        return {k: str(Coins(v)) for k, v in shares.items()}


class Intro(Page):
    form_model = "player"
    form_fields = ["age", "gender"]

    @staticmethod
    def vars_for_template(player: Player):
        return {"endowment": C.ENDOWMENT[player.condition]}


class Instructions(Page):
    get_template_name = get_template_rolename

    @staticmethod
    def vars_for_template(player: Player):
        return {"endowment": C.ENDOWMENT[player.condition]}


class Results(Page):
    pass


class Dropout(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.status == "dropout"


page_sequence = [
    Gather,
    Intro,
    Instructions,
    Main,
    Dropout,
    Results,
]
