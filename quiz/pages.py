from otree.api import Page

from _stuff.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Player, Response, Trial
from .progress import Progress


class TrialsPage(LivePage):
    page_styles = ["ot-progress.css", "ot-pulse.css"]
    page_scripts = ["ot-progress.js", "ot-pulse.js", "format.js"]

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
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

    @classmethod
    def live_response(page, player: Player, trialid: int, time: int, button: str) -> LiveResponding:
        current = progress.current(page, player)
        pagename, player, iteround, trial = current
        assert trial and trial.id == trialid, "mismatched response"

        answer = trial.options[button]
        response = progress.respond(current, answer, response_time=time, button=button)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(trial, response)
        if trial.is_completed:
            yield "result", page.output_result(trial)

    @classmethod
    def output_progress(page, progr: Progress) -> LivePayload:
        pagename, player, iteround, trial = progr
        assert iteround is not None
        return {
            "total": C.NUM_TRIALS[pagename],
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": iteround.total_score,
            "current": trial.iteration if trial else None,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "question": trial.question,
            "options": trial.options,
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
            "score": trial.score,
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
            "score": trial.score,
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
