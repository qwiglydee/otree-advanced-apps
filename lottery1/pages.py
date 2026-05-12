from otree.views import Page

from _stuff.live import live_page
from _stuff.layout import arrange

from .conf import C
from .models import Player, Response
from .progress import Progress
from . import progress


class LiveMethods:
    @classmethod
    def live_continue(page, player: Player, _):
        current = progress.current(player)

        # restore trial on page reloading
        if current.is_running:
            yield "progress", page.display_progress(current)
            yield "trial", page.display_trial(current)
            return

        current = progress.advance(current)

        yield "progress", page.display_progress(current)
        if current.is_running:
            yield "trial", page.display_trial(current)

    @classmethod
    def live_response(page, player: Player, data: dict):
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"

        assert 'button' in data
        button = int(data['button'])
        choice = current.trial.layout[button]
        response = progress.respond(current, choice, response_time=data['time'], button=button)

        yield "progress", page.display_progress(current)
        yield "feedback", page.display_feedback(current, response)
        if current.trial.is_completed:
            yield "result", page.display_result(current)

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "total": C.NUM_TRIALS[current.pagename],
            "finished": current.iteround.is_completed,
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
            "current": current.trial.iteration if current.trial else None,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "labels": arrange(current.trial.layout, current.trial.labels),
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        return {
            "final": current.trial.is_completed,
            "outcomes": arrange(current.trial.layout, response.outcomes),
        }

    @staticmethod
    def display_result(current: Progress):
        return {
            "score": current.trial.score,
        }


@live_page
class Practice(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css', 'cards.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]


@live_page
class Main(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css', 'cards.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]


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
