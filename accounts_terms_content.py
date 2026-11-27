import hashlib
import os
from pathlib import Path

def verified_content(metadata):
    path=os.environ.get("ESTOA_TERMS_DOCUMENT_PATH")
    if not path:
        raise ValueError("Terms content unavailable")
    try:
        with Path(path).open("rb") as stream:
            raw=stream.read(262145)
        if not raw or len(raw)>262144 or hashlib.sha256(raw).hexdigest()!=metadata["content_sha256"]:
            raise ValueError("Terms content unavailable")
        return raw.decode("utf-8")
    except (OSError,UnicodeError):
        raise ValueError("Terms content unavailable") from None
