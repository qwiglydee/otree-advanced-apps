from typing import Self
from time import monotonic as now

from sqlalchemy import desc
from sqlalchemy.orm.exc import MultipleResultsFound

from otree.models import BasePlayer, BaseGroup
from otree.database import db, ExtraModel
from otree import database


class IterStatusMixin:
    """Tracking status of trials/rounds

    Field `status` denote processing status of trial:
    - NEW: just created / initialized
    - STARTED: displayed to participant
    - CLOSED: completed or terminated by some other reason

    Field `completion` is to specify reason of closing
    - COMPLETED: normally completed
    - TIMEOUTED: skipped by timeout
    - SKIPPED: skipped by some reason
    - anything else for other reasons
    """
    status = database.StringField(choices=['NEW', 'STARTED', 'CLOSED'])
    completion = database.StringField()

    processing_started = database.FloatField()
    processing_ended = database.FloatField()

    @property
    def processing_time(self) -> float:
        """Server-side time in seconds from being started to closed
        This includes all processing time and network latency.
        """
        if self.processing_started is None or self.processing_ended is None:
            return None
        return self.processing_ended - self.processing_started

    @property
    def is_pristine(self) -> bool:
        return self.status == 'NEW'

    @property
    def is_started(self) -> bool:
        return self.status == "STARTED"

    @property
    def has_started(self) -> bool:
        return self.status == "STARTED" or self.status == "CLOSED"

    def start(self):
        self.processing_started = now()
        self.status = "STARTED"

    def close(self, reason: str):
        self.processing_ended = now()
        self.status = 'CLOSED'
        self.completion = reason

    @property
    def is_closed(self) -> bool:
        return self.status == 'CLOSED'

    def complete(self):
        self.close("COMPLETED")

    @property
    def is_completed(self) -> bool:
        return self.completion == "COMPLETED"


class BaseRoundModel(IterStatusMixin, ExtraModel):
    __abstract__ = True

    pagename = database.StringField()

    # add additional linking fields, such as:
    # player = database.Link(Player)
    # group = database.Link(Group)

    def init(self, **kwargs):
        """Initialize newly created round
        Called automatically (without kwargs) when a record is created
        Should be called manually to reinitialize with some args
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.init")

    @classmethod
    def current(cls, pagename: str, **kwargs) -> Self:
        """Get current (started) round matching the given pagename and kwargs.
        Returns None if none started.
        """
        assert 'player' in kwargs or 'group' in kwargs
        try:
            return cls.objects_filter(pagename=pagename, **kwargs).one_or_none()
        except MultipleResultsFound:
            raise RuntimeError(f"Multiple of {cls.__name__} started")

    @classmethod
    def create_new(cls, pagename: str, **kwargs) -> Self:
        """Create new record of round for the given pagename and kwargs
        The new round is not started
        """
        assert 'player' in kwargs or 'group' in kwargs
        instance = cls.create(pagename=pagename, **kwargs, status='NEW')
        instance.init()
        db.commit()
        return instance

    @classmethod
    def advance(cls, pagename: str, **kwargs) -> Self:
        """Get or create iteround for the given page and kwargs"""
        thenext = cls.current(pagename, **kwargs)
        if thenext is None:
            thenext = cls.create_new(pagename, **kwargs)
        return thenext


class BaseTrialModel(IterStatusMixin, ExtraModel):
    __abstract__ = True

    iteround = database.Link(BaseRoundModel)  # probably: redefine in concrete subclass
    iteration = database.IntegerField(initial=0)

    def init(self, **kwargs):
        """Initialize newly created trial
        Called automatically (without kwargs) when a record is created
        Should be called manually to reinitialize with some args
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.init")

    @classmethod
    def current(cls, iteround: BaseRoundModel) -> Self:
        """Get current (started) trial in the round.
        Returns None if none started.
        """
        try:
            return cls.objects_filter(iteround=iteround, status='STARTED').one_or_none()
        except MultipleResultsFound:
            raise RuntimeError(f"Multiple of {cls.__name__} started")

    @classmethod
    def create_new(cls, iteround: BaseRoundModel, iteration: int) -> Self:
        instance = cls.create(iteround=iteround, iteration=iteration, status='NEW')
        instance.init()
        return instance

    @classmethod
    def create_many(cls, iteround: BaseRoundModel, count: int) -> list[Self]:
        instances = [cls.create_new(iteround, 1 + i) for i in range(count)]
        db.commit()
        return instances

    @classmethod
    def create_next(cls, iteround: BaseRoundModel) -> Self:
        cnt = cls.count(iteround, status='CLOSED')
        instance = cls.create_new(iteround=iteround, iteration=cnt + 1)
        db.commit()
        return instance

    @classmethod
    def advance_next(cls, iteround: BaseRoundModel):
        thenext = cls.first(iteround, status='NEW')
        if thenext is None:
            thenext = cls.create_next(iteround)
        return thenext

    @classmethod
    def count(cls, iteround: BaseRoundModel, **kwargs) -> int:
        return cls.objects_filter(iteround=iteround, **kwargs).count()

    @classmethod
    def list(cls, iteround: BaseRoundModel, **kwargs) -> list[Self]:
        return list(cls.objects_filter(iteround=iteround, **kwargs).order_by("iteration"))

    @classmethod
    def first(cls, iteround: BaseRoundModel, **kwargs) -> Self:
        return cls.objects_filter(iteround=iteround, **kwargs).order_by("iteration").first()

    @classmethod
    def last(cls, iteround: BaseRoundModel, **kwargs) -> Self:
        return cls.objects_filter(iteround=iteround, **kwargs).order_by(desc("iteration")).first()


class BaseResponseModel(ExtraModel):
    __abstract__ = True

    trial = database.Link(BaseTrialModel)  # replace with link to actual Trial
    player = database.Link(BasePlayer)  # repalce with link to actual Player
    iteration = database.IntegerField()

    @classmethod
    def create_next(cls, trial: BaseTrialModel, player: BasePlayer, **kwargs) -> Self:
        cnt = cls.count(trial)
        return cls.create(trial=trial, player=player, iteration=cnt + 1, **kwargs)

    @classmethod
    def count(cls, trial: BaseTrialModel, **kwargs) -> int:
        return cls.objects_filter(trial=trial, **kwargs).count()

    @classmethod
    def list(cls, trial: BaseTrialModel, **kwargs) -> list[Self]:
        return list(cls.objects_filter(trial=trial, **kwargs).order_by("iteration"))

    @classmethod
    def last(cls, trial: BaseTrialModel, **kwargs) -> Self:
        return cls.objects_filter(trial=trial, **kwargs).order_by(desc("iteration")).first()


def track_players(group: BaseGroup, player: BasePlayer, tracking_prop: str, tracking_val) -> bool:
    setattr(player, tracking_prop, tracking_val)
    players = group.get_players()
    return all(p.field_maybe_none(tracking_prop) == tracking_val for p in players)
