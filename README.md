> :warning: The repository is currently work in progress. The apps are not yet field-tested.
>
> Use with caution

# otree-advanced-apps

The repository contains utilities and example apps for [oTtree](https://www.otree.org/) (v6)
with some advanced features and techniques beyond standard capabilities of the oTree.

## The Features

Major features:

- Micro-framework to simplify creating dynamic live page content:
    - dynamically (by scripts) changing page content, controls, switching visibility of sections
    - reacting on user inputs, clicks, keystrokes
    - reacting on live messages from server (from another players)
    - reacting on timers
- Improved scheme of communicating with live pages
- Extra data models for iterative tasks
- Scheme for running the iterative tasks within single page
    - can run separate rounds on different pages
    - runs pre-generated list of tasks or generate tasks on the fly
    - each round has multiple trials and possibly multiple responses (retries, sampling or multiplayer)
    - the sequence can terminate on exhausting of the task or by some calculated condition
- Some other minor utilites to simplify development
- Styles for fullscreen layout with centered content
- Also, some other vibrant styles to make it look more game-like

## The Apps

All the apps intended to be used as starting points.
Their content is intentionally dull with arbitrary parameters.

- [Survey](survey): a traditional survey with some enhancements in styles and input widgets
- [Quiz](quiz): questions sampled from a file with multi-choice answers
- [Trials 1](trials1): simple trials with text/numeric input
- [Trials 2](trials2): trials with choices for answers
- [Trials 3](trials3): trials with a stage for decision and answering in different methods
- [Lottery 1](lottery1): lottery with cards-like buttons with different outcomes
- [Lottery 2s](lottery2s): lottery with sampling phase (multiple responses in sampling + 1 final response)
- [Ultimatum 2](ultimatum2): classic 2-player game of ultimatum, with pre-recruiting of participants
    - assuming the participants are all well-known and won't drop out (a case like a controlled lab environment)
    - participants are grouped on session initialization
- [Ultimatum 2t](ultimatum2t): a 2-player game, with online recruiting of participants
    - assuming the participants may drop out of the game
    - participants are grouped on arrival with roles assigned dynamically
    - when a participant drops out, the game round is terminated (and the session continues with remaining participant)
- [Ultimatum 3](ultimatum3): a 2-player game, with chaotic recruiting of participants
    - additional `screener` app to possibly filter out participants without affecting remaining ones
    - the screener pre-assigns roles to minimize waiting time of already involved participants
- [Async Party](party3async): multiplayer chat-like trials with asyncronous responses
    - players respond in random order and observe partners' responses immediately
- [Parallel Party](party3parallel): the party game with parallel responses
    - players respond in random order, but they only observe partners' responses after all responded
- [Serial Party](party3serial): the party game with serial responding
    - players respond in turns defined by a sequence and they observe partners' responses as they're given
- [Stub](stub): just a minimal app with round/trial/response/feedback/result scheme
- TODO: Sliders: the classic real effort task

Most of the apps have many common fatures:

- Most of apps implement scheme with trial/response/feedback/result repeated in rounds.
- Some apps have 'practice' and 'main' rounds with the same logic, but different feedbacks/delays/etc.
- Some of the 'practice' rounds support multiple retries.
- Tasks are generated dynamically according to configured random distributions (except for the `quiz`)
- Apps do not reveal any correct/best answers into browser, to prevent any kind of cheating.
- Multiplayer games implement 'pending' state of waiting other participants to catch up between each trial and each page/round.
- Games use `points` for scoring, with customizable decimal formatting. In the end of the game they're converted to configured real currency.

## The Style

The look and feel is designed to resemble some table games with paper sheets, cards and tags.

The styles utilize [classic boostrap palette](https://getbootstrap.com/docs/5.3/helpers/color-background/) with `primary` used for all main elements and form controls.

Layout of pages is in a game paradigm:

- page header: global status (progress, total score)
- upper center, main area: description of task or game state + feedback/results
- lower center, cockpit area: form controls, only visible when active
- page footer: hints about what to do

## The Code

The repository contains lots of stuff shared between the apps and it can be reused in other projects:

- [`_extras`](_extras): contains various python utilitis for server-side scripts
    - The utilities are totally independant of the apps and can be easily reused elsewhere
- [`_static/_extras`](_static/_extras): contains javascript scripts and css styles for pages
    - The scripts mostly depend on the `otree-front-*.js` micro-framework and should be used together
- [`_templates/_extras`](_templates/_extras): templates for pages to easily integate the scipts and styles

The apps are intended to be highly adjustable and their code is very structured and decoupled to make it clear as much as possible.

Common structure:

- `conf.py`: static constant parameters
- `models.py`: all the data records and calculations of all the parameters, fields and outcomes
- `progress.py`: code to run sequences of iterative tasks with rounds/trials/responses
- `pages.py`: description of the pages
    - pages `Main` or `TrialsPage` contain all the live communication logic, which is _almost_ the same for all the apps
    - templates `Main.html` and `Practice.html` contain browser-side scripts to support the communication logic, and adjust the page view
- all the parts are more or less replaceble on their own

All the code intensively use type-hining and inline docs to allow assistance from any smart IDE (like vscode, pycharm).
Also, there're lots of `assert` statement all around to detect any possible bugs at runtime.

Anyway, the code is far from being trivial and it's not that easy to use as of typical oTree apps. Also, it's somewhat overcomplicated with intention to fit any possible designs.
Dealing with it will require programming skills, or AI assistance, or hiring a professional developer.
