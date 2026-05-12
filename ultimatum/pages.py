from otree.views import Page

from _stuff.live import live_page

from .conf import C, Points
from .models import Player
from .progress import Progress
from . import progress


@live_page
class Main(Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']  # noqa
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]  # noqa

    def get_template_name(self):
        # different page templates by role
        return f"{__package__}/Main_{self.player.role}.html"

    @classmethod
    def live_continue(page, player: Player, _):
        group = player.group
        current = progress.current(player)

        # restore trial on page reloading
        if current.is_running:
            yield player, "progress", page.display_progress(current)
            yield player, "trial", page.display_trial(current)
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
    def live_proposal(page, player: Player, data: dict):
        group = player.group
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"

        assert 'proposal' in data
        proposal = Points(data['proposal'])
        progress.respond_proposal(current, proposal, response_time=data['time'])

        yield group, "progress", page.display_progress(current)
        yield group, "update", page.display_trial(current)

    @classmethod
    def live_decision(page, player: Player, data: dict):
        group = player.group
        current = progress.current(player)
        assert current.trial and current.trial.id == data['id'], "mismatched response"

        assert 'decision' in data and data['decision'] in C.DECISIONS
        decision = data['decision']
        progress.respond_decision(current, decision, response_time=data['time'])

        yield group, "progress", page.display_progress(current)
        yield group, "update", page.display_trial(current)
        if current.trial.is_completed:
            yield group, "result", page.display_result(current)

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "total": C.NUM_TRIALS,
            "finished": current.iteround.is_completed,
            "passed": current.iteround.progress_trials,
            "pending": not current.is_running,
            "current": current.trial.iteration if current.trial else None,
            "turn": current.turn,
        }

    @staticmethod
    def display_trial(current: Progress):
        assert current.trial
        return {
            "id": current.trial.id,
            "endowment": current.trial.endowment,
            "proposal": current.trial.proposal,
            "decision": current.trial.decision,
        }

    @staticmethod
    def display_result(current: Progress):
        assert current.trial.is_completed
        return {
            "scores": current.trial.scores
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
