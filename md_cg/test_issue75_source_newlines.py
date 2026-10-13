"""The source contract must work on LF/CRLF and still reject a lost decorator."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from . import test_issue75_neural_failure as guard


class SourceNewlines(unittest.TestCase):
    def test_line_endings_and_negative_control(self):
        source = Path(guard._TARGET).read_text(encoding='utf8')
        anchor = '@staticmethod\n    def _cosine(a, b):'
        self.assertEqual(source.count(anchor), 1)
        with tempfile.TemporaryDirectory(prefix='issue75-newlines-') as tmp:
            target = Path(tmp) / 'source.py'
            for ending in ('\n', '\r\n'):
                with self.subTest(ending=repr(ending)):
                    target.write_bytes(source.replace('\n', ending).encode('utf8'))
                    with patch.object(guard, '_TARGET', str(target)):
                        self.assertTrue(guard.a11()[0], guard.a11()[1])
            target.write_text(source.replace(anchor, 'def _cosine(a, b):'), encoding='utf8')
            with patch.object(guard, '_TARGET', str(target)):
                passed, reason = guard.a11()
                self.assertFalse(passed)
                self.assertIn('cosine 保持 staticmethod', reason)


if __name__ == '__main__':
    unittest.main()
