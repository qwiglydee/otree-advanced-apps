from otree.models import BasePlayer, Participant
from otree.lookup import get_page_lookup


def find_player(participant: Participant, appname: str):
    [other] = [p for p in participant.get_players() if p.get_folder_name() == appname]
    return other


def clone_fields(dst: BasePlayer, src: BasePlayer, fields: list[str]):
    for fld in fields:
        setattr(dst, fld, getattr(src, fld))


def current_pagename(participant: Participant):
    return participant._current_page_name
