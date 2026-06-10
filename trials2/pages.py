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
    def live_response(page, player: Player, trialid: int, button: int, time: int) -> LiveResponding:
        current = progress.current(page, player)
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        answer = current.trial.get_option(button)
        response = progress.respond(current, answer, response_time=time, button=button)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress) -> LivePayload:
        pagename, player, iteround, trial = current
        assert iteround is not None
        return {
            "total": C.NUM_TRIALS[iteround.pagename],
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
            "options": trial.get_options(),
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
            "score": f"{trial.score:+}" if trial.score is not None else None,
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
