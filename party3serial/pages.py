from otree.api import Page

from _stuff.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Group, Player, Response, Trial  # noqa
from .progress import Progress


class Main(LivePage):
    page_styles = ["ot-progress.css", "ot-pulse.css"]
    page_scripts = ["ot-progress.js", "ot-pulse.js", "format.js"]

    @classmethod
    def live_load(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        if current.trial is None:
            yield from page.live_iterate(player)
        elif not current.trial.is_running:
            yield "progress", page.output_progress(current)
        else:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)
        current = progress.advance(current)
        group = current.group

        if current.trial is None:
            # no more trials
            yield group, "progress", page.output_progress(current)
        elif not current.trial.is_running:
            # pending state
            yield player, "progress", page.output_progress(current)
        else:
            yield group, "progress", page.output_progress(current)
            yield group, "trial", page.output_trial(current.trial)

    @classmethod
    def live_response(page, player: Player, trialid: int, utterance: str) -> LiveResponding:
        current = progress.current(page, player)
        group = current.group
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        response = progress.respond(current, utterance)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield player, "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield group, "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, progr: Progress) -> LivePayload:
        pagename, player, iteround, trial = progr
        assert iteround is not None
        return {
            "terminated": iteround.is_closed,
            "total": C.NUM_TRIALS,
            "passed": iteround.progress_trials,
            "current": trial.iteration if trial else None,
            "pending": not progr.is_running,
            "turn": progr.turn if progr.is_running else None,
            "score": iteround.total_score,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        chat = [{"id": r.player.id, "response": r.utterance} for r in Response.all(trial)]

        return {"id": trial.id, "responses": chat}

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        assert response
        return {
            "response": response.utterance,
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
    Main,
    Results,
]
