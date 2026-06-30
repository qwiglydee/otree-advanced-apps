from decimal import Decimal
from otree.api import Page, WaitPage

from _extras.livepage import LivePage, LivePayload, LiveResponding
from units import Coins

from .conf import C
from .models import Player, Trial, Response, evaluate, setup_group
from .progress import Progress


def get_template_rolename(page: Page):
    # different page templates by players role: `Pagename_ROLE.html`
    pagename = page.__class__.__name__
    role: str = page.player.role  # type: ignore
    return f"{__package__}/{pagename}_{role}.html"


class Gather(WaitPage):
    template_name = "_extras/WaitPage.html"
    group_by_arrival_time = True
    after_all_players_arrive = setup_group


class Main(LivePage):
    get_template_name = get_template_rolename
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        group = player.group
        current = Progress.current(page, player)

        # restore state on occasional page reload
        if current.trial is not None:
            yield player, "progress", page.output_progress(current)
            if current.trial.has_started:
                yield player, "trial", page.output_trial(current.trial)
            responded = Response.last(current.trial, player=player)
            if responded:
                yield player, "feedback", page.output_feedback(current.trial, responded)
            return

        advanced = Progress.advance(current)

        if advanced.trial and advanced.trial.has_started:
            yield group, "progress", page.output_progress(advanced)
            yield group, "trial", page.output_trial(advanced.trial)
        else:
            # just indicate status of gameover or something
            yield player, "progress", page.output_progress(advanced)

    @classmethod
    def live_proposal(page, player: Player, trialid: int, proposal: str, time: int) -> LiveResponding:
        group = player.group
        current = Progress.current(page, player)
        assert current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        response = Progress.respond(current, "PROPOSING", proposal=Coins(proposal), response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield player, "feedback", page.output_feedback(current.trial, response)

    @classmethod
    def live_decision(page, player: Player, trialid: int, decision: str, time: int) -> LiveResponding:
        group = player.group
        current = Progress.current(page, player)
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"
        assert decision in C.DECISIONS

        response = Progress.respond(current, "RESPONDING", decision=decision, response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield player, "feedback", page.output_feedback(current.trial, response)
        yield group, "result", page.output_result(current.trial)

    @classmethod
    def live_timeout(page, player: Player) -> LiveResponding:
        group = player.group
        current = Progress.current(page, player)

        Progress.timeout(current)

        yield group, "progress", {"terminated": True}

    @classmethod
    def output_progress(page, progress: Progress) -> LivePayload:
        player, iteround, trial = progress
        return {
            "total": C.NUM_TRIALS,
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "current": trial.iteration if trial and trial.has_started else None,
            "turn": progress.turn,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "endowment": str(trial.endowment),
            "proposal": f"{trial.proposal}" if trial.proposal is not None else None,
            "response": trial.response,
        }

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        return {
            "continue": not trial.is_closed,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return page.output_shares(trial.get_scores())

    @classmethod
    def live_evaluate(page, player: Player, proposal: int, decision: bool) -> LiveResponding:
        """Online payoff calculator (with proper score fomatting)"""
        current = Progress.current(page, player)
        assert current.trial is not None
        shares = evaluate(current.trial.endowment, Decimal(proposal), decision)
        yield player, "evaluation", page.output_shares(shares)

    @classmethod
    def output_shares(page, shares: dict[str, Decimal]) -> LivePayload:
        # explicitely convert to coins
        return {k: str(Coins(v)) for k, v in shares.items()}


class Intro(Page):
    pass


class Instructions(Page):
    get_template_name = get_template_rolename


class Results(Page):
    pass


class Dropout(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.status == "dropout"


page_sequence = [
    Gather,
    Main,
    Dropout,
    Results,
]
