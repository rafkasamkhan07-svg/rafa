import json, re, time
from datetime import datetime, timezone
from pathlib import Path
import yfinance as yf
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
OUT = ROOT / "stocks-live.json"
html = HTML.read_text(encoding="utf-8")
m = re.search(r"let stocks=(\[.*?\]);\nconst \$=", html, re.S)
if not m:
    # The embedded original dataset starts as let stocks=[ ... ];
    m = re.search(r"let stocks=(\[.*?\]);\s*const \$=", html, re.S)
if not m:
    raise RuntimeError("Tidak dapat membaca daftar saham dari index.html")
base = json.loads(m.group(1))
by_code = {x["code"]: x for x in base}
codes = list(by_code)
tickers = [c + ".JK" for c in codes]
updated = {}
# Batch requests to avoid a single enormous Yahoo query.
for start in range(0, len(tickers), 60):
    batch = tickers[start:start+60]
    try:
        frame = yf.download(batch, period="5d", interval="1d", group_by="ticker", auto_adjust=False,
                            progress=False, threads=True, timeout=25)
        if frame is None or frame.empty:
            continue
        for code, ticker in zip(codes[start:start+60], batch):
            try:
                if isinstance(frame.columns, pd.MultiIndex):
                    if ticker not in frame.columns.get_level_values(0):
                        continue
                    one = frame[ticker].dropna(subset=["Close"])
                else:
                    one = frame.dropna(subset=["Close"])
                if one.empty:
                    continue
                row = one.iloc[-1]
                prev = one.iloc[-2] if len(one) > 1 else row
                def num(key):
                    val = row.get(key)
                    return None if pd.isna(val) else float(val)
                close = num("Close")
                if close is None or close <= 0:
                    continue
                updated[code] = {
                    "code": code,
                    "name": by_code[code].get("name", code),
                    "date": str(one.index[-1].date()),
                    "open": num("Open"), "high": num("High"), "low": num("Low"), "close": close,
                    "prev": (None if pd.isna(prev.get("Close")) else float(prev.get("Close"))),
                    "change": (close - float(prev.get("Close"))) if not pd.isna(prev.get("Close")) else 0,
                    "volume": (0 if pd.isna(row.get("Volume")) else int(row.get("Volume"))),
                    "value": by_code[code].get("value", 0),
                    "frequency": by_code[code].get("frequency", 0),
                    "source": "Yahoo Finance"
                }
            except Exception:
                continue
    except Exception as e:
        print(f"Batch {start}: {e}")
    time.sleep(1)

# Only publish if a useful portion was fetched; otherwise retain prior JSON.
if len(updated) < 20:
    raise RuntimeError(f"Hanya {len(updated)} saham berhasil diambil; data lama tidak ditimpa.")
# Preserve rows not returned by provider using the existing imported values, clearly marked as stale.
combined = []
for code in codes:
    if code in updated:
        combined.append(updated[code])
    else:
        old = dict(by_code[code])
        old["source"] = "Data impor lama (tidak berhasil diperbarui)"
        combined.append(old)
market_dates = [x["date"] for x in updated.values() if x.get("date")]
payload = {
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "marketDate": max(market_dates) if market_dates else "Tidak tersedia",
    "provider": "Yahoo Finance; data mungkin tertunda dan tidak resmi",
    "updatedCount": len(updated),
    "totalCount": len(combined),
    "stocks": combined
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"Ditulis {len(updated)}/{len(codes)} saham ke {OUT}")
