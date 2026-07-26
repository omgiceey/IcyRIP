import unittest
from unittest.mock import patch

from core import utils


class PatchStateTests(unittest.TestCase):
    def test_does_not_skip_when_patch_not_marked(self):
        cfg = {"applied_patches": []}
        self.assertFalse(utils.should_skip_patch_alert("2.1.1", "patch-2.1.1", cfg))

    def test_skips_when_patch_marked(self):
        cfg = {"applied_patches": ["patch-2.1.1"]}
        self.assertTrue(utils.should_skip_patch_alert("2.1.1", "patch-2.1.1", cfg))

    @patch("core.config.save_config", return_value=True)
    def test_mark_patch_saves_tag_to_config(self, _save_config):
        cfg = {"applied_patches": []}
        updated = utils.mark_patch_as_applied("patch-2.1.1", cfg)
        self.assertEqual(updated["applied_patches"], ["patch-2.1.1"])


if __name__ == "__main__":
    unittest.main()
