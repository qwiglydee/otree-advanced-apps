from otree.views import Page

from _stuff.livepage import LivePage

from .conf import C, Points
from .models import Player, Trial
from .progress import Progress
from . import progress


class Main(LivePage):
    page_styles = ['ot-progress.css', 'ot-pulse.css']  # noqa
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]  # noqa

    def get_template_name(self):
        # different page templates by role
        return f"{__package__}/Main_{self.player.role}.html"

    @classmethod
    def live_continue(page, player: Player):
        group = player.group
        current = progress.current(page, player)

        # restore trial on page reloading
        if current.is_running:
            yield player, "progress", page.output_progress(current)
            yield player, "trial", page.output_trial(current.trial)
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
    def live_proposal(page, player: Player, *, id: int, proposal: str, time: int):
        group = player.group
        current = progress.current(page, player)
        assert current.trial and current.trial.id == id, "mismatched response"

        proposal = Points(proposal)
        progress.respond_proposal(current, proposal, response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)

    @classmethod
    def live_decision(page, player: Player, *, id: int, decision: str, time: int):
        group = player.group
        current = progress.current(page, player)
        assert current.trial and current.trial.id == id, "mismatched response"

        assert decision in C.DECISIONS
        progress.respond_decision(current, decision, response_time=time)

        yield group, "progress", page.output_progress(current)
        yield group, "update", page.output_trial(current.trial)
        if current.trial.is_completed:
            yield group, "result", page.output_result(current.trial)

    @classmethod
    def output_progress(page, current: Progress):
        pagename, player, iteround, trial = current
        return {
            "total": C.NUM_TRIALS,
            "finished": iteround.is_completed,
            "passed": iteround.progress_trials,
            "pending": not current.is_running,
            "current": trial.iteration if trial else None,
            "turn": current.turn,
        }

    @classmethod
    def output_trial(page, trial: Trial):
        return {
            "id": trial.id,
            "endowment": trial.endowment,
            "proposal": trial.proposal,
            "decision": trial.decision,
        }

    @classmethod
    def output_result(page, trial: Trial):
        return {
            "scores": trial.scores
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
