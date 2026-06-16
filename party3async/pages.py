from otree.api import Page

from _extras.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Group, Player, Response, Trial  # noqa
from .progress import Progress


class Main(LivePage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css", "_extras/grid.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @staticmethod
    def vars_for_template(player: Player):
        return {"chat_seq": list(range(C.CHAT_LEN))}

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        if current.trial is not None:
            # page reloaded while running trial
            yield "progress", page.output_progress(current)
            if current.trial.is_running:
                # the trial is still pending
                yield "trial", page.output_trial(current.trial)
            return

        advanced = progress.advance(current)
        group = advanced.group

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
    def live_response(page, player: Player, trialid: int, time: int, utterance: str) -> LiveResponding:
        current = progress.current(page, player)
        group = current.group
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        response = progress.respond(current, utterance, response_time=time)

        yield group, "progress", page.output_progress(current)
        yield player, "feedback", page.output_feedback(current.trial, response)
        yield group, "update", page.output_trial(current.trial)
        if current.trial.is_completed:
            yield group, "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress) -> LivePayload:
        pagename, player, iteround, trial = current
        assert iteround
        return {
            "terminated": iteround.is_closed,
            "total": C.NUM_TRIALS,
            "passed": iteround.progress_trials,
            "current": trial.iteration if trial else None,
            "pending": not current.is_running,
            "score": f"{iteround.total_score:n}",
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "chat": page.output_chat(Response.all(trial)),
        }

    @classmethod
    def output_chat(page, responses: list[Response]):
        return [{"id": r.player.id, "response": r.utterance} for r in responses]

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        assert response
        return {
            "response": response.utterance,
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+}" if trial.score is not None else None,
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
