"""
2010~2014 legacy adapter.

OpenDART's single-company full financial-statement API is documented as
available from 2015 onward. The collector therefore stores 2010~2014
regular-report receipt information, but does not invent financial numbers.

If historical DART report originals are supplied/exported separately,
implement parsing here and write the normalized rows to:
data/raw/legacy_financials.csv

Expected columns:
year, report_name, fs_div, account_nm, thstrm_amount
"""
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
print("2010~2014 legacy numeric parser placeholder:", BASE/"data/raw/legacy_financials.csv")
