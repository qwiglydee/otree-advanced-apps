from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import create_trials, custom_export_trials, custom_export_responses  # noqa
from .source import load_source, sample_data
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    session = subsession.session
    sourcefile = session.config['source']
    sourcedata = load_source(sourcefile)

    for player in subsession.get_players():
        player.condition = config_condition(session)
        round1 = Round.create_new('Practice', player=player)
        create_trials(round1, sample_data(sourcedata, C.NUM_TRIALS['Practice'], category='practice'))
        round2 = Round.create_new('Main', player=player)
        create_trials(round2, sample_data(sourcedata, C.NUM_TRIALS['Main'], category='task'))
