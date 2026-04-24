from os import environ


SESSION_CONFIGS = [
    dict(
        name='survey',
        app_sequence=['survey'],
        condition="random",
    ),
    dict(
        name='trials1',
        app_sequence=['trials1'],
        condition="random",
    ),
    dict(
        name='trials2',
        app_sequence=['trials2'],
        condition="random",
    ),
    dict(
        name='quiz',
        app_sequence=['quiz'],
        condition="random",
        source="tasks.csv",
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    num_demo_participants=2,
    participation_fee=1.00,
    real_world_currency_per_point=0.10,
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True  # makes player.payoff as points or currency

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = '4250744705247'
