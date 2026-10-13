# Rock Paper Scissors

A command-line Rock Paper Scissors game written in Python. Play first-to-N-wins matches against the computer, in classic mode or in the extended mode with Lizard and Spock.

## Features
- **Two game modes:** Classic (rock, paper, scissors) and Extended (adds lizard and Spock)
- **Two computer opponents:**
  - Random: picks any move
  - Smart: learns which move you use most and plays something that beats it
- **Matches:** first to 1, 2 or 3 round wins
- Ties never count as wins
- Invalid input never counts as a round
- Round descriptions such as "Paper covers rock." and "Spock vaporizes rock."
- Statistics for matches and rounds
- Type a full move name, a shortcut letter, or a menu number
- Automated tests (23), including a check that the rules are fair and balanced

## Requirements
- Python 3 installed
- No extra packages needed

## How to run
```
python rps.py
```
If `python` is not recognized on Windows, use `py rps.py`.

## How to play
From the main menu:
1. **Play a match**
2. **Change settings** (mode, opponent, match length)
3. **Statistics**
q. **Quit**

During a match, type a move and press Enter:

| Classic | Extended adds |
|---|---|
| `rock` or `r` | `lizard` or `l` |
| `paper` or `p` | `spock` or `k` |
| `scissors` or `s` | |

You can also type the move's number (1 to 3 in classic, 1 to 5 in extended). Type `q` to leave a match.

Example round:
```
Classic mode, random opponent. First to 2 win(s).
Moves: r=rock  p=paper  s=scissors   (type 'q' to leave the match)

Your move: rock
You: rock   Computer: scissors
Rock crushes scissors. You win this round.
Score: You 1 - 0 Computer
```

## Rules
Classic: rock crushes scissors, scissors cut paper, paper covers rock.

Extended adds: rock crushes lizard, lizard poisons Spock, Spock smashes scissors, scissors decapitate lizard, lizard eats paper, paper disproves Spock, Spock vaporizes rock.

## Tip
The smart opponent counts your moves. If you always play the same move, it will beat you. To win, mix up your moves unpredictably.

## Running the tests
```
python -m unittest -v
```

## How it works
- A dictionary describes who beats whom (`RULES`), so adding a new mode only needs a new dictionary entry
- `decide` compares two moves, `computer_move` picks the computer's choice, and `play_match` runs a whole match
- Game logic is separate from keyboard input, so it can be tested automatically

## Project structure
- `rps.py`: the game
- `test_rps.py`: automated tests
- `.gitignore`: files Git should ignore
- `readme.md`: this file

## Possible future improvements
- Save statistics to a file
- Show a history of rounds
- A graphical or web version
