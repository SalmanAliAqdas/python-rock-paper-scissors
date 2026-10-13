"""Rock Paper Scissors against the computer.

Two game modes (classic and extended with Lizard and Spock), two computer
opponents (random and smart), and first-to-N-wins matches.
"""

import random

# winner -> {loser: verb}
RULES = {
    "classic": {
        "rock": {"scissors": "crushes"},
        "paper": {"rock": "covers"},
        "scissors": {"paper": "cuts"},
    },
    "extended": {
        "rock": {"scissors": "crushes", "lizard": "crushes"},
        "paper": {"rock": "covers", "spock": "disproves"},
        "scissors": {"paper": "cuts", "lizard": "decapitates"},
        "lizard": {"spock": "poisons", "paper": "eats"},
        "spock": {"scissors": "smashes", "rock": "vaporizes"},
    },
}

SHORTCUTS = {
    "classic": {"r": "rock", "p": "paper", "s": "scissors"},
    "extended": {"r": "rock", "p": "paper", "s": "scissors", "l": "lizard", "k": "spock"},
}

STRATEGIES = {"1": "random", "2": "smart"}
MODES = {"1": "classic", "2": "extended"}
MATCH_LENGTHS = {"1": 1, "2": 2, "3": 3}   # first to this many round wins


class MoveError(Exception):
    """Input that is not a valid move (it does not count as a round)."""


# ---------- Game rules (pure functions, easy to test) ----------

def moves_for(mode):
    return list(RULES[mode])


def beats(move_a, move_b, mode):
    return move_b in RULES[mode][move_a]


def decide(player, computer, mode):
    """Return ('player' | 'computer' | 'tie', sentence describing the round)."""
    if player == computer:
        return "tie", f"Both chose {player}."
    if beats(player, computer, mode):
        verb = RULES[mode][player][computer]
        return "player", f"{player.capitalize()} {verb} {computer}."
    verb = RULES[mode][computer][player]
    return "computer", f"{computer.capitalize()} {verb} {player}."


def parse_move(text, mode):
    """Accept a full name, a shortcut letter, or a menu number."""
    text = text.strip().lower()
    moves = moves_for(mode)
    if text in moves:
        return text
    if text in SHORTCUTS[mode]:
        return SHORTCUTS[mode][text]
    if text.isdigit() and 1 <= int(text) <= len(moves):
        return moves[int(text) - 1]
    names = ", ".join(f"{m} ({k})" for k, m in SHORTCUTS[mode].items())
    raise MoveError(f"Please choose one of: {names}")


def computer_move(history, mode, strategy, rng=random):
    """Pick the computer's move.

    random: any move.
    smart:  find the move the player uses most often and play something that beats it.
    """
    moves = moves_for(mode)
    if strategy == "smart" and history:
        counts = {move: history.count(move) for move in moves}
        top = max(counts.values())
        favourites = [move for move, count in counts.items() if count == top]
        target = rng.choice(favourites)
        counters = [move for move in moves if beats(move, target, mode)]
        return rng.choice(counters)
    return rng.choice(moves)


# ---------- One match ----------

