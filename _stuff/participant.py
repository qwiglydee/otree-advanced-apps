from otree.models import BasePlayer, Participant


def find_player(participant: Participant, appname: str):
    """Find a player from another app corresponding to the same participant"""
    [other] = [p for p in participant.get_players() if p.get_folder_name() == appname]
    return other


def clone_fields(dst: BasePlayer, src: BasePlayer, fields: list[str]):
    """Copy some fields from a player of another app"""
    for fld in fields:
        setattr(dst, fld, getattr(src, fld))


def current_pagename(participant: Participant):
    return participant._current_page_name
