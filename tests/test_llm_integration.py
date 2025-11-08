from agent_files.lexical_agent import lexical_agent
from agent_files.agent_states import InputState
from agent_files.central_agent import evaluate_essay
import unittest
import pydantic
import os
from unittest.mock import patch


class TestLLMIntegration(unittest.TestCase):
    # Setup tests with basic input data
    @patch.dict(os.environ, {"LANGSMITH_TRACING_V2": "false"})
    def setUp(self):
        self.input_data = {
            "essay": "The answer to the meaning of life is 42. But I'm no expert on this.",
            "question": "What is the meaning of life?",
            "track_id": "test track",
            "essay_type": 2,
            "target_band": 5,
            "image_url": "test_url",
        }
        return super().setUp()

    # Test word count and valid output
    @patch.dict(os.environ, {"LANGSMITH_TRACING_V2": "false"})
    def test_word_count_valid_output(self):
        self.input_data["essay"] = (
            "The meaning of life is about how many words I can write in an essay. This is now 20 words."
        )
        self.input_data["image_url"] = None  # Missing url (optional is valid)
        out = evaluate_essay(InputState(**self.input_data))
        self.assertLessEqual(
            out["coherence_score"],
            1,
            f"Band score of {out['coherence_score']} exceeds 1 when word count not reached",
        )
        self.assertLessEqual(
            out["grammar_score"],
            1,
            f"Band score of {out['grammar_score']} exceeds 1 when word count not reached",
        )
        self.assertLessEqual(
            out["task_score"],
            1,
            f"Band score of {out['task_score']} exceeds 1 when word count not reached",
        )
        self.assertLessEqual(
            out["lexical_score"],
            1,
            f"Band score of {out['lexical_score']} exceeds 1 when word count not reached",
        )
        self.assertIsInstance(out, dict)
        self.assertEqual(len(out), 11)
        self.assertIn("track_id", out)
        self.assertIn("grammar_score", out)
        self.assertIn("grammar_comment", out)
        self.assertIn("coherence_score", out)
        self.assertIn("coherence_comment", out)
        self.assertIn("task_score", out)
        self.assertIn("task_comment", out)
        self.assertIn("lexical_score", out)
        self.assertIn("lexical_comment", out)
        self.assertIn("overall_feedback", out)
        self.assertIn("image_description", out)
        self.assertIsInstance(out["track_id"], str)
        self.assertIsInstance(out["grammar_score"], int)
        self.assertIsInstance(out["grammar_comment"], str)
        self.assertIsInstance(out["coherence_score"], int)
        self.assertIsInstance(out["coherence_comment"], str)
        self.assertIsInstance(out["task_score"], int)
        self.assertIsInstance(out["task_comment"], str)
        self.assertIsInstance(out["lexical_score"], int)
        self.assertIsInstance(out["lexical_comment"], str)
        self.assertIsInstance(out["overall_feedback"], str)

    # Test for valid output if image url exists
    @patch.dict(os.environ, {"LANGSMITH_TRACING_V2": "false"})
    def test_valid_output_format_image(self):
        self.input_data["image_url"] = (
            "https://www.oxfordonlineenglish.com/wp-content/uploads/2020/03/IELTS-Writing-Task-1-Academic-for-quiz-graphic-e1584609098154.jpg"
        )
        self.input_data["image_description"] = None
        out = evaluate_essay(InputState(**self.input_data))
        self.assertIsInstance(out, dict)
        self.assertEqual(len(out), 11)
        self.assertIn("track_id", out)
        self.assertIn("grammar_score", out)
        self.assertIn("grammar_comment", out)
        self.assertIn("coherence_score", out)
        self.assertIn("coherence_comment", out)
        self.assertIn("task_score", out)
        self.assertIn("task_comment", out)
        self.assertIn("lexical_score", out)
        self.assertIn("lexical_comment", out)
        self.assertIn("overall_feedback", out)
        self.assertIn("image_description", out)
        self.assertIsInstance(out["image_description"], str)
        self.assertGreater(len(out["image_description"]), 10)

    # Test image description returned if already exists
    @patch.dict(os.environ, {"LANGSMITH_TRACING_V2": "false"})
    def test_image_desc_return(self):
        self.input_data["image_url"] = (
            "https://www.oxfordonlineenglish.com/wp-content/uploads/2020/03/IELTS-Writing-Task-1-Academic-for-quiz-graphic-e1584609098154.jpg"
        )
        desc = "This description should pass through, regardless of the image"
        self.input_data["image_description"] = desc
        out = evaluate_essay(InputState(**self.input_data))
        self.assertTrue(out["image_description"], desc)
