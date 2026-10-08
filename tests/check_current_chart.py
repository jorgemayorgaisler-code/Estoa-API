"""Static syntax and UI-contract smoke check for the standalone current chart."""
from pathlib import Path
import re
import subprocess
import tempfile

page = (Path(__file__).resolve().parents[1] / "prototypes/current-curve.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", page, re.DOTALL)
assert len(scripts) == 1, "Expected one inline chart script"
for required in ("current-curve?", "weak-windows?", "forecast?", "conditions/at?", "renderNextSlack", "renderTide", "renderWindows", "moment-status", "window-rows"):
    assert required in page, f"Missing chart integration: {required}"
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "current-curve.js"
    source.write_text(scripts[0], encoding="utf-8")
    subprocess.run(["node", "--check", str(source)], check=True)
print("ESTOA current chart syntax and integration contract: PASS")
