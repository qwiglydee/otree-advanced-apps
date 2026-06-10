from otree.api import Page

from _extras.layout import arrange
from _extras.livepage import LivePage, LivePayload, LiveResponding

from . import progress
from .conf import C
from .models import Player, Response, Trial
from .progress import Progress


class TrialsPage(LivePage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css", "_extras/cards.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]

    @classmethod
    def live_load(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        if current.trial is None:
            yield from page.live_iterate(player)
        else:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)

    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        current = progress.current(page, player)

        advanced = progress.advance(current)
        if advanced.trial is None:
            # no more trials
            yield "progress", page.output_progress(advanced)
        else:
            yield "progress", page.output_progress(advanced)
            yield "trial", page.output_trial(advanced.trial)

    @classmethod
    def live_response(page, player: Player, trialid: int, stage: str, button: int, time: int) -> LiveResponding:
        current = progress.current(page, player)
        assert current.iteround is not None and current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        choice = current.trial.layout[button]
        response = progress.respond(current, stage, choice, response_time=time, button=button)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress) -> LivePayload:
        pagename, player, iteround, trial = current
        assert iteround
        return {
            "total": C.NUM_TRIALS[pagename],
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": f"{iteround.total_score:n}",
            "current": trial.iteration if trial else None,
            "finalizable": current.is_finalizable if trial else None,
        }

    @classmethod
    def output_trial(page, trial: Trial) -> LivePayload:
        return {
            "id": trial.id,
            "labels": arrange(trial.layout, trial.get_labels()),
        }

    @classmethod
    def output_feedback(page, trial: Trial, response: Response) -> LivePayload:
        def fmt(val):
            # format as plain numbers or leave null
            return f"{val:n}" if val is not None else None

        outcomes = response.get_outcomes()
        return {
            "final": trial.is_completed,
            "outcomes": arrange(trial.layout, {key: fmt(val) for key, val in outcomes.items()}),
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        def fmt(val):
            # format as signed units or leave null
            return f"{val:+}" if val is not None else None

        return {
            "score": fmt(trial.score),
        }


class Practice(TrialsPage):
    pass


class Main(TrialsPage):
    pass


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
