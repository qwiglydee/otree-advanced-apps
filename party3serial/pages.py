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
    def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)
        group = current.group

        if current.trial is not None:
            # page reloaded during a trial
            yield player, "progress", page.output_progress(current)
            if current.trial.is_running:
                # restore
                yield player, "trial", page.output_trial(current.trial)
        else:
            # go first/next round/trial
            advanced = progress.advance(current)

            if advanced.trial is None:
                # no more trials
                yield group, "progress", page.output_progress(advanced)
            elif not advanced.trial.is_running:
                # pending state
                yield player, "progress", page.output_progress(advanced)
            else:
                yield group, "progress", page.output_progress(advanced)
                yield group, "trial", page.output_trial(advanced.trial)

    @classmethod
    def live_response(page, player: Player, *, id: int, utterance: str) -> LiveResponding:
        group = player.group
        current = progress.current(page, player)
        assert current.trial is not None and current.trial.id == id, "mismatched response"

        response = progress.respond(current, utterance)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield player, "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield group, "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress):
        pagename, player, iteround, trial = current
        assert iteround is not None
        return {
            "terminated": iteround.is_closed,
            "total": C.NUM_TRIALS,
            "passed": iteround.progress_trials,
            "current": trial.iteration if trial else None,
            "pending": not current.is_running,
            "turn": current.turn if current.is_running else None,
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
