from time import monotonic as now
from typing import Self

from otree.api import BasePlayer, models
from otree.database import db, ExtraModel
from sqlalchemy import desc
from sqlalchemy.orm.exc import MultipleResultsFound


class IterStatusMixin:
    """Tracking status of rounds/trials/responses

    All the models can be created/started/closed
    The field `status` indicates processing stage:
    - NEW: just created / initialized
    - STARTED: displayed to participant
    - CLOSED: completed or terminated by some other reason

    Additionally, field `completion` indicates reason of closing:
    - COMPLETED: normally completed
    - use anything else for additional reasons
    """

    status = models.StringField(choices=["NEW", "STARTED", "CLOSED"])
    completion = models.StringField()

    processing_started = models.FloatField()
    processing_ended = models.FloatField()

    @property
    def processing_time(self) -> float | None:
        """Server-side time in seconds from being started to closed
        This includes all processing time and network latency.
        """
        if self.processing_started is None or self.processing_ended is None:
            return None
        return self.processing_ended - self.processing_started

    @property
    def is_pristine(self) -> bool:
        return self.status == "NEW"

    @property
    def has_started(self) -> bool:
        return self.status != "NEW"

    @property
    def is_running(self) -> bool:
        return self.status == "STARTED"

    @property
    def is_closed(self) -> bool:
        return self.status == "CLOSED"

    def start(self):
        self.processing_started = now()
        self.status = "STARTED"

    def close(self, reason: str):
        """Mark model as closed for some reason"""
        self.processing_ended = now()
        self.status = "CLOSED"
        self.completion = reason

    def complete(self):
        """Mark model as (succesfully) completed
        Actual model could override this method to calculate and update some scores or something.
        Overriden method should call `self.close("COMPLETED")` to track status.
        """
        self.close("COMPLETED")

    @property
    def is_completed(self):
        return self.is_closed and self.completion == "COMPLETED"


