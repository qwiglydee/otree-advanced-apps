from otree.api import Page

from _extras.livepage import LivePage, LivePayload, LiveResponding

from .conf import C
from .models import Group, Player, Response, Trial  # noqa
from .progress import Progress


class Main(LivePage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css", "_extras/grid.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        group = player.group
        current = Progress.current(page, player)

        # restore state on occasional page reload
        if current.trial is not None:
            yield player, "progress", page.output_progress(current)
            if current.trial.has_started:
                yield player, "trial", page.output_trial(current.trial)
            responded = Response.last(current.trial, player=player)
            if responded:
                yield player, "feedback", page.output_feedback(current.trial, responded)
            return

        advanced = Progress.advance(current)

        if advanced.trial and advanced.trial.has_started:
            yield group, "progress", page.output_progress(advanced)
            yield group, "trial", page.output_trial(advanced.trial)
        else:
            # just indicate status of gameover or something
            yield player, "progress", page.output_progress(advanced)

    @classmethod
    def live_response(page, player: Player, trialid: int, time: int, utterance: str) -> LiveResponding:
        group = player.group
        current = Progress.current(page, player)
        assert current.trial is not None
        assert trialid == current.trial.id, "mismatched response"
        assert utterance in C.RESPONSES, "invalid response"

        response = Progress.respond(current, utterance=utterance, response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        yield player, "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield group, "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, progress: Progress) -> LivePayload:
        player, iteround, trial = progress
        return {
            "total": C.NUM_TRIALS,
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": f"{iteround.total_score:n}",
            "current": trial.iteration if trial and trial.has_started else None,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "chat": page.output_chat(Response.allast(trial)) if trial.is_completed else None,
        }

    @classmethod
    def output_chat(page, responses: list[Response]):
        return [{"id": r.player.id_in_group, "response": r.utterance} for r in responses]

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        assert response
        return {
            "continue": not trial.is_closed,
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
