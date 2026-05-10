from otree.views import Page

from _stuff.live import live_page

from .conf import C, Points, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
# from .models import custom_export_trials, custom_export_responses  # noqa
from .progress import Progress
from . import progress


def creating_session(subsession: Subsession):
    session = subsession.session
    for group in subsession.get_groups():
        group.condition = config_condition(session)


def set_payoff(player: Player):
    iteround = Round.current('Main', group=player.group)
    player.payoff = iteround.total_scores[player.role]


# PAGES

class LiveMethods:
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
            yield group, "feedback", page.display_feedback(current)

    @staticmethod
    def display_progress(current: Progress):
        assert current.iteround
        return {
            "finished": current.iteround.is_completed,
            "total": progress.max_trials(current.iteround),
            "passed": current.iteround.progress_trials,
            "pending": not current.is_running,
            "current": current.trial.iteration if current.trial else None,
            "stage": current.stage,
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
    def display_feedback(current: Progress):
        assert current.trial.is_completed
        return {
            "completed": current.trial.is_completed,
            "scores": current.trial.scores
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if not timeout_happened:
            set_payoff(player)


@live_page
class Main(LiveMethods, Page):
    page_styles = ['ot-progress.css', 'ot-pulse.css']  # noqa
    page_scripts = ['ot-progress.js', 'ot-pulse.js', "format.js"]  # noqa

    def get_template_name(self):
        # different page templates by role
        return f"{__package__}/Main_{self.player.role}.html"


class Intro(Page):
    pass


class Results(Page):
    pass


page_sequence = [
    Intro,
    Main,
    Results,
]
