from os import environ
from decimal import Decimal as D

SESSION_CONFIGS = [
    dict(
        name="survey",
        app_sequence=["survey"],
        condition="random",
    ),
    dict(
        name="quiz",
        app_sequence=["quiz"],
        condition="random",
        source="questions.csv",
    ),
    dict(
        name="trials1",
        app_sequence=["trials1"],
        condition="random",
    ),
    dict(
        name="trials2",
        app_sequence=["trials2"],
        condition="random",
    ),
    dict(
        name="trials3",
        app_sequence=["trials3"],
        condition="random",
    ),
    dict(
        name="lottery1",
        app_sequence=["lottery1"],
        condition="random",
        disclosure="random",
    ),
    dict(
        name="lottery2s",
        app_sequence=["lottery2s"],
        condition="random",
        disclosure="random",
    ),
    dict(
        name="ultimatum2",
        app_sequence=["ultimatum2"],
        condition="random",
    ),
    dict(
        name="ultimatum1b",
        app_sequence=["ultimatum1b"],
        condition="random",
        role="random",
    ),
    dict(
        name="ultimatum2t",
        app_sequence=["ultimatum2t"],
        condition="random",
    ),
    dict(
        name="ultimatum2b",
        app_sequence=["ultimatum2b"],
        condition="random",
    ),
    dict(
        name="ultimatum3",
        app_sequence=["ultimatum3_screener", "ultimatum3"],
        condition="random",
        num_demo_participants=6,
    ),
    dict(name="party3async", app_sequence=["party3async"], num_demo_participants=3),
    dict(name="party3parallel", app_sequence=["party3parallel"], num_demo_participants=3),
    dict(name="party3serial", app_sequence=["party3serial"], num_demo_participants=3),
    dict(name="party3sequential", app_sequence=["party3sequential"], num_demo_participants=3),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    num_demo_participants=2,
    participation_fee=1.00,
    real_world_currency_per_point=D("0.1"),
)

PARTICIPANT_FIELDS = ["assignment"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# old way
# USE_POINTS = False  # = True breaks player.payoff and participant.payoff
# REAL_WORLD_CURRENCY_CODE = "EUR"

# new way
CURRENCY_UNIT = "units.EUR"

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

SECRET_KEY = "4250744705247"
