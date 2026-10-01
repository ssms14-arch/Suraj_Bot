import os
import subprocess
import sys
import unittest
from pathlib import Path

from config import REQUIRED_ENV_VARS, _require_environment


class ConfigurationTests(unittest.TestCase):
    def test_local_environment_provides_required_settings(self):
        values = _require_environment(os.environ)

        self.assertEqual(set(values), set(REQUIRED_ENV_VARS))
        self.assertFalse(any(not value for value in values.values()))

    def test_missing_settings_raise_names_only(self):
        with self.assertRaises(RuntimeError) as raised:
            _require_environment({})

        message = str(raised.exception)
        self.assertIn("Missing required environment variables", message)
        self.assertTrue(all(name in message for name in REQUIRED_ENV_VARS))
        self.assertNotIn("sk-", message)

    def test_config_import_fails_when_required_environment_is_empty(self):
        environment = os.environ.copy()
        for name in REQUIRED_ENV_VARS:
            environment[name] = ""

        result = subprocess.run(
            [sys.executable, "-c", "import config"],
            cwd=Path(__file__).resolve().parent,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required environment variables", result.stderr)
        self.assertTrue(all(name in result.stderr for name in REQUIRED_ENV_VARS))
        self.assertNotIn("sk-", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()