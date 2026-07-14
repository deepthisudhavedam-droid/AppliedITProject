import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import services.llm as llm_module


class TestLLMEnv(unittest.TestCase):
    def test_resolve_api_key_prefers_gemini_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini-key"}, clear=True):
            self.assertEqual(llm_module.resolve_api_key(), "gemini-key")

    def test_resolve_api_key_falls_back_to_google_key(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "google-key"}, clear=True):
            self.assertEqual(llm_module.resolve_api_key(), "google-key")

    def test_resolve_api_key_reads_dotenv_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("GEMINI_API_KEY=dotenv-key\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(llm_module, "get_dotenv_path", return_value=env_path):
                    self.assertEqual(llm_module.resolve_api_key(), "dotenv-key")

    def test_resolve_model_candidates_prefers_env(self):
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-1.5-flash"}, clear=True):
            self.assertEqual(llm_module.resolve_model_candidates(), ["gemini-1.5-flash"])


if __name__ == "__main__":
    unittest.main()
