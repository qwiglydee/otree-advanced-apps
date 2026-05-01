An example of lottery-like game of choices

- Task: deciding which choice is most profitable
- Input: selecting a desird card
- Result: an outcome calculated for the selected card
- Feedback:
    - outcome of all the cards
    - resulting score
- Conditions: different parameters for outcome distribution

Trial scenario:

- cards are displayed in 'closed' state with some labels on them
- player selects desired card
- the choice get evaluated and outcome calculated
- feedback provided, turning cards into 'open' state
- scenario advances to next trial
    - [practice round] when players press 'continue'
    - [in main round] after some delay
