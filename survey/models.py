from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.forms import widgets

from _stuff.widgets.hidden import HiddenWidget
from _stuff.widgets.slider import IntegerSlider


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()

    age = database.IntegerField(min=18, max=90)
    gender = database.StringField(
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
        widget=widgets.RadioSelect
    )
    localtime = database.StringField(label="", blank=True, widget=HiddenWidget)

    q_range = database.IntegerField(
        label="How much do you something?",
        min=1, max=100,
        widget=IntegerSlider)

    q_scale = database.IntegerField(
        label="How much do you agree with something",
        choices=[
            (1, "1<br> totally disagree"),
            (2, "2<br> somewhat disagree"),
            (3, "3"),
            (4, "4<br> somewhat agree"),
            (5, "5<br> totally agree"),
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    q_foo_c1 = database.StringField(
        label="Something something?",
        choices=[
            ("F1", "Foo 1"),
            ("F3", "Foo 3"),
        ],
        widget=widgets.RadioSelect,
    )

    q_foo_c2 = database.StringField(
        label="Something something?",
        choices=[
            ("F2", "Foo 2"),
            ("F4", "Foo 4"),
        ],
        widget=widgets.RadioSelect,
    )

    q_bar_c1 = database.StringField(
        label="Something something?",
        choices=[
            ("B1", "Bar 1"),
            ("B3", "Bar 3"),
        ],
        widget=widgets.RadioSelect,
    )

    q_bar_c2 = database.StringField(
        label="Something something?",
        choices=[
            ("B2", "Bar 2"),
            ("B4", "Bar 4"),
        ],
        widget=widgets.RadioSelect,
    )

    q_baz = database.StringField(
        label="Something something?",
        choices=[
            ("Z1", "Baz 1"),
            ("Z2", "Baz 2"),
            ("Z3", "Baz 3"),
            ("Z4", "Baz 4"),
            ("Z0", "Other"),
        ],
    )

    q_baz_other = database.StringField(label="Specify baz", blank=True)

    q_qux = database.StringField(
        label="Something something?",
        choices=[
            ("Q1", "Qux 1"),
            ("Q2", "Qux 2"),
            ("Q3", "Qux 3"),
            ("Q4", "Qux 4"),
            ("Q0", "Other"),
        ],
    )

    q_qux_other = database.StringField(label="Specify qux", blank=True)
