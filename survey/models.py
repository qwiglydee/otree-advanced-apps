from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()

    age = models.IntegerField(min=18, max=90)
    gender = models.StringField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], widget=widgets.RadioSelect)
    agreement = models.BooleanField(label="I agree with something something", widget=widgets.Checkbox)

    dropout = models.BooleanField(initial=False)
    misfit = models.BooleanField(initial=False)

    hidden_localtime = models.StringField(label="", blank=True, widget=None)

    q_scale = models.IntegerField(
        label="How much do you agree with something",
        choices=[
            (1, "totally disagree"),
            (2, "somewhat disagree"),
            (3, ""),
            (4, ""),
            (5, ""),
            (6, ""),
            (7, ""),
            (8, "somewhat agree"),
            (9, "totally agree"),
        ],
        widget=None,
        help_text="This field is rendered as a horizontal scale using very custom html",  # type: ignore
    )

    q_range = models.IntegerField(
        label="How much do you something?",
        min=1,
        max=100,
        step=5,  # type: ignore
        widget=None,
        help_text="This field is rendered as a horizontal scale using very custom html",  # type: ignore
    )

    q_grid_foo = models.IntegerField(
        label="Something something",
        widget=None,
        choices=[1, 2, 3, 4, 5],
    )
    q_grid_bar = models.IntegerField(
        label="Something something something something something",
        widget=None,
        choices=[1, 2, 3, 4, 5],
    )
    q_grid_baz = models.IntegerField(
        label="Something something something something something something something something something something something",
        widget=None,
        choices=[1, 2, 3, 4, 5],
    )

    q_foo = models.StringField(
        label="Something something?",
        choices=[
            ("F1", "Foo 1"),
            ("F2", "Foo 2"),
            ("F3", "Foo 3"),
            ("F4", "Foo 4"),
            ("OTHER", "Other"),
        ],
    )

    q_foo_other = models.StringField(label="Specify your foo", blank=True)
