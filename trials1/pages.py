from otree.api import Page

from _stuff.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Player, Response, Trial
from .progress import Progress


class TrialsPage(LivePage):
    page_styles = ["ot-progress.css", "ot-pulse.css"]
    page_scripts = ["ot-progress.js", "ot-pulse.js"]

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
    def live_response(page, player: Player, trialid: int, answer: str, time: int) -> LiveResponding:
        current = progress.current(page, player)
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        response = progress.respond(current, answer, response_time=time)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, progr: Progress) -> LivePayload:
        pagename, player, iteround, trial = progr
        assert iteround is not None
        return {
            "total": C.NUM_TRIALS[pagename],
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": f"{iteround.total_score:g}",
            "current": trial.iteration if trial else None,
            "retries": progr.retries_left if trial else None,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "task": trial.task,
        }

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload: ...

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload: ...


class Practice(TrialsPage):
    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        return {
            "final": trial.is_completed,
            "correct": response.correct,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+n}" if trial.score is not None else None,
            "truth": trial.truth,
        }


class Main(TrialsPage):
    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        return {
            "final": trial.is_completed,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+n}" if trial.score is not None else None,
        }


class Intro(Page):
    pass


class Results(Page):
    pass


page_sequence = [
    Intro,
    Practice,
    Main,
    Results,
]
