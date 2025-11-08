from agent_files.grammar_agent import grammar_agent
from agent_files.agent_states import InputState
import unittest
import pydantic

class TestGrammar(unittest.TestCase):
    
    #Setup tests with basic input data
    def setUp(self):
        self.input_data = {"essay":"The answer to the meaning of life is 42. But I'm no expert on this.","question":"What is the meaning of life?","track_id":"test track","essay_type":2,"target_band":5,"image_url":"test_url"}
        return super().setUp()
    
    #Test for invalid target band
    def test_invalid_target_band(self):
        self.input_data['target_band'] = 0 #Below minimum
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['target_band'] = 10 #Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['target_band'] = 'one' #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['target_band'] = 2.5 #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))

    #Test for invalid essay type
    def test_invalid_essay_type(self):
        self.input_data['essay_type'] = 0 #Below minimum
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['essay_type'] = 5 #Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['essay_type'] = 'two' #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['essay_type'] = 2.5 #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))

    #Test for no trackID
    def test_invalid_track_ID(self):
        self.input_data['track_id'] = None #Missing TrackID
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['track_id'] = 5 #Not a String
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['track_id'] = '' #Empty String
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))

    #Test for no question
    def test_invalid_question(self):
        self.input_data['question'] = None #Missing question
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['question'] = 5 #Not a String
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['question'] = '' #Empty String
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))

    #Test for no essay
    def test_invalid_essay_answer(self):
        self.input_data['essay'] = None #Missing essay
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['essay'] = 5 #Not a String
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
        self.input_data['essay'] = '' #Empty String
        with self.assertRaises(pydantic.ValidationError):
            grammar_agent(InputState(**self.input_data))
    
    #Tests to see if submitting a valid essay submission returns valid output data
    def test_valid_output_format(self):
        out = grammar_agent(InputState(**self.input_data))
        self.assertIsInstance(out,dict)
        self.assertEqual(len(out),2)
        self.assertIn("grammar_score",out)
        self.assertIn("grammar_comment",out)
        self.assertIsInstance(out['grammar_score'],int)
        self.assertIsInstance(out['grammar_comment'],str)


    #Tests if a word count of 20 or fewer words returns a score of 1 or lower
    def test_word_count(self):
        self.input_data['essay'] = "The meaning of life is about how many words I can write in an essay. This is now 20 words."
        out = grammar_agent(InputState(**self.input_data))
        self.assertLessEqual(out['grammar_score'],1,f"Band score of {out['grammar_score']} exceeds 1 when word count not reached")