def play_match(mode, strategy, wins_needed, rng=random, ask=input, show=print):
    """Play until someone reaches wins_needed. Returns a result dictionary."""
    score = {"player": 0, "computer": 0}
    ties = 0
    history = []        # the player's moves, used by the smart opponent
    moves = moves_for(mode)
    menu = "  ".join(f"{k}={m}" for k, m in SHORTCUTS[mode].items())

    show(f"\n{mode.capitalize()} mode, {strategy} opponent. First to {wins_needed} win(s).")
    show(f"Moves: {menu}   (type 'q' to leave the match)")

    while score["player"] < wins_needed and score["computer"] < wins_needed:
        text = ask("\nYour move: ").strip().lower()
        if text in ("q", "quit"):
            show("You left the match.")
            return {"outcome": "quit", "score": score, "ties": ties, "rounds": len(history)}

        try:
            player = parse_move(text, mode)
        except MoveError as error:
            show(f"{error} (This round did not count.)")
            continue

        computer = computer_move(history, mode, strategy, rng)
        history.append(player)
        winner, description = decide(player, computer, mode)

        show(f"You: {player}   Computer: {computer}")
        if winner == "tie":
            ties += 1
            show(f"{description} It's a tie.")
        else:
            score[winner] += 1
            show(f"{description} {'You win' if winner == 'player' else 'Computer wins'} this round.")
        show(f"Score: You {score['player']} - {score['computer']} Computer")

    outcome = "player" if score["player"] > score["computer"] else "computer"
    show("\n*** You win the match! ***" if outcome == "player" else "\n*** Computer wins the match. ***")
    return {"outcome": outcome, "score": score, "ties": ties, "rounds": len(history)}


# ---------- Statistics and menus ----------

def new_stats():
    return {"matches_won": 0, "matches_lost": 0, "rounds_won": 0, "rounds_lost": 0, "ties": 0}


def update_stats(stats, result):
    if result["outcome"] == "quit":
        return
    stats["matches_won"] += result["outcome"] == "player"
    stats["matches_lost"] += result["outcome"] == "computer"
    stats["rounds_won"] += result["score"]["player"]
    stats["rounds_lost"] += result["score"]["computer"]
    stats["ties"] += result["ties"]


def format_stats(stats):
    played = stats["matches_won"] + stats["matches_lost"]
    if played == 0:
        return "No finished matches yet."
    return (
        f"Matches: won {stats['matches_won']}, lost {stats['matches_lost']}\n"
        f"Rounds:  won {stats['rounds_won']}, lost {stats['rounds_lost']}, tied {stats['ties']}"
    )


def choose_setting(title, options, ask=input, show=print):
    """Show a numbered list and return the chosen key."""
    show(title)
    for key, label in options.items():
        show(f"  {key}. {label}")
    while True:
        choice = ask("Your choice: ").strip()
        if choice in options:
            return choice
        show("Please type one of the numbers shown.")


def change_settings(settings, ask=input, show=print):
    mode_key = choose_setting("\nGame mode:", {"1": "Classic (rock, paper, scissors)",
                                              "2": "Extended (adds lizard and Spock)"}, ask, show)
    strategy_key = choose_setting("\nComputer opponent:", {"1": "Random",
                                                           "2": "Smart (learns your habits)"}, ask, show)
    length_key = choose_setting("\nMatch length:", {"1": "First to 1 win", "2": "First to 2 wins",
                                                    "3": "First to 3 wins"}, ask, show)
    settings["mode"] = MODES[mode_key]
    settings["strategy"] = STRATEGIES[strategy_key]
    settings["wins_needed"] = MATCH_LENGTHS[length_key]


def main():
    settings = {"mode": "classic", "strategy": "random", "wins_needed": 2}
    stats = new_stats()

    while True:
        print()
        print("Rock Paper Scissors")
        print(f"  Current settings: {settings['mode']}, {settings['strategy']} opponent, "
              f"first to {settings['wins_needed']}")
        print("  1. Play a match")
        print("  2. Change settings")
        print("  3. Statistics")
        print("  q. Quit")
        choice = input("Your choice: ").strip().lower()

        if choice == "1":
            result = play_match(settings["mode"], settings["strategy"], settings["wins_needed"])
            update_stats(stats, result)
            input("\nPress Enter to go back to the menu...")
        elif choice == "2":
            change_settings(settings)
        elif choice == "3":
            print()
            print(format_stats(stats))
            input("\nPress Enter to go back to the menu...")
        elif choice in ("q", "quit", "exit"):
            print()
            print(format_stats(stats))
            print("Thanks for playing. Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3 or q.")


if __name__ == "__main__":
    main()
