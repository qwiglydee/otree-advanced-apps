from typing import Self
from time import monotonic as now

from sqlalchemy import desc
from sqlalchemy.orm.exc import MultipleResultsFound

from otree.models import BasePlayer
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

    @property
    def is_closed(self) -> bool:
        return self.status == 'CLOSED'

    def start(self):
        self.processing_started = now()
        self.status = "STARTED"

    def close(self, reason: str):
        """Mark model as closed for some reason"""
        self.processing_ended = now()
        self.status = 'CLOSED'
        self.completion = reason

    def complete(self):
        """Mark model as (succesfully) completed
        Actual model could override this method to calculate and update some scores or something 
        (and it should call to `super().complete()`)
        """
        self.close("COMPLETED")

    @property
    def is_completed(self) -> bool:
        return self.completion == "COMPLETED"


class BaseRoundModel(IterStatusMixin, ExtraModel):
    """Base of model for round of trials
    A round is a bunch of repeating tasks.
    It consists of many trials (created separately via another model).

    Each round is linked to a page by it's name and should also be linked to a player or a group.

    Actual model in your app should add links to player or group models,
    and they should be explicitely provided to all the methods via their kwargs.
    """
    __abstract__ = True

    pagename = database.StringField()

    # add additional linking fields, such as:
    # player = database.Link(Player)
    # group = database.Link(Group)

    def init(self, **kwargs):
        """Initialize newly created round
        Called automatically (without kwargs) when a model is created.
        Could be called manually (with some args) to reinitialize with some parameters.
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.init")

    @classmethod
    def current(cls, pagename: str, **kwargs) -> Self:
        """Get current round matching the given pagename and kwargs.
        Returns None if none yet created.
        """
        assert 'player' in kwargs or 'group' in kwargs
        try:
            return cls.objects_filter(pagename=pagename, **kwargs).one_or_none()
        except MultipleResultsFound:
            raise RuntimeError(f"Multiple of matching {cls.__name__} created")

    @classmethod
    def create_new(cls, pagename: str, **kwargs) -> Self:
        """Create new record of round for the given pagename and kwargs"""
        assert 'player' in kwargs or 'group' in kwargs
        instance = cls.create(pagename=pagename, **kwargs, status='NEW')
        instance.init()
        db.commit()
        return instance

    @classmethod
    def advance(cls, pagename: str, **kwargs) -> Self:
        """Get existing or create a new round for the given pagename and kwargs"""
        thenext = cls.current(pagename, **kwargs)
        if thenext is None:
            thenext = cls.create_new(pagename, **kwargs)
        return thenext

    def update(self):
        """Update some stats
        Used to update some fields after the round is started or a trial is completed
        """
        # a placeholder to be implemented in some specific models


class BaseTrialModel(IterStatusMixin, ExtraModel):
    """Base of model for trial
    A trial is an instance of repeating task with some particular parameters.
    It may have one or more responses (created separately via another model).

    Each trial is linked to a round, and in turn - to a page and player/group
    They are ordered within round by sequential iteration number.

    Actual model in your app should add link to round model. 
    And obviously all the parameters of the task.
    """
    __abstract__ = True

    iteround = database.Link(BaseRoundModel)  # probably: redefine in concrete subclass
    iteration = database.IntegerField(initial=0)

    def init(self, **kwargs):
        """Initialize newly created trial
        Called automatically (without kwargs) when a model is created.
        Could be called manually (with some args) to reinitialize with some parameters.
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.init")

    @classmethod
    def current(cls, iteround: BaseRoundModel) -> Self:
        """Get current (already started) trial in the round.
        Returns None if none started yet.
        """
        try:
            return cls.objects_filter(iteround=iteround, status='STARTED').one_or_none()
        except MultipleResultsFound:
            raise RuntimeError(f"Multiple of {cls.__name__} started")

    @classmethod
    def create_new(cls, iteround: BaseRoundModel, iteration: int) -> Self:
        """Create a new trial within given round"""
        instance = cls.create(iteround=iteround, iteration=iteration, status='NEW')
        instance.init()
        return instance

    @classmethod
    def create_many(cls, iteround: BaseRoundModel, count: int) -> list[Self]:
        """Create many trials within given round"""
        instances = [cls.create_new(iteround, 1 + i) for i in range(count)]
        db.commit()
        return instances

    @classmethod
    def create_next(cls, iteround: BaseRoundModel) -> Self:
        """Create a neext trial within given round, 
        with sequential iteration number
        """
        cnt = cls.count(iteround, status='CLOSED')
        instance = cls.create_new(iteround=iteround, iteration=cnt + 1)
        db.commit()
        return instance

    @classmethod
    def advance_next(cls, iteround: BaseRoundModel):
        """Get or create next trial
        Works both for pre-generated trials or created on the fly
        """
        thenext = cls.first(iteround, status='NEW')
        if thenext is None:
            thenext = cls.create_next(iteround)
        return thenext

    def update(self):
        """Update some stats
        Used to update some fields after the trial is completed.
        """
        # a placeholder to be implemented in some specific models

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
    """Base of model for response.
    A response is a single reaction on trial from a player.
    A trial can have one or more responses from one or different players.

    Responses are also enumerated by `iteration` number,
    and could be further qualified in your app with player roles or stages or whatever

    Actual model in your app should extend it with fields describing the response 
    and any outcomes such as success or payoff or something.
    """

    __abstract__ = True

    trial = database.Link(BaseTrialModel)  # replace with link to actual Trial
    player = database.Link(BasePlayer)  # repalce with link to actual Player
    iteration = database.IntegerField()

    @classmethod
    def create_next(cls, trial: BaseTrialModel, player: BasePlayer, **kwargs) -> Self:
        """Create next response for the given trial.
        The response has sequential iteration number.
        The kwargs may add some additional specific like stage/phase.
        """
        cnt = cls.count(trial)
        return cls.create(trial=trial, player=player, iteration=cnt + 1, **kwargs)

    def respond(self, **kwargs):
        """Initialize the response and calculate result.
        This should set all the response and result fields.
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.respond")

    @classmethod
    def count(cls, trial: BaseTrialModel, **kwargs) -> int:
        return cls.objects_filter(trial=trial, **kwargs).count()

    @classmethod
    def list(cls, trial: BaseTrialModel, **kwargs) -> list[Self]:
        return list(cls.objects_filter(trial=trial, **kwargs).order_by("iteration"))

    @classmethod
    def last(cls, trial: BaseTrialModel, **kwargs) -> Self:
        return cls.objects_filter(trial=trial, **kwargs).order_by(desc("iteration")).first()
