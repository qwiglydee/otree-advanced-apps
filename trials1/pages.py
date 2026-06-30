from otree.api import Page

from _extras.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Player, Response, Trial
from .progress import Progress


class TrialsPage(LivePage):
    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        if current.trial is not None:
            # page reloaded while running trial
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)
            return

        advanced = progress.advance(current)

        if advanced.trial is None:
            # no more trials
            yield "progress", page.output_progress(advanced)
        else:
            yield "progress", page.output_progress(advanced)
            yield "trial", page.output_trial(advanced.trial)

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
    def output_progress(page, current: Progress) -> LivePayload:
        pagename, player, iteround, trial = current
        assert iteround is not None
        return {
            "total": C.NUM_TRIALS[pagename],
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": f"{iteround.total_score:n}",
            "current": trial.iteration if trial else None,
            "retries": current.retries_left if trial and trial.is_running else None,
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
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        return {
            "final": trial.is_completed,
            "answer": response.answer,
            "correct": response.correct,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+}" if trial.score is not None else None,
            "truth": trial.truth if not trial.success else None,
        }


class Main(TrialsPage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        return {
            "final": trial.is_completed,
            "answer": response.answer,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+}" if trial.score is not None else None,
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
