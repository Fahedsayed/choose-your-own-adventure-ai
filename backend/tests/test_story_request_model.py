import unittest

from pydantic import ValidationError

from schemas.story import CreateStoryRequest


class CreateStoryRequestTests(unittest.TestCase):
    def test_accepts_a_meaningful_theme(self):
        request = CreateStoryRequest(theme="Space adventure")

        self.assertEqual(request.theme, "Space adventure")

    def test_rejects_too_short_theme(self):
        with self.assertRaises(ValidationError):
            CreateStoryRequest(theme="  ")


if __name__ == "__main__":
    unittest.main()
