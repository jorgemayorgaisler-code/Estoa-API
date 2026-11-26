"""Release regression checks for the installed ESTOA mobile web app."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
app = (root / "web/src/main.jsx").read_text(encoding="utf-8")
sw = (root / "web/public/sw.js").read_text(encoding="utf-8")
html = (root / "web/index.html").read_text(encoding="utf-8")
workflow = (root / ".github/workflows/validate-weak-windows.yml").read_text(encoding="utf-8")

assert 'apple-mobile-web-app-capable' in html
assert 'navigator.serviceWorker.register' in html
assert re.search(r"const CACHE='estoa-v\d+'", sw)
assert "e.request.mode==='navigate'" in sw
assert "cache:'no-store'" in sw
assert "u.origin!==self.location.origin" in sw
assert "const fetchWithTimeout=" in app
assert "fetchWithTimeout(API+'/conditions/at?" in app
moment_query = app.split("const queryMoment=async()=>", 1)[1].split("const rad=", 1)[0]
assert re.search(r"setMomentData\(a\);(?:setMomentSolarStatus\('loading'\);)?setLoading\(false\);", moment_query)
assert moment_query.index("setLoading(false);") < moment_query.index("Promise.allSettled(")
assert "finally{if(request===momentRequest.current)setLoading(false)}" in moment_query
assert "Promise.allSettled(" in app
assert "tideCurve={momentCurve} nowTime={moment}" in app
assert "CONSULTA · " in app
assert "no equivalen a una validación hidrográfica" in app
assert "tests/check_mobile_release.py" in workflow
print("ESTOA mobile release contract: PASS")
