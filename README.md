> :warning: The repository is currently work in progress. Code is not quite usable

# otree-advanced-apps

The repository contains utilities and example apps for [oTtree](https://www.otree.org/) v6
with some advanced features and techniques beyond standard capabilities of the oTree.

## The Features

- interactive live pages with real-time dynamic content
    - immediate reacting on user inputs, timers, or live messages from server
    - dynamically changing content
    - hiding/showing page elements or toggling inputs
- system of repetitive tasks (trials) organized in rounds
    - running within single app (without repeating everything or reloading pages)
    - the rounds are run within one or several pages and linked to each player or group of players
    - the tasks could be generated on the fly or loaded from pre-generated data file
    - the trials can have one or multiple responses (several retries, multiple stages or multiple players)
- also, somewhat vibrant style and fullscreen layout

## The Apps

The apps are intended to serve as stubs/templates for real experiments.
Example content and calculations are intentionally dull so they can be easily replaced with something meaningful.

- [Survey](survey): a traditional survey with some enhancements in styles and input widgets
    - a hidden field to record local time
    - horizontal choices scale
    - form fields defined by a session condition
    - conditional fields for something 'other'
- [Quiz](quiz): trials of questions with answers' choices
    - the questions and choices are sampled from a data file
    - practice and main rounds on different pages with different feedback
- [Trials 1](trials1): trials with text input
    - tasks are geneated on the fly according to session condition
    - multiple retries in practice round
    - practice and main rounds on different pages with different feedback
- [Trials 2](trials2): trials with choices
    - tasks and choices are geneated on the fly according to session condition
    - multiple retries in practice round
    - practice and main rounds on different pages with different feedback
- [Trials 3](trials3): trials with 2 stages and different answering methods
    - the trials are of 2 stages: decision and answering
    - tasks and choices are geneated on the fly according to session condition
    - multiple retries in practice round
    - practice and main rounds on different pages with different feedback
- [Lottery 1](lottery1): lottery with cards-like buttons with different outcomes
    - lottery parameters are geneated on the fly according to configuration
    - layout of the buttons is randomized for each player
    - labels of the buttons are configurable (by default - arranged by screen position)
    - outcomes of the cards are resolved according to distribution parameters
- [Lottery 2s](lottery2s): lottery with sampling phase
    - multiple responses in sampling phase + last final response
    - outcomes of the cards are resolved for each response
- [Ultimatum 2](ultimatum2): classic 2-player game of ultimatum, with pre-recruiting of participants
    - assuming they are all well-known and won't drop out, like in a lab environment
    - participants are grouped on session initialization
- [Ultimatum 1b](ultimatum1b): a single-player version, with automated partner
    - role of the only participant is pre-configured or selected at random
    - another role is played automatically by an auto-responing script
- [Ultimatum 2t](ultimatum2t): a 2-player game, with online recruiting of participants
    - assuming the participants may drop out of the game
    - participants are grouped on arrival with roles assigned dynamically
    - when one of participants drops out, the game round is terminated (and the session continues with remaining player)
- [Ultimatum 2b](ultimatum2b): the same, with bot replacment
    - when one of participants drops out, the game round continues with auto-reponding script
- [Ultimatum 3](ultimatum3): a 2-player game, with chaotic recruiting of participants
    - assuming the participants can drop out from instruction pages, refuse a consent, or fail comprehension check
    - participants are first run individually through a separate screener app
    - the screener pre-assigns game roles to minimize waiting time of those who already passed
    - when one of participants drops out, the game round is terminated (and the session continues with remaining player)
- [Async Party](party3async): multiplayer chat-like trials with asyncronous responses
    - players respond in arbitrary order
    - they observe partners' responses immediately
- [Parallel Party](party3parallel): the party game with parallel responses
    - players respond in arbitrary order
    - but they only observe partners' responses after all responded
- [Serial Party](party3serial): the party game with serial responding
    - players respond in turns by their group membership
    - they observe partners' responses as they're given
- [Sequential Party](party3sequential): the party game with sequential responding
    - players respond in turns following a custom sequence, it may contain multiple turns for the same role
    - they observe partners' responses as they're given
    - later responses of the same player override former

## Usage

### From scratch

- setup oTree environment as usual
- copy all the content of the repository
- remove all apps except the one that best matches your need
- adjust code of the app

### From stub

If you already have existing project:

- copy content of `_static`, `_stuff` and `_templates` from this repo into your project
- copy directory of desired example app to your project
- adjust code of the app

### Utilities and scripts

The utilities are all intended to be used without modification in many apps.

Python utilities from `_stuff` can be imported with:

```python
from _stuff import somemodule
from _stuff.somemodule import something
```

Styles from `_static` can be included into page templates in block `styles`:

```html
{% block styles %}
<link rel="stylesheet" href="{{ static 'filename.css' }}" />
{% endblock %}
```

Scripts from `_static` can be added into page templates in block `scripts`:

```html
{% block scripts %}
<script src="{{ static 'filename.js' }}"></script>
{% endblock %}
```

The `ot-` and `otree-front-` scripts rely on the `otree-front` library that should also be included.

Templates from `_templates` can be used in your page by adding the line at top of your page template:

```html
{% extends "ExtPage.html" %}
```

(the same for `FullPage.html`)

The templates already include some scripts and styles from `_static`,
and allow adding additional stuff in python class:

```python
class SomePage(Page):
    page_styles = [ "somestyle.css" ]
    page_scripts = [ "somescript.js" ]
```

## The Code

All the code is written with intention of further modification and adjustment to fit various experiment designs.
It is structured as much as possible for better clarity and written in very general way to make it more reusable.
Some modules, scripts and snippets can be easily reused in other oTree applications.

The code extensively uses type hints to enable assisting from enough smart IDE.
(However, the core of oTree does not respect this approach.)
Also, it uses lots of `assert` statements to help detecting bugs at runtime.

Documentation is mostly inside the code in comments in modules from `_stuff` and `_static`.
Documentation for the `otree-front` is missing at the moment.
However, it's still quite not trivial and will require some programming skills or AI assistance.
