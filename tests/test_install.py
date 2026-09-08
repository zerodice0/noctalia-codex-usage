from pathlib import Path
import sys
import unittest
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from install import shortcut_config, TOGGLE


class ShortcutTests(unittest.TestCase):
    def test_comments_and_other_shortcuts_survive_install_and_uninstall(self):
        original = '# Personal config\n[keybinds]\n"Mod+D" = "existing" # Keep this\n\n[general]\nmod_key = "Super"\n'
        installed = shortcut_config(original, "Mod+Shift+U")
        self.assertIn('"Mod+D" = "existing" # Keep this', installed)
        self.assertEqual(tomllib.loads(installed)["keybinds"]["Mod+Shift+U"]["action"], "spawn:" + TOGGLE)
        self.assertEqual(shortcut_config(installed, "Mod+Shift+U"), installed)
        self.assertEqual(shortcut_config(installed, "Mod+Shift+U", remove=True), original)

    def test_conflicting_shortcut_is_not_overwritten(self):
        with self.assertRaises(ValueError):
            shortcut_config('[keybinds]\n"Mod+Shift+U" = "other"\n', "Mod+Shift+U")

    def test_missing_section_and_missing_final_newline(self):
        for original in ('[general]\nmod_key = "Super"', '[keybinds]'):
            self.assertIn("Mod+Shift+U", tomllib.loads(shortcut_config(original, "Mod+Shift+U"))["keybinds"])


if __name__ == "__main__":
    unittest.main()
