from otree.views import Page

from _stuff.livepage import LivePage
from _stuff.layout import arrange

from .conf import C
from .models import Player, Trial, Response
from .progress import Progress
from . import progress


class TrialsPage(LivePage):
    page_styles = ['ot-progress.css', 'ot-pulse.css', "cards.css"]
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @classmethod
    def live_continue(page, player: Player):
        current = progress.current(page, player)

        # restore trial on page reloading
        if current.is_running:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)
            return

        current = progress.advance(current)

        yield "progress", page.output_progress(current)
        if current.is_running:
            yield "trial", page.output_trial(current.trial)

    @classmethod
    def live_response(page, player: Player, *, id: int, button: str, time: int):
        current = progress.current(page, player)
        assert current.trial and current.trial.id == id, "mismatched response"

        button = button
        choice = current.trial.layout[button]
        response = progress.respond(current, choice, response_time=time, button=button)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress):
        pagename, player, iteround, trial = current
        return {
            "total": C.NUM_TRIALS[pagename],
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": iteround.total_score,
            "current": trial.iteration if trial else None,
        }

    @classmethod
    def output_trial(page, trial: Trial):
        return {
            "id": trial.id,
            "labels": arrange(trial.layout, trial.labels),
        }

    @classmethod
    def output_feedback(page, trial: Trial, response: Response):
        return {
            "final": trial.is_completed,
            "outcomes": arrange(trial.layout, response.outcomes),
        }

    @classmethod
    def output_result(page, trial: Trial):
        return {
            "score": trial.score,
        }


class Practice(TrialsPage):
    pass


class Main(TrialsPage):
    pass


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
