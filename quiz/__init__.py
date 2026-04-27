from otree.views import Page

from _stuff.live import live_page
from _stuff.config import get_session_param

from .const import C
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_trials  # noqa
from .source import load_source, sample_data
from .progress import Progress
from . import progress


def creating_session(subsession: Subsession):
    session = subsession.session
    sourcefile = session.config['source']
    sourcedata = load_source(sourcefile)

    for player in subsession.get_players():
        player.condition = get_session_param(session, 'condition', choices=C.CONDITIONS, default="random")
        generate_trials(C.NUM_TRIALS['Tasks'], player, 'Tasks', sourcedata, 'Task')


def generate_trials(count: int, player: Player, pagename: str, sourcedata: list[dict], section: str):
    iteround = Round.create_new(pagename, player=player)
    tasks = sample_data(sourcedata, count, condition=player.condition, section=section)
    trials = Trial.create_many(iteround, count)
    for trial, task in zip(trials, tasks, strict=True):
        trial.init(**task)


def set_payoff(player: Player):
    player.payoff = player.total_score


# PAGES

class LiveMethods:
    @classmethod
    def live_continue(page, player: Player, _):
        current = progress.current(player)

        # restore trial on page reloading
        if current.trial and current.trial.is_started:
            yield "trial", page.display_trial(current)
            yield "progress", page.display_progress(current)
            return

        current = progress.advance(current)

        if current.trial:
            yield "trial", page.display_trial(current)
        yield "progress", page.display_progress(current)

    @classmethod
    def live_response(page, player: Player, message: dict):
        current = progress.current(player)
        assert current.trial and current.trial.id == message['id'], "mismatched response"

        answer = current.trial.options[message['choice']]
        current = progress.respond(current, response_time=message['time'], answer=answer)

        yield "feedback", page.display_feedback(current)
        yield "update", page.display_trial(current)
        yield "progress", page.display_progress(current)


@live_page
class Tasks(LiveMethods, Page):
    page_styles = ['game-style.css', 'ot-progress.css', 'ot-pulse.css']
    page_scripts = ['otree-front-live.js', 'ot-progress.js', 'ot-pulse.js']

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        progr = {
            "finished": current.iteround.is_completed,
            "total": progress.max_trials(current.iteround),
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
        }

        if current.trial:
            progr.update({
                "current": current.trial.iteration,
                "started": current.trial.has_started,
                "completed": current.trial.is_completed,
            })

        return progr

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "task": current.trial.task,
            "options": current.trial.options,
            "score": current.trial.score if current.trial.is_completed else None,
            "truth": current.trial.truth if current.trial.is_completed else None,
        }

    @staticmethod
    def display_feedback(current: Progress):
        assert current.response
        return {
            "correct": current.response.correct,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if not timeout_happened:
            set_payoff(player)


page_sequence = [
    Tasks,
]
