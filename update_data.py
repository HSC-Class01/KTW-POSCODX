import os, io, zipfile, json, time
from pathlib import Path
import requests
import pandas as pd

BASE = Path(__file__).resolve().parent
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
API_KEY = os.getenv("DART_API_KEY")
if not API_KEY:
    raise SystemExit("DART_API_KEY 환경변수가 없습니다.")

# POSCO DX's OpenDART corp_code is obtained from corpCode.xml at runtime.
# Do not hard-code the API key.
CORP_NAME = CONFIG["company_name"]
START_YEAR = int(CONFIG["start_year"])
REPORTS = CONFIG["reports"]

RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PROC = BASE / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "KTW-POSCODX-DART-Agent/1.0"})

def get_json(url, params):
    r = SESSION.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    if str(data.get("status")) != "000":
        raise RuntimeError(f"DART API error: {data.get('status')} {data.get('message')}")
    return data

def get_corp_code():
    url = "https://opendart.fss.or.kr/api/corpCode.xml"
    r = SESSION.get(url, params={"crtfc_key": API_KEY}, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        xml = z.read(z.namelist()[0]).decode("utf-8")
    # Simple XML parsing without external dependency.
    m = re.search(r"<list>.*?<corp_code>(.*?)</corp_code>.*?<corp_name>(.*?)</corp_name>.*?</list>",
                  xml, re.S)
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    for item in root.findall("list"):
        name = (item.findtext("corp_name") or "").strip()
        if name in {"포스코디엑스", "포스코DX", "POSCO DX COMPANY LTD."}:
            return item.findtext("corp_code")
    raise RuntimeError("포스코DX corp_code를 찾지 못했습니다.")

def collect_report_list(corp_code):
    rows = []
    for year in range(START_YEAR, pd.Timestamp.today().year + 1):
        # API accepts a date range. Search year by year.
        data = get_json(
            "https://opendart.fss.or.kr/api/list.json",
            {
                "crtfc_key": API_KEY,
                "corp_code": corp_code,
                "bgn_de": f"{year}0101",
                "end_de": f"{year}1231",
                "pblntf_ty": "A",
                "last_reprt_at": "Y",
                "sort": "date",
                "sort_mth": "asc",
                "page_no": 1,
                "page_count": 100,
            },
        )
        for x in data.get("list", []):
            detail = x.get("pblntf_detail_ty")
            if detail in REPORTS:
                rows.append({
                    "year": year,
                    "report_name": REPORTS[detail],
                    "report_code": detail,
                    "rcept_no": x.get("rcept_no"),
                    "rcept_dt": x.get("rcept_dt"),
                    "report_nm": x.get("report_nm"),
                    "corp_name": x.get("corp_name"),
                })
        time.sleep(0.15)
    return pd.DataFrame(rows)

def collect_financials(corp_code):
    rows = []
    current_year = pd.Timestamp.today().year
    # OpenDART's full single-company financial statements API is documented
    # as available from 2015 onward.
    for year in range(max(2015, START_YEAR), current_year + 1):
        for report_code, report_name in REPORTS.items():
            for fs_div in ["CFS", "OFS"]:
                try:
                    data = get_json(
                        "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json",
                        {
                            "crtfc_key": API_KEY,
                            "corp_code": corp_code,
                            "bsns_year": str(year),
                            "reprt_code": report_code,
                            "fs_div": fs_div,
                        },
                    )
                except Exception:
                    continue
                for x in data.get("list", []):
                    rows.append({
                        "year": year,
                        "report_name": report_name,
                        "report_code": report_code,
                        "fs_div": fs_div,
                        "sj_div": x.get("sj_div"),
                        "account_id": x.get("account_id"),
                        "account_nm": x.get("account_nm"),
                        "thstrm_amount": x.get("thstrm_amount"),
                        "thstrm_add_amount": x.get("thstrm_add_amount"),
                        "frmtrm_amount": x.get("frmtrm_amount"),
                        "frmtrm_q_amount": x.get("frmtrm_q_amount"),
                        "rcept_no": x.get("rcept_no"),
                    })
                time.sleep(0.1)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    import re
    corp_code = get_corp_code()
    print("corp_code:", corp_code)

    reports = collect_report_list(corp_code)
    reports.to_csv(RAW / "dart_reports.csv", index=False, encoding="utf-8-sig")

    financials = collect_financials(corp_code)
    financials.to_csv(RAW / "dart_financials.csv", index=False, encoding="utf-8-sig")

    print(f"reports: {len(reports):,}")
    print(f"financial rows: {len(financials):,}")
    print("2010~2014 report index is collected; numeric financial API data starts at 2015.")
