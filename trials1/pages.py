from otree.views import Page

from _stuff.live import live_page

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

        answer = str(data['answer'])
        response = progress.respond(current, answer, response_time=data['time'])

        yield "progress", page.display_progress(current)
        yield "feedback", page.display_feedback(current, response)


@live_page
class Practice(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "finished": current.iteround.is_closed,
            "total": progress.max_trials(current.iteround),
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
            "current": current.trial.iteration if current.trial else None,
            "retries": current.retries_left if current.trial else None,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "task": current.trial.task,
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert current.trial and response
        return {
            "completed": current.trial.is_closed,
            "correct": response.correct,
            "score": current.trial.score if current.trial.is_completed else None,
            "truth": current.trial.truth if current.trial.is_completed else None,
        }


@live_page
class Main(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "finished": current.iteround.is_completed,
            "total": progress.max_trials(current.iteround),
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
            "current": current.trial.iteration if current.trial else None,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "task": current.trial.task,
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert response
        return {
            "completed": current.trial.is_completed,
            "score": current.trial.score if current.trial.is_completed else None,
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
