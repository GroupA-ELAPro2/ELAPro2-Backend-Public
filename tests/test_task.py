from agent_files.task_agent import task_agent
import agent_files.task_agent as agent
from agent_files.agent_states import InputState
import unittest
import pydantic
import os


class TestTask(unittest.TestCase):

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
            task_agent(InputState(**self.input_data))
        self.input_data["target_band"] = 10  # Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["target_band"] = "one"  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["target_band"] = 2.5  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))

    # Test for invalid essay type
    def test_invalid_essay_type(self):
        self.input_data["essay_type"] = 0  # Below minimum
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["essay_type"] = 5  # Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["essay_type"] = "two"  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["essay_type"] = 2.5  # Not an integer
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))

    # Test for no trackID
    def test_invalid_track_ID(self):
        self.input_data["track_id"] = None  # Missing TrackID
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["track_id"] = 5  # Not a String
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["track_id"] = ""  # Empty String
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))

    # Test for no question
    def test_invalid_question(self):
        self.input_data["question"] = None  # Missing question
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["question"] = 5  # Not a String
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["question"] = ""  # Empty String
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))

    # Test for no essay
    def test_invalid_essay_answer(self):
        self.input_data["essay"] = None  # Missing essay
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["essay"] = 5  # Not a String
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))
        self.input_data["essay"] = ""  # Empty String
        with self.assertRaises(pydantic.ValidationError):
            task_agent(InputState(**self.input_data))


class testTaskImage(unittest.TestCase):
    # Setup tests with basic input data
    def setUp(self):
        os.environ["LANGSMITH_TRACING_V2"] = "false"
        self.input_data = {
            "essay": """The line graph illustrates the number of smokers per 1,000 people in Austria, divided by gender, between 1960 and 2000.

Overall, it is evident that the rate of smoking among men declined consistently over the forty-year period, while the proportion of female smokers initially rose before falling slightly towards the end. Despite these changes, men remained more likely to smoke than women throughout.

In 1960, the male smoking rate stood at around 600 per 1,000 people. This figure fell gradually to about 550 by 1970 and continued to decrease more sharply thereafter, reaching approximately 250 by the year 2000. The steepest decline occurred between 1970 and 1995.

In contrast, only about 80 women per 1,000 smoked in 1960. This number increased rapidly to nearly 200 by 1965 and peaked at just over 300 around 1975 and 1980. However, after this point the rate began to fall, dropping to about 200 per 1,000 in 2000.

In summary, although both genders experienced a reduction in smoking towards the end of the period, men showed a steady decline, whereas women’s smoking rose initially before decreasing, leading to a narrowing gap between the two groups by 2000.""",
            "question": "Write a report for the university lecturer describing the information in the graph below.\n\
You should write at least 150 words.\n\
Allow yourself 20 minutes for this task.",
            "track_id": "test track",
            "essay_type": 2,
            "target_band": 5,
            "image_url": "https://elapro2.coderiverstudio.net/wp-content/uploads/2025/09/Smokers.webp",
        }
        return super().setUp()

    def test_agent_w_image(self):
        self.input_data["image_description"] = None
        out = task_agent(InputState(**self.input_data))
        print(out["image_description"])
        self.assertEqual(len(out), 3)
        self.assertIsInstance(out["task_score"], int)
        self.assertIsInstance(out["task_comment"], str)
        self.assertIsInstance(out["image_description"], str)
