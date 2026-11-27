import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from accounts_terms_content import verified_content

class TermsContentTests(unittest.TestCase):
    def test_exact_bytes(self):
        raw="Condiciones de prueba\n".encode("utf-8")
        metadata={"content_sha256":hashlib.sha256(raw).hexdigest()}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"terms.txt"
            path.write_bytes(raw)
            with patch.dict("os.environ",{"ESTOA_TERMS_DOCUMENT_PATH":str(path)}):
                self.assertEqual(verified_content(metadata),raw.decode("utf-8"))
                path.write_bytes(raw+b" ")
                with self.assertRaises(ValueError):
                    verified_content(metadata)
                path.unlink()
                with self.assertRaises(ValueError):
                    verified_content(metadata)
    def test_missing_configuration(self):
        with patch.dict("os.environ",{"ESTOA_TERMS_DOCUMENT_PATH":""}):
            with self.assertRaises(ValueError):
                verified_content({"content_sha256":"a"*64})
