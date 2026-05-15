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
    - 2 phases in each trial: sampling and final
    - multiple responses in sampling phase + last final response
    - outcomes of the cards are resolved for each response
- [Async Party](party3async): multiplayer chat-like trials with asyncronous responses
    - players respond in arbitrary order
    - they observe partners' responses immediately
- [Parallel Party](party3parallel): multiplayer chat-like trials with parallel responses
    - players respond in arbitrary order
    - but they only observe partners' responses at the end
- [Serial Party](party3serial): multiplayer chat-like trials with responses in serial order
    - players respond in turns by their group membership
    - they observe partners' responses immediately
- [Sequential Party](party3sequential): multiplayer chat-like trials with responses in order of custom sequence
    - players respond in turns by a custom sequence, that may contain multiple turns of the same role
    - they observe partners' responses immediately,
    - latter responces override former
- [Ultimatum 1](ultimatum1): classic ultimatum game, with pre-grouping of participants
    - participants are grouped on session initialization, like in a lab environment
    - assuming they won't drop out
    - condition can be assigned randomly to each group
- [Ultimatum 1b](ultimatum1b): the same, with one player replaced with bot
    - role of the only participant is pre-configured or selected at random
    - another role is played automatically with random answers
- [Ultimatum 2](ultimatum2): the ultimatum game, with pre-recruiting of participants
    - participants are grouped on arrival, like with online recruiting
    - assuming they can drop out during their game session
    - when one of participants does not respond, the game is cancelled
    - condition can be assigned randomly to each group
- [Ultimatum 2b](ultimatum2b): the same, with bots replacement
    - dropped out participants replaced by auto-responding

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
