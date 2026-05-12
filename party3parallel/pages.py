from otree.views import Page

from _stuff.live import live_page

from .conf import C
from .models import Group, Player, Trial, Response  # noqa
from .progress import Progress
from . import progress


class LiveMethods:
    @classmethod
    def live_continue(page, player: Player, _):
        group: Group = player.group
        current = progress.current(player)

        # restoring incomplete trial when page occasionally reloaded
        if current.is_running:
            yield player, "progress", page.display_progress(current)
            yield player, "trial", page.display_trial(current)
            resp = Response.last(current.trial, player=player)
            if resp:
                yield player, "feedback", page.display_feedback(current, resp)
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
    def live_response(page, player: Player, data: dict):
        group = player.group
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"

        utterance = str(data['utterance'])
        response = progress.respond(current, utterance)

        yield group, "progress", page.display_progress(current)
        yield group, "update", page.display_trial(current)
        yield player, "feedback", page.display_feedback(current, response)
        if current.trial.is_completed:
            yield group, "result", page.display_result(current)


@live_page
class Main(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "finished": current.iteround.is_completed,
            "total": C.NUM_TRIALS,
            "passed": current.iteround.progress_trials,
            "current": current.trial.iteration if current.trial else None,
            "pending": not current.is_running,
            "score": current.iteround.total_score,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial

        if current.trial.is_completed:
            responses = Response.group_last(current.trial, current.group)
            chat = [{'id': r.player.id, 'response': r.utterance} for r in responses]
        else:
            chat = None

        return {
            "id": current.trial.id,
            "responses": chat
        }

    @staticmethod
    def display_feedback(current: Progress, response: Response):
        assert response
        return {
            "response": response.utterance
        }

    @staticmethod
    def display_result(current: Progress):
        assert current.trial.is_completed
        return {
            "score": current.trial.score,
        }


class Intro(Page):
    pass


class Results(Page):
    pass


page_sequence = [
    Intro,
    Main,
    Results,
]
