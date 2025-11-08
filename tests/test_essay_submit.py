from agent_files.central_agent import evaluate_essay
from agent_files.agent_states import InputState
import unittest
import pydantic
import os


class TestEssaySubmission(unittest.TestCase):

    # Setup tests with basic input data
    def setUp(self):
        os.environ["LANGSMITH_TRACING_V2"] = "false"
        self.input_data = {
            "essay": "The answer to the meaning of life is 42. But I'm no expert on this.",
            "question": "What is the meaning of life?",
            "track_id": "test track",
            "essay_type": 2,
            "target_band": 5,
            "image_url": "test_url",
        }
        return super().setUp()

    # Test for invalid target band
    def test_invalid_target_band(self):
        self.input_data["target_band"] = 0  # Below minimum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["target_band"] = 10  # Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["target_band"] = "one"  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["target_band"] = 2.5  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    # Test for invalid essay type
    def test_invalid_essay_type(self):
        self.input_data["essay_type"] = 0  # Below minimum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["essay_type"] = 5  # Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["essay_type"] = "two"  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["essay_type"] = 2.5  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    # Test for no trackID
    def test_invalid_track_ID(self):
        self.input_data["track_id"] = None  # Missing TrackID
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["track_id"] = 5  # Not a String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["track_id"] = ""  # Empty String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    # Test for no question
    def test_invalid_question(self):
        self.input_data["question"] = None  # Missing question
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["question"] = 5  # Not a String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["question"] = ""  # Empty String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    # Test for no essay
    def test_invalid_essay_answer(self):
        self.input_data["essay"] = None  # Missing essay
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["essay"] = 5  # Not a String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data["essay"] = ""  # Empty String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    # Test for no image url
    def test_image_url(self):
        self.input_data["image_url"] = 0  # Invalid integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
