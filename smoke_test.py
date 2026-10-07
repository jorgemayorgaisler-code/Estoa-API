import json
from tide_engine import tide_at
def main():
    k=tide_at("CUR011","2026-10-04T18:30:00")
    assert k["available"] is True
    assert k["trend"]=="FALLING"
    assert k["display_height_m"]==0.25
    print(json.dumps({"status":"PASS","kirke_tide_1830":k},ensure_ascii=False))
if __name__=="__main__": main()
