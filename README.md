# otree-advanced-apps

The repository contains utilities and example apps for [oTtree](https://www.otree.org/) v6
with some advanced features and techniques beyond standard capabilities of the oTree.

All the code is written implying further modifications and adjustment to fit various other experiment designs.
It is structured as much as possible for better clarity and written in very general/universal way to make it adjustable.
Some modules, scripts and snippets can be easily reused in other oTree applications.

The code is mostly documented in comments.
However, it's still quite complex and will require some programming skills or AI assistance.

## The Features

- interactive live pages with real-time dynamic content
    - immediate reacting on user inputs, timers, or live messages from server
    - dynamically changing content
    - hiding/showing page elements or toggling inputs
- system of repetitive tasks (trials) organized in rounds
    - running within single app (without repeating everything or reloading pages)
    - the rounds are run within one or several pages and linked to each player or group of players
    - the tasks are generated on the fly or loaded from pre-generated data file
    - the trials can have one or multiple responses (several retries, multiple stages or multiple players)
- also, somewhat vibrant style and fullscreen layout

## The Apps

Content of the demo apps is intentionally dull so they can be easily changed into something meaningful.

- [Survey](survey): a traditional survey with some enhancements in styles and input widgets
    - a hidden field to record local time
    - horizontal choices scale
    - form fields defined by a session condition
    - conditional fields for something 'other'
- [Quiz](quiz): trials of a simple math task with predefined choices for answer
    - tasks and choices are sampled from a data file
    - 2 rounds on separate pages:
        - practice: full feedback, 'continue' button
        - main: scarse feedback, auto-continue
- [Trials 1](trials1): trials of a math task with text input for answer
    - tasks are geneated on the fly according to session condition
    - multiple responses for retries
    - 2 rounds on separate pages:
        - practice: multiple retries, full feedback, 'continue' button
        - main: single attempt, scarse feedback, auto-continue
- [Trials 2g](trials2g): two-player trials with 2 stages of answering
    - each player answers in a corresponding stage according to player role
    - page updates to make players see partners answer
    - 2 rounds on separate pages:
        - practice: full feedback, 'continue' button
        - main: scarse feedback, auto-continue
- [Lottery 1](lottery1): lottery with cards-like buttons with different outcomes
    - lottery parameters are geneated on the fly according to configuration
    - layout of the buttons is randomized for each player
    - labels of the buttons are configurable (by default - arranged by screen position)
    - outcomes of the cards are resolved according to distribution parameters
- [Lottery 2s](lottery2s): lottery with sampling phase
    - 2 phases in each trial: sampling and final
    - multiple responses in sampling phase + last final response
    - outcomes of the cards are resolved for each response

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

The utilities in `_stuff` an `_static` are intended to be used without modification in many apps

Python utilities from `_stuff` can be imported with:

```python
from _stuff import somemodule
from _stuff.somemodule import something
```

Styles from `_static` can be included into page templates in block `styles`:

```html
{% block styles %}
<link rel="stylesheet" href="{{ static 'filename.css' }}" />
{% endblock }
```

Scripts from `_static` can be added into page templates in block `scripts`:

```html
{% block scripts %}
<script src="{{ static 'filename.js' }}"></script>
{% endblock }
```

Templates from `_templates` can be used in your page by adding the line at top of your page template:

```html
{% extends "ExtPage.html" %}
```

(the same for FullPage)

The templates already include some scripts and styles from `_static`,
and allow to add additional stuff in python class:

```python
class SomePage(Page):
    page_styles = [ "somestyle.css" ]
    page_scripts = [ "somescript.css" ]
```
