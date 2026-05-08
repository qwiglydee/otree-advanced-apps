from otree.views import Page

from _stuff.live import live_page
from _stuff.config import get_session_param

from .const import C
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_trials, custom_export_responses  # noqa
from .progress import Progress
from . import progress


def creating_session(subsession: Subsession):
    session = subsession.session
    for group in subsession.get_groups():
        group.condition = get_session_param(session, 'condition', choices=C.CONDITIONS)


def set_payoff(player: Player):
    player.payoff = player.group.total_score


# PAGES

class LiveMethods:
    @classmethod
    def live_continue(page, player: Player, _):
        group = player.group
        current = progress.current(player)

        # restore trial on page reloading
        if current.is_running:
            yield player, "progress", page.display_progress(current)
            yield player, "trial", page.display_trial(current)
            return

        current = progress.advance(current)

        if current.is_running:
            # synchronize progress and trial
            yield group, "progress", page.display_progress(current)
            yield group, "trial", page.display_trial(current)
        else:
            # pending state
            yield player, "progress", page.display_progress(current)

    @classmethod
    def live_response(page, player: Player, message: dict):
        group = player.group
        current = progress.current(player)
        assert current.trial and current.trial.id == message['id'], "mismatched response"

        progress.respond(current, response_time=message['time'], answer=message['answer'])

        yield group, "progress", page.display_progress(current)
        for response in Response.allast(current.trial):
            yield response.player, "feedback", page.display_feedback(current, response)
        yield group, "update", page.display_trial(current)


@live_page
class Practice(LiveMethods, Page):
    page_styles = ['game-style.css', 'ot-progress.css', 'ot-pulse.css']
    page_scripts = ['otree-front-live.js', 'ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "finished": current.iteround.is_completed,
            "total": progress.max_trials(current.iteround),
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
            "pending": not current.is_running,
            "current": current.trial.iteration if current.trial else None,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        responses = Response.allast(current.trial)
        return {
            "id": current.trial.id,
            "task": current.trial.task,
            "answers": {r.player.role: r.answer for r in responses} if current.trial.is_completed else {},
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        return {
            "completed": current.trial.is_completed,
            "correct": response.correct if current.trial.is_completed else None,
            "score": current.trial.score if current.trial.is_completed else None,
            "truth": current.trial.truth if current.trial.is_completed else None,
        }


@live_page
class Main(LiveMethods, Page):
    page_styles = ['game-style.css', 'ot-progress.css', 'ot-pulse.css']
    page_scripts = ['otree-front-live.js', 'ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "finished": current.iteround.is_completed,
            "total": progress.max_trials(current.iteround),
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
            "pending": not current.is_running,
            "current": current.trial.iteration if current.trial else None,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        responses = Response.allast(current.trial)
        return {
            "id": current.trial.id,
            "task": current.trial.task,
            "answers": {r.player.role: r.answer for r in responses} if current.trial.is_completed else {},
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        return {
            "completed": current.trial.is_completed,
            "score": current.trial.score if current.trial.is_completed else None,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if not timeout_happened:
            set_payoff(player)


class Intro(Page):
    page_styles = ['game-style.css']


class Results(Page):
    page_styles = ['game-style.css']


page_sequence = [
    Intro,
    Practice,
    Main,
    Results,
]