class BaseRoundModel(IterStatusMixin, ExtraModel):
    """Base of model for rounds
    A round consists of trials (created separately via another model).
    It corresponds to a page and player or gruup

    Actual model in your app should add links to player or group models, whatever applies.
    Links to the player/group should be provided in all the methods via their kwargs
    """

    __abstract__ = True

    pagename = models.StringField()

    # add additional linking fields, such as:
    # player = models.Link(Player)
    # group = models.Link(Group)

    def init(self):
        """Initialize newly created round
        Called automatically when a model is created.
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.init")

    def update(self):
        """Update some stats
        Calculate something reflecting current state when the round is just started or a trial is completed.
        Used in progress.py
        """
        # a placeholder to be implemented in some specific models

    @classmethod
    def current(cls, pagename: str, **kwargs) -> Self | None:
        """Get current round matching the given pagename and kwargs.
        Returns None if none yet created.
        """
        assert "player" in kwargs or "group" in kwargs
        try:
            cls.objects_filter()
            return cls.objects_filter(pagename=pagename, **kwargs).one_or_none()
        except MultipleResultsFound:
            raise RuntimeError(f"Multiple of matching {cls.__name__} created")

    @classmethod
    def create_new(cls, pagename: str, **kwargs) -> Self:
        """Create new round for the given pagename and kwargs"""
        assert "player" in kwargs or "group" in kwargs
        instance = cls.create(pagename=pagename, **kwargs, status="NEW")
        instance.init()
        db.commit()
        return instance

    @classmethod
    def pick_curr(cls, pagename: str, **kwargs) -> Self:
        """Create or get already created round for the given page and kwargs
        Works both for pre-generated rounds or created on the fly
        """
        thenext = cls.current(pagename, **kwargs)
        if thenext is None:
            thenext = cls.create_new(pagename, **kwargs)
        return thenext

    @classmethod
    def totall(cls) -> list[Self]:
        """Retrieve totally all rounds in the app"""
        return cls.objects_filter().all()


class BaseTrialModel(IterStatusMixin, ExtraModel):
    """Base of model for trials
    A trial is an instance of repeating task with some particular parameters.
    It may have one or more responses (created separately via another model).

    Each trial is linked to a round, and in turn, to a page and player/group
    They are ordered within round by sequential iteration number.

    Actual model in your app should add link to round model.
    And obviously all the parameters of the task.
    """

    __abstract__ = True

    iteround = models.Link(BaseRoundModel)  # probably: redefine in concrete subclass
    iteration = models.IntegerField(initial=0)

    def init(self):
        """Initialize newly created trial
        Called automatically when a model is created.
        """
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.init")

    def update(self):
        """Update some stats
        Calculate something reflecting current state when the trial is just started or responded.
        Used in progress.py
        """
        # a placeholder to be implemented in some specific models

    @classmethod
    def current(cls, iteround: BaseRoundModel) -> Self | None:
        """Get current (already started) trial in the round.
        Returns None if none started yet.
        """
        try:
            return cls.objects_filter(iteround=iteround, status="STARTED").one_or_none()
        except MultipleResultsFound:
            raise RuntimeError(f"Multiple of {cls.__name__} started")

    @classmethod
    def create_new(cls, iteround: BaseRoundModel, iteration: int) -> Self:
        instance = cls.create(iteround=iteround, iteration=iteration, status="NEW")
        instance.init()
        return instance

    @classmethod
    def create_next(cls, iteround: BaseRoundModel) -> Self:
        """Create a next trial within given round
        With sequential iteration number following last closed trial
        """
        cnt = cls.count(iteround, status="CLOSED")
        instance = cls.create_new(iteround=iteround, iteration=cnt + 1)
        db.commit()
        return instance

    @classmethod
    def create_many(cls, iteround: BaseRoundModel, count: int) -> list[Self]:
        """Create many enumerated trials within given round"""
        instances = [cls.create_new(iteround, 1 + i) for i in range(count)]
        db.commit()
        return instances

    @classmethod
    def pick_next(cls, iteround: BaseRoundModel) -> Self:
        """Get or create next new trial
        Works both for pre-generated trials or created on the fly
        """
        thenext = cls.first(iteround, status="NEW")
        if thenext is None:
            thenext = cls.create_next(iteround)
        return thenext

    @classmethod
    def count(cls, iteround: BaseRoundModel, **kwargs) -> int:
        return cls.objects_filter(iteround=iteround, **kwargs).count()

    @classmethod
    def all(cls, iteround: BaseRoundModel, **kwargs) -> list[Self]:
        return cls.objects_filter(iteround=iteround, **kwargs).order_by("iteration").all()

    @classmethod
    def totall(cls) -> list[Self]:
        """Retrieve totally all trials in the app"""
        return cls.objects_filter().order_by("iteround_id", "iteration").all()

    @classmethod
    def first(cls, iteround: BaseRoundModel, **kwargs) -> Self | None:
        return cls.objects_filter(iteround=iteround, **kwargs).order_by("iteration").first()

    @classmethod
    def last(cls, iteround: BaseRoundModel, **kwargs) -> Self | None:
        return cls.objects_filter(iteround=iteround, **kwargs).order_by(desc("iteration")).first()


class BaseResponseModel(ExtraModel):
    """Base of model for responses.
    A response is a single reaction on trial from a player.
    A trial can have one or more responses from one or different players.

    Responses are enumerated by `iteration` field,
    so that trials can have multiple responses by retries, players, stages.

    Actual model in your app should extend it with some meaningful fields
    describing the response iself and any outcome like success or score.
    """

    __abstract__ = True

    trial = models.Link(BaseTrialModel)  # replace with link to actual Trial in your app
    player = models.Link(BasePlayer)  # repalce with link to actual Player in your app
    iteration = models.IntegerField(initial=0)

    @classmethod
    def create_next(cls, trial: BaseTrialModel, player: BasePlayer, **kwargs) -> Self:
        """Create next response for the given trial.
        The kwargs should specify all specific fields of the response.
        """
        cnt = cls.count(trial)
        return cls.create(trial=trial, player=player, iteration=cnt + 1, **kwargs)

    def evaluate(self):
        """Resolve outcomes of the response"""
        raise NotImplementedError(f"Missing method {self.__class__.__name__}.evaluate")

    @classmethod
    def count(cls, trial: BaseTrialModel, **kwargs) -> int:
        return cls.objects_filter(trial=trial, **kwargs).count()

    @classmethod
    def all(cls, trial: BaseTrialModel, **kwargs) -> list[Self]:
        return cls.objects_filter(trial=trial, **kwargs).order_by("iteration").all()

    @classmethod
    def totall(cls) -> list[Self]:
        """Retrieve totally all responses in the app"""
        return cls.objects_filter().order_by("trial_id", "iteration").all()

    @classmethod
    def last(cls, trial: BaseTrialModel, **kwargs) -> Self | None:
        return cls.objects_filter(trial=trial, **kwargs).order_by(desc("iteration")).first()

    @classmethod
    def allast(cls, trial: BaseTrialModel, **kwargs) -> list[Self]:
        """All responses with only last response from each player"""
        # this works for parallel, sequential, asyncronous single- and multi-responding
        all = cls.objects_filter(trial=trial, **kwargs).order_by("iteration").all()
        if len(all) == 0:
            return []
        pids = [r.player.id for r in all]
        return [r for i, r in enumerate(all) if r.player.id not in pids[i + 1 :]]
