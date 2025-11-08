from agent_files.helper_functions import calculate_overall_band
import unittest


import unittest
import math


class TestCalculateOverallBand(unittest.TestCase):
    """Test suite for calculate_overall_band function."""

    # Valid inputs - normal cases
    def test_all_same_score(self):
        """Test when all band scores are identical."""
        self.assertEqual(calculate_overall_band([7, 7, 7, 7]), 7.0)
        self.assertEqual(calculate_overall_band([5, 5, 5, 5]), 5.0)
        self.assertEqual(calculate_overall_band([9, 9, 9, 9]), 9.0)

    def test_average_whole_number(self):
        """Test when average is a whole number."""
        self.assertEqual(calculate_overall_band([6, 7, 7, 8]), 7.0)
        self.assertEqual(calculate_overall_band([5, 6, 6, 7]), 6.0)

    def test_rounding_down_to_half(self):
        """Test rounding down to nearest 0.5."""
        # Average 6.25 should round down to 6.0
        self.assertEqual(calculate_overall_band([6, 6, 6, 7]), 6.0)
        # Average 7.25 should round down to 7.0
        self.assertEqual(calculate_overall_band([7, 7, 7, 8]), 7.0)

    def test_rounding_down_to_next_half(self):
        """Test rounding down to nearest 0.5 when closer to next half."""
        # Average 6.75 should round down to 6.5
        self.assertEqual(calculate_overall_band([6, 7, 7, 7]), 6.5)
        # Average 7.75 should round down to 7.5
        self.assertEqual(calculate_overall_band([7, 8, 8, 8]), 7.5)

    def test_exact_half_scores(self):
        """Test when average is exactly a half score."""
        # Average 6.5
        self.assertEqual(calculate_overall_band([6, 6, 7, 7]), 6.5)
        # Average 7.5
        self.assertEqual(calculate_overall_band([7, 7, 8, 8]), 7.5)

    # Boundary cases
    def test_minimum_valid_scores(self):
        """Test with minimum valid scores (all zeros)."""
        self.assertEqual(calculate_overall_band([0, 0, 0, 0]), 0.0)

    def test_maximum_valid_scores(self):
        """Test with maximum valid scores (all nines)."""
        self.assertEqual(calculate_overall_band([9, 9, 9, 9]), 9.0)

    def test_mixed_min_max_scores(self):
        """Test with mixture of minimum and maximum scores."""
        # Average 4.5
        self.assertEqual(calculate_overall_band([0, 0, 9, 9]), 4.5)
        # Average 6.75 -> 6.5
        self.assertEqual(calculate_overall_band([0, 9, 9, 9]), 6.5)

    def test_single_low_score(self):
        """Test with one low score dragging down average."""
        # Average 6.75 -> 6.5
        self.assertEqual(calculate_overall_band([4, 8, 8, 8]), 7.0)
        # Average 5.25 -> 5.0
        self.assertEqual(calculate_overall_band([2, 6, 6, 7]), 5.0)

    # Edge cases for rounding
    def test_rounding_precision(self):
        """Test various rounding scenarios."""
        # Average 5.5
        self.assertEqual(calculate_overall_band([5, 5, 6, 6]), 5.5)
        # Average 8.5
        self.assertEqual(calculate_overall_band([8, 8, 9, 9]), 8.5)
        # Average 4.0
        self.assertEqual(calculate_overall_band([3, 4, 4, 5]), 4.0)

    # Invalid input - wrong number of scores
    def test_too_few_scores(self):
        """Test with fewer than 4 scores."""
        with self.assertRaises(ValueError) as context:
            calculate_overall_band([7, 8, 9])
        self.assertEqual(
            str(context.exception), "4 band scores required to calculate overall score"
        )

    def test_too_many_scores(self):
        """Test with more than 4 scores."""
        with self.assertRaises(ValueError) as context:
            calculate_overall_band([7, 8, 9, 8, 7])
        self.assertEqual(
            str(context.exception), "4 band scores required to calculate overall score"
        )

    def test_empty_list(self):
        """Test with empty list."""
        with self.assertRaises(ValueError) as context:
            calculate_overall_band([])
        self.assertEqual(
            str(context.exception), "4 band scores required to calculate overall score"
        )

    def test_single_score(self):
        """Test with only one score."""
        with self.assertRaises(ValueError) as context:
            calculate_overall_band([7])
        self.assertEqual(
            str(context.exception), "4 band scores required to calculate overall score"
        )

    # Invalid input - out of range scores
    def test_negative_score(self):
        """Test with negative score."""
        with self.assertRaises(ValueError) as context:
            calculate_overall_band([-1, 7, 8, 9])
        self.assertEqual(
            str(context.exception),
            "Individual band scores must be an integer between 0 and 9",
        )

    def test_score_above_maximum(self):
        """Test with score above 9."""
        with self.assertRaises(ValueError) as context:
            calculate_overall_band([7, 8, 9, 10])
        self.assertEqual(
            str(context.exception),
            "Individual band scores must be an integer between 0 and 9",
        )

    # All valid score combinations (comprehensive)
    def test_various_valid_combinations(self):
        """Test various valid score combinations."""
        test_cases = [
            ([0, 1, 2, 3], 1.5),  # Average 1.5
            ([1, 2, 3, 4], 2.5),  # Average 2.5
            ([2, 3, 4, 5], 3.5),  # Average 3.5
            ([3, 4, 5, 6], 4.5),  # Average 4.5
            ([4, 5, 6, 7], 5.5),  # Average 5.5
            ([5, 6, 7, 8], 6.5),  # Average 6.5
            ([6, 7, 8, 9], 7.5),  # Average 7.5
            ([1, 1, 1, 2], 1.0),  # Average 1.25 -> 1.0
            ([8, 9, 9, 9], 8.5),  # Average 8.75 -> 8.5
        ]
        for scores, expected in test_cases:
            with self.subTest(scores=scores):
                self.assertEqual(calculate_overall_band(scores), expected)
