# tests/test_ai_service.py
import unittest
from ai_service import AISummarizer

class TestAISummarizer(unittest.TestCase):
    def test_summarize(self):
        summarizer = AISummarizer(api_key="test-key")
        summary = summarizer.summarize("Sample text")
        self.assertIsInstance(summary, str)

if __name__ == "__main__":
    unittest.main()
