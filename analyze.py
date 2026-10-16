from pathlib import Path
import pandas as pd
import json, re

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

METRICS = {
    "매출액": ["매출액", "수익(매출액)", "영업수익"],
    "영업이익": ["영업이익", "영업이익(손실)"],
    "당기순이익": ["당기순이익", "당기순이익(손실)", "분기순이익"],
    "자산총계": ["자산총계"],
    "부채총계": ["부채총계"],
    "자본총계": ["자본총계"],
    "유동자산": ["유동자산"],
    "유동부채": ["유동부채"],
    "현금및현금성자산": ["현금및현금성자산", "현금및현금성 자산"],
    "영업활동현금흐름": ["영업활동현금흐름", "영업활동으로인한현금흐름", "영업활동으로 인한 현금흐름"],
}

def num(v):
    if pd.isna(v): return None
    s = str(v).replace(",", "").strip()
    if s in {"", "-", "nan", "None"}: return None
    try: return float(s)
    except: return None

def pick_value(g, names):
    for n in names:
        m = g[g["account_nm"].astype(str).str.replace(" ", "", regex=False) == n.replace(" ", "")]
        if not m.empty:
            # Prefer accumulated amount for interim income-statement rows.
            for col in ["thstrm_add_amount", "thstrm_amount"]:
                vals = m[col].map(num).dropna()
                if not vals.empty:
                    return vals.iloc[0]
    return None

f = RAW / "dart_financials.csv"
if not f.exists():
    raise SystemExit("dart_financials.csv가 없습니다. 먼저 update_data.py를 실행하세요.")

df = pd.read_csv(f, dtype=str)
df["year"] = pd.to_numeric(df["year"], errors="coerce")

# Prefer CFS for consolidated data when available; otherwise OFS.
records = []
for (year, report_name, report_code, fs_div), g in df.groupby(
    ["year","report_name","report_code","fs_div"], dropna=False
):
    rec = {"year": int(year), "report_name": report_name, "report_code": report_code, "fs_div": fs_div}
    for metric, aliases in METRICS.items():
        rec[metric] = pick_value(g, aliases)
    records.append(rec)

out = pd.DataFrame(records)

# One representative row per year/report: prefer CFS, then OFS.
rank = out["fs_div"].map({"CFS": 0, "OFS": 1}).fillna(9)
out["_rank"] = rank
out = out.sort_values(["year","report_code","_rank"]).drop_duplicates(
    ["year","report_code"], keep="first"
).drop(columns="_rank")

# Annual series: use business report when available.
annual = out[out["report_code"].astype(str) == "11011"].copy().sort_values("year")
for col in METRICS:
    annual[col] = pd.to_numeric(annual[col], errors="coerce")

# Ratios. Assets/equity use average balance where prior year is available.
annual["영업이익률"] = annual["영업이익"] / annual["매출액"] * 100
annual["순이익률"] = annual["당기순이익"] / annual["매출액"] * 100
annual["부채비율"] = annual["부채총계"] / annual["자본총계"] * 100
annual["자기자본비율"] = annual["자본총계"] / annual["자산총계"] * 100
annual["유동비율"] = annual["유동자산"] / annual["유동부채"] * 100
annual["총자산회전율"] = annual["매출액"] / annual["자산총계"]

annual["ROA"] = annual["당기순이익"] / annual["자산총계"] * 100
annual["ROE"] = annual["당기순이익"] / annual["자본총계"] * 100

annual["매출액증가율"] = annual["매출액"].pct_change() * 100
annual["영업이익증가율"] = annual["영업이익"].pct_change() * 100
annual["당기순이익증가율"] = annual["당기순이익"].pct_change() * 100

annual.to_csv(OUT / "annual_analysis.csv", index=False, encoding="utf-8-sig")
out.to_csv(OUT / "all_report_analysis.csv", index=False, encoding="utf-8-sig")

# JSON for GitHub Pages.
payload = {
    "company": "포스코DX",
    "updated_at": pd.Timestamp.utcnow().isoformat(),
    "annual": annual.astype(object).where(pd.notna(annual), None).to_dict(orient="records"),
    "metrics": list(METRICS.keys()),
    "ratios": ["영업이익률","순이익률","ROA","ROE","부채비율","자기자본비율","유동비율",
               "매출액증가율","영업이익증가율","당기순이익증가율","총자산회전율"]
}
(OUT / "dashboard_data.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2, default=str, allow_nan=False), encoding="utf-8"
)
print("분석 완료:", OUT / "annual_analysis.csv")
