from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()

    age = models.IntegerField(min=18, max=90)
    gender = models.StringField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], widget=widgets.RadioSelect)
    agreement = models.BooleanField(label="I agree with something", widget=widgets.Checkbox)

    dropout = models.BooleanField(initial=False)
    misfit = models.BooleanField(initial=False)

    hidden_localtime = models.StringField(label="", blank=True, widget=None)

    field_scale = models.IntegerField(
        label="How much do you agree with something?",
        choices=[
            (1, "totally<br>disagree"),
            (2, "somewhat<br>disagree"),
            (3, ""),
            (4, ""),
            (5, "do not care"),
            (6, ""),
            (7, ""),
            (8, "somewhat<br>agree"),
            (9, "totally<br>agree"),
        ],
        widget=None,
        help_text="This field is rendered as a horizontal scale using very custom html",  # type: ignore
    )

    field_range = models.IntegerField(
        label="How much do you something?",
        min=-50,
        max=50,
        step=5,  # type: ignore
        initial=0,
        widget=None,
        help_text="This field is rendered as a horizontal scale using very custom html",  # type: ignore
    )

    field_foo = models.IntegerField(
        label="Something something",
        widget=None,
        choices=[1, 2, 3, 4, 5],
    )
    field_bar = models.IntegerField(
        label="Something something something something",
        widget=None,
        choices=[1, 2, 3, 4, 5],
    )
    field_baz = models.IntegerField(
        label="Something something something something something something",
        widget=None,
        choices=[1, 2, 3, 4, 5],
    )

    field_qux = models.StringField(
        label="What's your something?",
        choices=[
            ("1", "One"),
            ("2", "Two"),
            ("3", "Three"),
            ("4", "Four"),
            ("OTHER", "Other"),
        ],
    )

    field_qux_other = models.StringField(label="Specify your something", blank=True)
