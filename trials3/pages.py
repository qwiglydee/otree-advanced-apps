from otree.views import Page

from _stuff.live import live_page

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
    def live_decision(page, player: Player, data: dict):
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"
        assert data['decision'] in C.STRATEGIES

        decision = data['decision']
        progress.respond_decision(current, decision, response_time=data['time'])

        yield "progress", page.display_progress(current)
        yield "update", page.display_trial(current)

    @classmethod
    def live_response(page, player: Player, data: dict):
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"

        if current.trial.strategy == 'INPUT':
            assert 'answer' in data and 'choice' not in data
            answer = str(data['answer'])
            response = progress.respond_answer(current, answer, response_time=data['time'])

        if current.trial.strategy == 'CHOOSE':
            assert 'choice' in data and 'answer' not in data
            button = str(data['choice'])
            answer = current.trial.options[button]
            response = progress.respond_answer(current, answer, response_time=data['time'], button=button)

        yield "progress", page.display_progress(current)
        yield "feedback", page.display_feedback(current, response)
        if current.trial.is_completed:
            yield "result", page.display_result(current)

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "total": C.NUM_TRIALS[current.pagename],
            "finished": current.iteround.is_closed,
            "passed": current.iteround.progress_trials,
            "score": current.iteround.total_score,
            "current": current.trial.iteration if current.trial else None,
            "retries": current.retries_left if current.trial else None,
            "stage": current.stage if current.trial else None,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "task": current.trial.task,
            "options": current.trial.options,
            "strategy": current.trial.strategy,
        }


@live_page
class Practice(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert current.trial and response
        return {
            "final": current.trial.is_completed,
            "correct": response.correct,
        }

    @staticmethod
    def display_result(current: Progress):
        assert current.trial and current.trial.is_completed
        return {
            "score": current.trial.score,
            "truth": current.trial.truth,
        }


@live_page
class Main(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert current.trial and response
        return {
            "final": True,
        }

    @staticmethod
    def display_result(current: Progress):
        assert current.trial and current.trial.is_completed
        return {
            "score": current.trial.score,
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
