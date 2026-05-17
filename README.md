> :warning: The repository is currently work in progress. Code is not quite usable

# otree-advanced-apps

The repository contains utilities and example apps for [oTtree](https://www.otree.org/) v6
with some advanced features and techniques beyond standard capabilities of the oTree.

## The Features

:bangbang: TODO

- /dynamic content with otree-front/
- /rounds of trials/
    - /multiple rounds/trials/responses/
    - /conditional termination/
    - /infinite sequences/
- /autoresponding with scripts or chatbots/
- /style and layout/

## The Apps

- [Survey](survey): a traditional survey with some enhancements in styles and input widgets
    - a hidden field to record local time
    - horizontal choices scale
    - form fields defined by a session condition
    - conditional fields for answer choices like 'other' / 'specify'
- [Quiz](quiz): trials of questions with multiple options of answers
    - the questions and options are sampled from a data file
- [Trials 1](trials1): simple trials with text/numeric input
    - tasks are geneated on the fly according to configuration/condition
    - multiple retries (in practice round)
- [Trials 2](trials2): trials with choices
    - tasks and choices are geneated on the fly according to session condition
- [Trials 3](trials3): trials with 2 stages and different answering methods
    - decision stage to choose method of answering
    - answering stage with either text input or option selection
- [Lottery 1](lottery1): lottery with cards-like buttons with different outcomes
    - outcomes of the cards are resolved according to distribution configuration/condition
    - configurable labels of the cards
    - randomized layout of the cards
    - different feedback/reveal conditions
- [Lottery 2s](lottery2s): lottery with sampling phase
    - multiple responses in sampling phase + last final response
- [Ultimatum 2](ultimatum2): classic 2-player game of ultimatum, with pre-recruiting of participants
    - assuming the participants are all well-known and won't drop out (a case like a controlled lab environment)
    - participants are grouped on session initialization
- [Ultimatum 1b](ultimatum1b): a single-player version, with automated partner
    - role of the only participant is pre-configured or selected at random
    - another role is played automatically by an auto-responing script
- [Ultimatum 2t](ultimatum2t): a 2-player game, with online recruiting of participants
    - assuming the participants may drop out of the game
    - participants are grouped on arrival with roles assigned dynamically
    - when a participant drops out, the game round is terminated (and the session continues with remaining player)
- [Ultimatum 2b](ultimatum2b): a 2-player game, with bot replacment
    - when one of participants drops out, the game round continues with auto-responding script
- [Ultimatum 3](ultimatum3): a 2-player game, with chaotic recruiting of participants
    - assuming the participants may drop out from instruction pages, refuse a consent, or fail comprehension check
    - participants are first run individually through a separate screener app
    - the screener pre-assigns game roles to minimize waiting time of those who already passed
    - when a participant drops out in screener, it does not affect the rest
    - when a participant drops out during main game, the game round is terminated (and the session continues with remaining player)
- [Async Party](party3async): multiplayer chat-like trials with asyncronous responses
    - players respond in random order
    - they observe partners' responses immediately
- [Parallel Party](party3parallel): the party game with parallel responses
    - players respond in random order
    - but they only observe partners' responses after all responded
- [Serial Party](party3serial): the party game with serial responding
    - players respond in turns by their group membership
    - they observe partners' responses as they're given
- [Sequential Party](party3sequential): the party game with sequential responding
    - players respond in turns following a custom sequence
    - it may contain multiple turns for the same role
    - they observe partners' responses as they're given
    - later responses of the same player override former
- Sliders: TODO

### Common fatures

Most of the apps have many common fatures:

:bangbang: TODO

- /session config conditions/
- /practice and main rounds/
- /page reloading/
- /anti-cheating/
- /multiplayer pending/

## Usage

:bangbang: TODO

- /installing/
- /integrating/

## Coding

:bangbang: TODO
