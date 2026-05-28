from otree.api import Page

from _extras.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Player, Response, Trial
from .progress import Progress


class TrialsPage(LivePage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @classmethod
    def live_load(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        if current.trial is None:
            yield from page.live_iterate(player)
        else:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)
        current = progress.advance(current)

        if current.trial is None:
            # no more trials
            yield "progress", page.output_progress(current)
        else:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)

    @classmethod
    def live_response(page, player: Player, trialid: int, time: int, value: str) -> LiveResponding:
        current = progress.current(page, player)
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        response = progress.respond(current, value, response_time=time)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, progr: Progress) -> LivePayload:
        pagename, player, iteround, trial = progr
        assert iteround is not None
        return {
            "total": C.NUM_TRIALS,
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": f"{iteround.total_score:n}",
            "current": trial.iteration if trial else None,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "task": trial.task,
        }

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        return {
            "final": trial.is_completed,
            "outcome": response.outcome,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+}" if trial.score is not None else None,
            "outcome": trial.outcome,
        }


class Intro(Page):
    pass


class Main(TrialsPage):
    pass


class Results(Page):
    pass


page_sequence = [
    Intro,
    Main,
    Results,
]
