from agent_files.central_agent import evaluate_essay
from agent_files.agent_states import InputState
import unittest
import pydantic

class TestEssaySubmission(unittest.TestCase):
    
    #Setup tests with basic input data
    def setUp(self):
        self.input_data = {"essay":"The answer to the meaning of life is 42. But I'm no expert on this.","question":"What is the meaning of life?","track_id":"test track","essay_type":2,"target_band":5,"image_url":"test_url"}
        return super().setUp()
    
    #Test for invalid target band
    def test_invalid_target_band(self):
        self.input_data['target_band'] = 0 #Below minimum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['target_band'] = 10 #Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['target_band'] = 'one' #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['target_band'] = 2.5 #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    #Test for invalid essay type
    def test_invalid_essay_type(self):
        self.input_data['essay_type'] = 0 #Below minimum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['essay_type'] = 5 #Above Maximum
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['essay_type'] = 'two' #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['essay_type'] = 2.5 #Not an integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    #Test for no trackID
    def test_invalid_track_ID(self):
        self.input_data['track_id'] = None #Missing TrackID
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['track_id'] = 5 #Not a String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['track_id'] = '' #Empty String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    #Test for no question
    def test_invalid_question(self):
        self.input_data['question'] = None #Missing question
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['question'] = 5 #Not a String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['question'] = '' #Empty String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))

    #Test for no essay
    def test_invalid_essay_answer(self):
        self.input_data['essay'] = None #Missing essay
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['essay'] = 5 #Not a String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
        self.input_data['essay'] = '' #Empty String
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
    
    #Tests to see if submitting a valid essay submission returns valid output data (no image)
    def test_valid_output_format(self):
        out = evaluate_essay(InputState(**self.input_data))
        self.assertIsInstance(out,dict)
        self.assertEqual(len(out),11)
        self.assertIn("track_id",out)
        self.assertIn("grammar_score",out)
        self.assertIn("grammar_comment",out)
        self.assertIn("coherence_score",out)
        self.assertIn("coherence_comment",out)
        self.assertIn("task_score",out)
        self.assertIn("task_comment",out)
        self.assertIn("lexical_score",out)
        self.assertIn("lexical_comment",out)
        self.assertIn("overall_feedback",out)
        self.assertIn("image_description",out)
        self.assertIsInstance(out['track_id'],str)
        self.assertIsInstance(out['grammar_score'],int)
        self.assertIsInstance(out['grammar_comment'],str)
        self.assertIsInstance(out['coherence_score'],int)
        self.assertIsInstance(out['coherence_comment'],str)
        self.assertIsInstance(out['task_score'],int)
        self.assertIsInstance(out['task_comment'],str)
        self.assertIsInstance(out['lexical_score'],int)
        self.assertIsInstance(out['lexical_comment'],str)
        self.assertIsInstance(out['overall_feedback'],str)

        
    #Test for no image url
    def test_image_url(self):
        self.input_data['image_url'] = None #Missing url (optional is valid)
        evaluate_essay(InputState(**self.input_data))
        self.assertTrue(True) #Dummy assert to pass if no exception raised
        self.input_data['image_url'] = 0 #Invalid integer
        with self.assertRaises(pydantic.ValidationError):
            evaluate_essay(InputState(**self.input_data))
            
    #Test for valid output if image url exists
    def test_valid_output_format_image(self):
        self.input_data['image_url'] = 'https://www.oxfordonlineenglish.com/wp-content/uploads/2020/03/IELTS-Writing-Task-1-Academic-for-quiz-graphic-e1584609098154.jpg'
        self.input_data['image_description'] = None
        out = evaluate_essay(InputState(**self.input_data))
        self.assertIsInstance(out,dict)
        self.assertEqual(len(out),11)
        self.assertIn("track_id",out)
        self.assertIn("grammar_score",out)
        self.assertIn("grammar_comment",out)
        self.assertIn("coherence_score",out)
        self.assertIn("coherence_comment",out)
        self.assertIn("task_score",out)
        self.assertIn("task_comment",out)
        self.assertIn("lexical_score",out)
        self.assertIn("lexical_comment",out)
        self.assertIn("overall_feedback",out)
        self.assertIn("image_description",out)
        self.assertIsInstance(out['image_description'],str)
        
    #Test image description returned if exists
    def test_image_desc_return(self):
        self.input_data['image_url'] = 'https://www.oxfordonlineenglish.com/wp-content/uploads/2020/03/IELTS-Writing-Task-1-Academic-for-quiz-graphic-e1584609098154.jpg'
        desc = "This description should pass through, regardless of the image"
        self.input_data['image_description'] = desc
        out = evaluate_essay(InputState(**self.input_data))
        self.assertTrue(out['image_description'],desc)

    #Test image description returned if exists
    def test_image_desc_return2(self):
        self.input_data['image_url'] = 'https://elapro2.coderiverstudio.net/wp-content/uploads/2025/09/Sugar-levels.webp'
        desc = ""
        self.input_data['image_description'] = desc
        out = evaluate_essay(InputState(**self.input_data))
        print(out['image_description'])
        self.assertIsInstance(out['image_description'],str)

     

