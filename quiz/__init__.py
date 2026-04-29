from otree.views import Page

from _stuff.live import live_page
from _stuff.config import get_session_param

from .const import C
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import create_trials, custom_export_trials  # noqa
from .source import load_source, sample_data
from .progress import Progress
from . import progress


def creating_session(subsession: Subsession):
    session = subsession.session
    sourcefile = session.config['source']
    sourcedata = load_source(sourcefile)

    for player in subsession.get_players():
        player.condition = get_session_param(session, 'condition', choices=C.CONDITIONS, default="random")
        create_tasks(sourcedata, player, 'Practice')
        create_tasks(sourcedata, player, 'Main')


def create_tasks(sourcedata: list[dict], player: Player, pagename: str):
    iteround = Round.create_new(pagename, player=player)
    data = sample_data(sourcedata, C.NUM_TRIALS[pagename], section=pagename, condition=player.condition)
    create_trials(iteround, data)


def set_payoff(player: Player):
    player.payoff = player.total_score


# PAGES

class LiveMethods:
    @classmethod
    def live_continue(page, player: Player, _):
        current = progress.current(player)

        # restore trial on page reloading
        if current.trial and current.trial.is_started:
            yield "progress", page.display_progress(current)
            yield "trial", page.display_trial(current)
            return

        current = progress.advance(current)

        yield "progress", page.display_progress(current)
        if current.trial:
            yield "trial", page.display_trial(current)

    @classmethod
    def live_response(page, player: Player, data: dict):
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"

        button = str(data['choice'])
        answer = current.trial.options[button]
        response = progress.respond(current, response_time=data['time'], button=button, answer=answer)

        yield "progress", page.display_progress(current)
        yield "feedback", page.display_feedback(current, response)


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
            "current": current.trial.iteration if current.trial else None
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "task": current.trial.task,
            "options": current.trial.options,
            "labels": current.trial.labels,
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert response
        return {
            "completed": current.trial.is_completed,
            "score": current.trial.score if current.trial.is_completed else None,
            "correct": response.correct,
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
            "current": current.trial.iteration if current.trial else None
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "task": current.trial.task,
            "options": current.trial.options,
            "labels": current.trial.labels,
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert response
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
