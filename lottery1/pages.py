from otree.api import Page

from _extras.layout import arrange
from _extras.livepage import LivePage, LivePayload, LiveResponding

from .conf import C
from .models import Player, Round, Response, Trial
from .progress import Progress


class TrialsPage(LivePage):
    @classmethod
    def live_iterate(page, player: Player) -> LiveResponding:
        current = Progress.current(page, player)

        # restore state on occasional page reload
        if current.trial is not None:
            yield "progress", page.output_progress(current)
            yield "trial", page.output_trial(current.trial)
            return

        advanced = Progress.advance(current)

        if advanced.trial and advanced.trial.has_started:
            yield "progress", page.output_progress(advanced)
            yield "trial", page.output_trial(advanced.trial)
        else:
            # just indicate status of gameover or something
            yield "progress", page.output_progress(advanced)

    @classmethod
    def live_response(page, player: Player, trialid: int, button: int, time: int) -> LiveResponding:
        current = Progress.current(page, player)
        assert current.trial is not None
        assert trialid == current.trial.id, "mismatched response"

        response = Progress.respond(current, choice=current.trial.layout[button], response_time=time, button=button)

        yield "progress", page.output_progress(current)
        yield "feedback", page.output_feedback(current.trial, response)
        if current.trial.is_completed:
            yield "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, progress: Progress) -> LivePayload:
        player, iteround, trial = progress
        return {
            "total": C.NUM_TRIALS[iteround.pagename],
            "terminated": iteround.is_closed,
            "passed": iteround.progress_trials,
            "score": f"{iteround.total_score:n}",
            "current": trial.iteration if trial else None,
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
            "continue": not trial.is_closed,
            "choice": trial.get_label(response.choice),  # onscreen label
            "outcomes": arrange(trial.layout, {key: fmt(val) for key, val in outcomes.items()}),
        }

    @classmethod
    def output_result(page, trial: Trial) -> LivePayload:
        return {
            "score": f"{trial.score:+}" if trial.score is not None else None,
        }


class Practice(TrialsPage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css", "_extras/cards.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]


class Main(TrialsPage):
    page_styles = ["_extras/ot-progress.css", "_extras/ot-pulse.css", "_extras/cards.css"]
    page_scripts = ["_extras/ot-progress.js", "_extras/ot-pulse.js"]


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
