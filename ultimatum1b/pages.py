from otree.api import Page

from _stuff.livepage import LivePage, LivePayload, LiveResponding
from units import Points

from . import progress
from .conf import C
from .models import Player, Trial
from .progress import Progress


def get_template_rolename(page: Page):
    # different page templates by players role: `Pagename_ROLE.html`
    pagename = page.__class__.__name__
    role: str = page.player.role  # type: ignore
    return f"{__package__}/{pagename}_{role}.html"


class Main(LivePage):
    get_template_name = get_template_rolename
    page_styles = ["ot-progress.css", "ot-pulse.css"]  # noqa
    page_scripts = ["ot-progress.js", "ot-pulse.js", "format.js"]  # noqa

    @classmethod
    async def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        if current.trial is not None:
            # page reloaded during a trial
            yield "progress", page.output_progress(current)
            if current.trial.is_running:
                # restore
                yield "trial", page.output_trial(current.trial)
        else:
            # go first/next round/trial
            advanced = progress.advance(current)

            if advanced.trial is None:
                # no more trials
                yield "progress", page.output_progress(advanced)
            else:
                yield "progress", page.output_progress(advanced)
                yield "trial", page.output_trial(advanced.trial)

                # autorespond the very first turn
                async for r in page.autoresponding(advanced):
                    yield r

    @classmethod
    async def autoresponding(page, current: Progress):
        if current.trial is None or not current.autoresponding:
            return
        await progress.autorespond(current)
        yield "progress", page.output_progress(current)
        yield "update", page.output_trial(current.trial)

    @classmethod
    async def live_proposal(page, player: Player, *, id: int, proposal: str, time: int) -> LiveResponding:
        current = progress.current(page, player)
        assert current.trial is not None and current.trial.id == id, "mismatched response"

        progress.respond_proposal(current, Points(proposal), response_time=time)

        yield "progress", page.output_progress(current)
        yield "update", page.output_trial(current.trial)

        # autorespond next turn
        async for r in page.autoresponding(current):
            yield r

        yield "result", page.output_result(current.trial)

    @classmethod
    async def live_decision(page, player: Player, *, id: int, decision: str, time: int) -> LiveResponding:
        current = progress.current(page, player)
        assert current.trial is not None and current.trial.id == id, "mismatched response"

        assert decision in C.DECISIONS
        progress.respond_decision(current, decision, response_time=time)

        yield "progress", page.output_progress(current)
        yield "update", page.output_trial(current.trial)
        yield "result", page.output_result(current.trial)

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
            "endowment": trial.endowment,
            "proposal": trial.proposal,
            "decision": trial.decision,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {"scores": trial.scores}


class Intro(Page):
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


page_sequence = [
    Intro,
    Instructions,
    Main,
    Results,
]
