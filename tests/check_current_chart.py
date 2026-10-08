"""Static syntax and UI-contract smoke check for the standalone current chart."""
from pathlib import Path
import re
import subprocess
import tempfile
import json

page = (Path(__file__).resolve().parents[1] / "prototypes/current-curve.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", page, re.DOTALL)
assert len(scripts) == 1, "Expected one inline chart script"
for required in ("current-curve?", "weak-windows?", "forecast?", "conditions/at?", "renderNextSlack", "renderTide", "renderWindows", "moment-status", "window-rows"):
    assert required in page, f"Missing chart integration: {required}"
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "current-curve.js"
    source.write_text(scripts[0], encoding="utf-8")
    subprocess.run(["node", "--check", str(source)], check=True)
    # Execute the pure civil-time helper in Node, including invalid-date rejection.
    script = source.read_text(encoding="utf-8")
    helper = script[script.index("function civilMs("):script.index("function el(")]
    cases = [
        ("2026-10-07T18:30", "2026-10-07T19:30:00", 60),
        ("2026-10-07T23:30", "2026-10-08T00:30", 60),
    ]
    checks = "const assert=require('node:assert/strict');\n" + helper + "\n"
    for start, end, minutes in cases:
        checks += f"assert.equal((civilMs({json.dumps(end)})-civilMs({json.dumps(start)}))/60000,{minutes});\n"
    checks += "assert.ok(Number.isNaN(civilMs('2026-02-30T12:00')));\n"
    for zone in ("UTC", "America/Santiago", "Europe/Madrid"):
        subprocess.run(["node", "-e", checks], check=True, env={**__import__("os").environ, "TZ": zone})
print("ESTOA current chart syntax and integration contract: PASS")
