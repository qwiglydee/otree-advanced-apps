from otree.views import Page

from _stuff.livepage import LivePage

from .conf import C
from .models import Group, Player, Trial, Response  # noqa
from .progress import Progress
from . import progress


class Main(LivePage):
    page_styles = ['ot-progress.css', 'ot-pulse.css']
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]

    @classmethod
    def live_continue(page, player: Player):
        group: Group = player.group
        current = progress.current(page, player)

        # restoring incomplete trial when page occasionally reloaded
        if current.is_running:
            yield player, "progress", page.output_progress(current)
            yield player, "trial", page.output_trial(current.trial)
            resp = Response.last(current.trial, player=player)
            if resp:
                yield player, "feedback", page.output_feedback(current, resp)
            return

        current = progress.advance(current)

        if current.is_running:
            # synchronize progress and trial
            yield group, "progress", page.output_progress(current)
            yield group, "trial", page.output_trial(current.trial)
        else:
            # pending state
            yield player, "progress", page.output_progress(current)

    @classmethod
    def live_response(page, player: Player, *, id: int, utterance: str, time: int):
        group = player.group
        current = progress.current(page, player)
        assert current.trial and current.trial.id == id, "mismatched response"

        response = progress.respond(current, utterance)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield player, "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield group, "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress):
        pagename, player, iteround, trial = current
        return {
            "finished": iteround.is_completed,
            "total": C.NUM_TRIALS,
            "passed": iteround.progress_trials,
            "current": trial.iteration if trial else None,
            "pending": not current.is_running,
            "turn": current.turn,
            "score": iteround.total_score,
        }

    @classmethod
    def output_trial(page, trial: Trial):
        chat = [{'id': r.player.id, 'response': r.utterance} for r in Response.group_last(trial, trial.iteround.group)]
        return {
            "id": trial.id,
            "responses": chat
        }

    @classmethod
    def output_feedback(page, trial: Trial, response: Response):
        return {
            "response": response.utterance,
        }

    @classmethod
    def output_result(page, trial: Trial):
        return {
            "score": trial.score,
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
