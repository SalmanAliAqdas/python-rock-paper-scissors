"""Automated tests. Run with:  python -m unittest -v"""

import random
import unittest

import rps


def scripted(answers):
    iterator = iter(answers)
    return lambda prompt="": next(iterator)


class RuleTests(unittest.TestCase):
    def test_every_move_beats_exactly_half_of_the_others(self):
        for mode in rps.RULES:
            moves = rps.moves_for(mode)
            for move in moves:
                self.assertEqual(len(rps.RULES[mode][move]), (len(moves) - 1) // 2, (mode, move))

    def test_no_two_moves_beat_each_other(self):
        for mode in rps.RULES:
            for a in rps.moves_for(mode):
                for b in rps.moves_for(mode):
                    self.assertFalse(rps.beats(a, b, mode) and rps.beats(b, a, mode))

    def test_every_pair_has_exactly_one_winner(self):
        for mode in rps.RULES:
            moves = rps.moves_for(mode)
            for a in moves:
                for b in moves:
                    if a != b:
                        self.assertNotEqual(rps.beats(a, b, mode), rps.beats(b, a, mode))

    def test_classic_results(self):
        self.assertEqual(rps.decide("rock", "scissors", "classic")[0], "player")
        self.assertEqual(rps.decide("rock", "paper", "classic")[0], "computer")
        self.assertEqual(rps.decide("paper", "paper", "classic")[0], "tie")
        self.assertEqual(rps.decide("scissors", "paper", "classic")[1], "Scissors cuts paper.")

    def test_extended_results(self):
        self.assertEqual(rps.decide("spock", "rock", "extended")[1], "Spock vaporizes rock.")
        self.assertEqual(rps.decide("lizard", "spock", "extended")[0], "player")
        self.assertEqual(rps.decide("rock", "spock", "extended")[0], "computer")

    def test_extended_moves_are_not_in_classic(self):
        self.assertNotIn("lizard", rps.moves_for("classic"))


class ParseTests(unittest.TestCase):
    def test_accepted_forms(self):
        self.assertEqual(rps.parse_move("Rock", "classic"), "rock")
        self.assertEqual(rps.parse_move(" p ", "classic"), "paper")
        self.assertEqual(rps.parse_move("3", "classic"), "scissors")
        self.assertEqual(rps.parse_move("k", "extended"), "spock")
        self.assertEqual(rps.parse_move("l", "extended"), "lizard")
        self.assertEqual(rps.parse_move("5", "extended"), "spock")

    def test_rejected_forms(self):
        for bad in ["", "banana", "0", "4", "l", "k"]:
            with self.assertRaises(rps.MoveError, msg=bad):
                rps.parse_move(bad, "classic")
        with self.assertRaises(rps.MoveError):
            rps.parse_move("6", "extended")


class ComputerTests(unittest.TestCase):
    def test_random_uses_valid_moves_and_all_of_them(self):
        rng = random.Random(1)
        seen = {rps.computer_move([], "extended", "random", rng) for _ in range(300)}
        self.assertEqual(seen, set(rps.moves_for("extended")))

    def test_smart_first_round_is_valid(self):
        self.assertIn(rps.computer_move([], "classic", "smart", random.Random(2)), rps.moves_for("classic"))

    def test_smart_counters_favourite_move(self):
        rng = random.Random(3)
        self.assertEqual(rps.computer_move(["rock"] * 5, "classic", "smart", rng), "paper")
        for _ in range(50):
            move = rps.computer_move(["lizard"] * 3 + ["rock"], "extended", "smart", rng)
            self.assertTrue(rps.beats(move, "lizard", "extended"))

    def test_smart_beats_a_predictable_player(self):
        rng = random.Random(4)
        history, computer_wins, player_wins = [], 0, 0
        for _ in range(40):
            computer = rps.computer_move(history, "classic", "smart", rng)
            history.append("rock")
            winner = rps.decide("rock", computer, "classic")[0]
            computer_wins += winner == "computer"
            player_wins += winner == "player"
        self.assertEqual(player_wins, 0)
        self.assertGreaterEqual(computer_wins, 38)


class MatchTests(unittest.TestCase):
    def run_match(self, answers, mode="classic", strategy="random", wins=2, seed=0):
        output = []
        result = rps.play_match(mode, strategy, wins, random.Random(seed), scripted(answers), output.append)
        return result, "\n".join(output)

    def test_match_ends_when_someone_reaches_target(self):
        # always play rock until the match ends; it must end with someone on 2 wins
        result, text = self.run_match(["rock"] * 60)
        self.assertIn(2, result["score"].values())
        self.assertIn(result["outcome"], ("player", "computer"))
        self.assertLess(max(result["score"].values()), 3)

    def test_ties_do_not_count_as_wins(self):
        result, _ = self.run_match(["rock"] * 60)
        self.assertEqual(result["rounds"], sum(result["score"].values()) + result["ties"])

    def test_invalid_input_does_not_count_as_a_round(self):
        result, text = self.run_match(["banana", "", "99"] + ["rock"] * 60)
        self.assertEqual(text.count("did not count"), 3)
        self.assertEqual(result["rounds"], sum(result["score"].values()) + result["ties"])

    def test_quit(self):
        result, text = self.run_match(["q"])
        self.assertEqual(result["outcome"], "quit")
        self.assertEqual(result["rounds"], 0)

    def test_player_can_win_and_lose_across_seeds(self):
        outcomes = {self.run_match(["rock"] * 80, seed=s)[0]["outcome"] for s in range(30)}
        self.assertEqual(outcomes, {"player", "computer"})

    def test_smart_opponent_beats_always_rock_player(self):
        wins = sum(self.run_match(["rock"] * 80, strategy="smart", wins=3, seed=s)[0]["outcome"] == "computer"
                   for s in range(40))
        self.assertGreaterEqual(wins, 35)

    def test_extended_match_runs(self):
        result, _ = self.run_match(["k", "l", "r", "p", "s"] * 30, mode="extended", wins=3)
        self.assertIn(result["outcome"], ("player", "computer"))


class StatsTests(unittest.TestCase):
    def test_stats(self):
        stats = rps.new_stats()
        rps.update_stats(stats, {"outcome": "player", "score": {"player": 2, "computer": 1}, "ties": 1})
        rps.update_stats(stats, {"outcome": "computer", "score": {"player": 0, "computer": 2}, "ties": 0})
        rps.update_stats(stats, {"outcome": "quit", "score": {"player": 1, "computer": 0}, "ties": 0})
        self.assertEqual(stats, {"matches_won": 1, "matches_lost": 1, "rounds_won": 2,
                                 "rounds_lost": 3, "ties": 1})
        self.assertIn("won 1, lost 1", rps.format_stats(stats))

    def test_empty_stats(self):
        self.assertEqual(rps.format_stats(rps.new_stats()), "No finished matches yet.")


class SettingsTests(unittest.TestCase):
    def test_change_settings(self):
        settings = {}
        rps.change_settings(settings, scripted(["2", "2", "3"]), lambda text: None)
        self.assertEqual(settings, {"mode": "extended", "strategy": "smart", "wins_needed": 3})

    def test_bad_setting_input_asks_again(self):
        settings = {}
        rps.change_settings(settings, scripted(["x", "1", "9", "1", "", "2"]), lambda text: None)
        self.assertEqual(settings, {"mode": "classic", "strategy": "random", "wins_needed": 2})


if __name__ == "__main__":
    unittest.main()
