#!/usr/bin/env python3
"""digest_tool.py (v1, 2026-11-20) - builds docs/history_digest.md (digest v2) and the data/ tables from the Strava export, the FIT files
from the chat (tests/) and the hand-kept session list data/session_context.csv. Uses cp_lib v1.15+ (METRICS section).

Pipeline: sessions (1 Hz, cached in .cache/) -> HR cleaning (manual ranges, artefact scan, jumps) -> HR model per sport (second cleaning
pass, session HR offsets) -> loads (TSS / rTSS, intensity shares) -> CTL/ATL/TSB -> factors (weather, room temperature, fatigue) ->
[--calibrate: context model + HCI reference] -> HCI -> decoupling, EF, HRR -> power bests -> markdown.

Inputs (data/): session_context.csv (one row per session from the data basis, 1 Sep 2026: id, date, start_local, kind ride/vride/run,
src E/F/C, file 'export:activities/<f>' | 'tests/<f>' | 'stream:data/<json>', rpe, feel (default 5), fan, room_start/room_end, hr_bad
'from-to;from-to' minutes, km_override (MyWhoosh km for Edge files without distance), alt_m, ill 0/1, notes), weather_cache.csv (outdoor
weather per session), strava_bests.json (connector best efforts, Ride and VirtualRide, with the date read), run_10_11_stream.json (unused since 21 Nov: tests/10_11.fit).
Calibration files (written by --calibrate, read otherwise): hci_ctx_coef.csv, hci_rpe_coef.csv, hci_reference.json.
Outputs (data/): metrics.csv, pmc.csv, factors.csv, hci.csv, bests.csv; the digest markdown (--out).

Usage:  python3 digest_tool.py --export strava_export_22_11.zip --out docs/history_digest.md [--calibrate] [--asof 2026-11-22]
        New activities in the export that are missing from session_context.csv are appended with defaults (check and edit them, then rerun).
Recalibrate (--calibrate) about monthly or after big changes (new fan, new meter); the HCI scale then shifts a little.
"""
import argparse, json, os, sys, zipfile, re
from datetime import date, timedelta
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cp_lib as cp

DATA_START = "2026-09-01"                      # data basis (Pat 20 Nov): rides with power and HR, and all runs, from 1 Sep
RIDER_KG = 56.0                                # Pat 12 Nov
SEC = {"5s": 5, "15s": 15, "30s": 30, "1min": 60, "2min": 120, "3min": 180, "5min": 300, "8min": 480, "10min": 600, "15min": 900, "20min": 1200,
       "30min": 1800, "45min": 2700, "60min": 3600, "90min": 5400, "120min": 7200, "150min": 9000}
ZE = dict(ride=[132.5, 148.5, 162.5, 177.5], run=[149.5, 163.5, 172.5, 187.5])     # HR zone boundaries (cycling / running zones)
SIG = (0.03, 4.0)                              # stops-excluded best shown only if >= 3% and >= 4 W above the elapsed-based one


# ----------------------------------------------------------------------------- inputs
class Root:
    def __init__(self, root, export):
        self.root = os.path.abspath(root); self.data = os.path.join(self.root, "data"); self.cache = os.path.join(self.root, ".cache")
        os.makedirs(self.cache, exist_ok=True); self.export = self._export(export)

    def _export(self, export):
        p = export if os.path.isabs(export) else os.path.join(self.root, export)
        if os.path.isdir(p): return p
        out = os.path.join(self.cache, "export_" + os.path.basename(p).replace(".zip", ""))
        if not os.path.exists(os.path.join(out, "activities.csv")):
            with zipfile.ZipFile(p) as z: z.extractall(out)
        return out

    def path(self, f):
        if f.startswith("export:"): return os.path.join(self.export, f[7:])
        if f.startswith("stream:"): return os.path.join(self.root, f[7:])
        return os.path.join(self.root, f)


def read_context(R):
    c = pd.read_csv(os.path.join(R.data, "session_context.csv"), dtype={"id": str}, keep_default_na=True)
    c["hr_bad"] = c["hr_bad"].fillna("").astype(str); c["feel"] = c["feel"].fillna(5)
    return c.sort_values(["date", "start_local"]).reset_index(drop=True)


def sync_context(R, c, acts):
    """Append export activities from DATA_START that are missing from the context (defaults: feel 5, RPE from Strava). Returns (c, added)."""
    have = set(c["id"]); add = []
    kinds = {"Ride": "ride", "Virtual Ride": "vride", "VirtualRide": "vride", "Run": "run"}
    for r in acts.itertuples():
        if r.date < DATA_START or str(r.id) in have or r.type not in kinds or not isinstance(r.file, str): continue
        add.append(dict(id=str(r.id), date=r.date, start_local=str(r.start_local)[:19], kind=kinds[r.type], src="E", file="export:" + r.file,
                        rpe=r.rpe, rpe_src="strava", desc=r.desc if isinstance(r.desc, str) else "", feel=5, feel_src="default", hr_bad="", alt_m=65.0, ill=0))
    if add:
        c = pd.concat([c, pd.DataFrame(add)], ignore_index=True).sort_values(["date", "start_local"]).reset_index(drop=True)
        c.to_csv(os.path.join(R.data, "session_context.csv"), index=False)
    return c, add


def load_session(R, row):
    key = "%s_%s" % (row["date"], row["id"]); fn = os.path.join(R.cache, key + ".npz")
    if os.path.exists(fn):
        z = np.load(fn); return {k: z[k] for k in z.files}
    f = row["file"]
    if f.startswith("stream:"):
        j = json.load(open(R.path(f))); x = cp.stream_run_1hz(j["t"], j["d"], j["hr"], min_d=j.get("hr_valid_from_m", 1300))
    else:
        x = cp.session_1hz(R.path(f), row["kind"])
    np.savez_compressed(fn, **x); return x


def ranges(s):
    out = []
    for part in str(s).split(";"):
        m = re.match(r"\s*([\d.]+)\s*-\s*([\d.]+)", part)
        if m: out.append((float(m.group(1)), float(m.group(2))))
    return out


# ----------------------------------------------------------------------------- per-session metrics
def run_splits(x, step=1000):
    """Moving time per full km and best windowed 1 km / 5 km (moving time)."""
    D = np.asarray(x["D"], float); tm = np.cumsum(x["mov"].astype(float)); D = np.maximum.accumulate(np.nan_to_num(D, nan=0.0)); D = D - D[0]
    spl = []; k = step
    while k <= D[-1]:
        i = np.searchsorted(D, k); j = np.searchsorted(D, k - step); spl.append(tm[min(i, len(tm) - 1)] - tm[j]); k += step
    def best(L):
        if D[-1] < L: return np.nan
        j = np.searchsorted(D, D + L); ok = j < len(D); return float(np.min(tm[j[ok]] - tm[np.where(ok)[0]]))
    return spl, best(1000), best(5000)


def session_metrics(R, c, models):
    rows, events = [], {}
    for _, r in c.iterrows():
        x = dict(load_session(R, r)); kind = r["kind"]; ftp = cp.ftp_for(r["date"]); key = (r["date"], r["id"])
        H0, bad, sh = cp.clean_hr(x, kind, ranges(r["hr_bad"]))
        rb = 0.0
        if key in models: x["H"], rb = models[key]["H"], models[key]["resid_blank"]
        else: x["H"] = H0
        d = dict(date=r["date"], id=r["id"], kind=kind, src=r["src"], ftp=ftp if kind != "run" else np.nan)
        d.update(cp.run_load(x) if kind == "run" else cp.ride_load(x, ftp))
        if np.isfinite(r.get("km_override", np.nan)): d["km"] = float(r["km_override"])
        if np.isfinite(r.get("sec_override", np.nan)):               # Strava moving time where the file is only a reduced stream
            d["sec"] = int(r["sec_override"])
            if kind == "run": d["pace"] = d["sec"] / d["km"]; d["tss"] = d["sec"] / 3600 * d["IF"] ** 2 * 100
        d["notes"] = r["notes"] if isinstance(r["notes"], str) else ""
        d["has_power"] = kind != "run" and np.isfinite(d.get("np_w", np.nan))
        d.update(cp.hr_stats(x)); d["hr_bad_pct"] = (sh + rb) * 100
        d.update(cp.aero_decoupling(x, kind, ftp)); d["ef"] = cp.efficiency_factor(x, kind) if (kind == "run" or d["has_power"]) else np.nan
        ev = cp.hrr_events(x, kind, ftp) if (kind == "run" or d["has_power"]) else []; events[key] = ev
        for cat in ("mod", "max"):
            v = [e[2] for e in ev if e[3] == cat]; d["hrr_%s_n" % cat] = len(v)
            d["hrr_%s_avg" % cat] = float(np.mean(v)) if v else np.nan; d["hrr_%s_best" % cat] = float(max(v)) if v else np.nan
            d["hrr_%s_list" % cat] = ";".join("%.1f" % a for a in v)
        if kind == "run":
            spl, b1, b5 = run_splits(x); d["splits"] = " ".join(cp.fmt_t(s) for s in spl); d["best_1k"] = b1; d["best_5k"] = b5
        rows.append(d)
    return pd.DataFrame(rows), events


def pre_basis_tss(R, acts):
    """Load before DATA_START for the CTL/ATL seed: rides with power from the file (FTP of the month), others moving h x 0.75^2 x 100."""
    rows = []
    for r in acts[acts.date < DATA_START].itertuples():
        if r.type not in ("Ride", "Virtual Ride", "Run"): continue
        t = r.moving_s / 3600 * 0.75 ** 2 * 100; how = "estimate (IF 0.75)"
        if isinstance(r.file, str) and r.type != "Run":
            x = load_session(R, dict(date=r.date, id=str(r.id), file="export:" + r.file, kind="ride"))
            L = cp.ride_load(x, cp.ftp_for(r.date))
            if np.isfinite(L.get("tss", np.nan)):
                t, how = L["tss"], "power (FTP %.0f)" % cp.ftp_for(r.date)
                rows.append(dict(date=r.date, id=str(r.id), type=r.type, km=r.km, min=L["sec"] / 60, tss=t, how=how, sec_p=L["sec"],
                                 easy_pct=L["easy_pct"], z3_pct=L["z3_pct"], z4_pct=L["z4_pct"])); continue
        rows.append(dict(date=r.date, id=str(r.id), type=r.type, km=r.km, min=r.moving_s / 60, tss=t, how=how, sec_p=0.0, easy_pct=np.nan, z3_pct=np.nan, z4_pct=np.nan))
    return pd.DataFrame(rows)


def factors(R, c, m, P):
    w = pd.read_csv(os.path.join(R.data, "weather_cache.csv"), dtype={"id": str}); P = P.set_index("date"); rows = []
    daily = P["tss"].to_dict()
    for _, r in c.iterrows():
        mm = m[(m.date == r["date"]) & (m.id == r["id"])].iloc[0]; dur = mm["sec"] / 60; IF = mm.get("IF", np.nan)
        if r["kind"] == "vride":
            rs = r["room_start"] if np.isfinite(r["room_start"]) else 15.5
            rise = (r["room_end"] - rs) if np.isfinite(r["room_end"]) else 3.0 * min(1.3, (IF if np.isfinite(IF) else 0.8) / 0.85) * (1 - np.exp(-dur / 45))
            temp = rs + 0.6 * rise                            # [Claude] room model: mean = start + 0.6 x rise (start 15.5 C unless known)
        else:
            ww = w[(w.date == r["date"]) & (w.id == r["id"])]; temp = float(ww["apparent"].iloc[0]) if len(ww) and np.isfinite(ww["apparent"].iloc[0]) else np.nan
        fan = r["fan"] if isinstance(r["fan"], str) else ""
        fancat = "out" if r["kind"] != "vride" else ("nofan" if fan in ("none", "weak") else ("oldfan" if fan == "old" else "newfan"))
        prev = (pd.Timestamp(r["date"]) - timedelta(days=1)).strftime("%Y-%m-%d")
        p1 = sum(daily.get((pd.Timestamp(r["date"]) - timedelta(days=i)).strftime("%Y-%m-%d"), 0) for i in (1,))
        rows.append(dict(date=r["date"], id=r["id"], kind=r["kind"], temp=temp, fancat=fancat, feel=r["feel"], rpe=r["rpe"], IF=IF, dur=dur,
                         tsb=P.loc[r["date"], "tsb"], atl=P.loc[prev, "atl"], ctl=P.loc[prev, "ctl"], prev1=p1,
                         alt_m=r.get("alt_m", 65.0), ill=r.get("ill", 0)))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- HCI
def hci_offsets(models, F):
    rows = []
    for (d, i), s in models.items():
        rows.append(dict(date=d, id=i, b=s["b"], rmse=s["rmse"], n=s["n_ok"]))
    return pd.DataFrame(rows).merge(F, on=["date", "id"])


def calibrate(R, models, F):
    """Context model for the ride HR offsets (OLS, positive-part shrinkage per coefficient) and the RPE expectation; writes the coefficient files."""
    B = hci_offsets(models, F); B = B[np.isfinite(B.b) & (B.n >= 600) & (B.kind != "run")].copy()
    fr = B[np.isfinite(B.rpe)]; cr = np.linalg.lstsq(np.column_stack([np.ones(len(fr)), fr.IF, np.log(fr.dur / 60)]), fr.rpe, rcond=None)[0]
    B["rpe_dev"] = B.rpe - (cr[0] + cr[1] * B.IF + cr[2] * np.log(B.dur / 60))
    B["indoor"] = (B.fancat != "out") * 1.0; B["nofan"] = (B.fancat == "nofan") * 1.0; B["oldfan"] = (B.fancat == "oldfan") * 1.0
    B["t_c"] = B.temp - 18; B["feel_d"] = B.feel - 5; B["atl_d"] = B.atl - 35
    cols = ["indoor", "t_c", "nofan", "oldfan", "feel_d", "atl_d", "rpe_dev"]
    X = np.column_stack([np.ones(len(B))] + [B[k].values for k in cols]); y = B.b.values
    cf = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ cf; s2 = e @ e / (len(y) - X.shape[1]); se = np.sqrt(np.diag(s2 * np.linalg.pinv(X.T @ X)))
    shr = np.maximum(0, 1 - 1 / np.maximum((cf / se) ** 2, 1e-9)); shr[:2] = 1.0
    pd.DataFrame(dict(name=["intercept"] + cols, coef=cf, se=se, shrink=shr, used=cf * shr)).to_csv(os.path.join(R.data, "hci_ctx_coef.csv"), index=False)
    pd.DataFrame(dict(name=["a", "b_IF", "c_lnh"], coef=cr)).to_csv(os.path.join(R.data, "hci_rpe_coef.csv"), index=False)
    return dict(n=len(B), sd=float(B.b.std()), coef=dict(zip(["intercept"] + cols, np.round(cf * shr, 3))))


def hci_components(R, models, F, sport_of):
    CF = pd.read_csv(os.path.join(R.data, "hci_ctx_coef.csv")).set_index("name")["used"].to_dict()
    RC = tuple(pd.read_csv(os.path.join(R.data, "hci_rpe_coef.csv"))["coef"])
    Fk = F.set_index(["date", "id"]); rows = []
    runs = F[F.kind == "run"]; run_shift = float(np.nanmean(runs.rpe - (RC[0] + RC[1] * runs.IF + RC[2] * np.log(runs.dur / 60)))) if len(runs) else 0.0
    ctx = {}
    for key, s in models.items():
        f = Fk.loc[key].to_dict(); f["kind"] = sport_of[key]
        ctx[key] = cp.hci_context(f, CF, RC, run_shift if f["kind"] == "run" else 0.0)
    ok_run = [k for k, s in models.items() if sport_of[k] == "run" and s["n_ok"] >= 600]
    run_ref = float(np.mean([models[k]["b"] - ctx[k][0] for k in ok_run])) if ok_run else np.nan
    for key, s in models.items():
        sport = "run" if sport_of[key] == "run" else "ride"; f = Fk.loc[key]; c, parts = ctx[key]
        blank = s["resid_blank"] + f.get("_hr_bad_share", 0.0)
        d = dict(date=key[0], id=key[1], kind=sport_of[key], n_ok=s["n_ok"], blank=blank)
        if s["n_ok"] < cp.HCI_MIN["score_s"] or not np.isfinite(s["b"]): d["flag"] = "-"; rows.append(d); continue
        ref = CF["intercept"] + CF["indoor"] * (f["fancat"] != "out") if sport == "ride" else run_ref
        o = s["ok"]
        d.update(b=s["b"], ref=ref, c=c, L_raw=s["b"] - ref, L_adj=s["b"] - ref - c, R=s["rmse"],
                 Z_raw=cp.hci_zone_credit(s["H"][o], (s["pred0"] + ref)[o], ZE[sport]), Z_adj=cp.hci_zone_credit(s["H"][o], (s["pred0"] + ref + c)[o], ZE[sport]),
                 flag="u" if (s["n_ok"] < cp.HCI_MIN["ok_s"] or blank > cp.HCI_MIN["max_blank"]) else "", **{"c_" + k: v for k, v in parts.items()})
        rows.append(d)
    return pd.DataFrame(rows)


def hci_scores(R, C, recal=False, asof=""):
    fn = os.path.join(R.data, "hci_reference.json"); v = C[C.flag.isin(["", "u"])].copy()
    if recal or not os.path.exists(fn):
        g = v[v.flag == ""]; scales = dict(L=float(np.median(np.abs(g.L_raw))), R=float(np.median(g.R)), Z=float(np.median(1 - g.Z_raw)))
    else:
        scales = json.load(open(fn))["scales"]
    v["D_raw"] = cp.hci_badness(v.L_raw, v.R, v.Z_raw, scales); v["D_adj"] = cp.hci_badness(v.L_adj, v.R, v.Z_adj, scales)
    v["alpha"] = 0.35 + 0.25 * np.minimum(1, np.abs(v.c) / 8); v["D"] = (1 - v.alpha) * v.D_raw + v.alpha * v.D_adj
    if recal or not os.path.exists(fn):
        ref = sorted(v.loc[v.flag == "", "D"].tolist()); json.dump(dict(scales=scales, D=ref, n=len(ref), calibrated=asof), open(fn, "w"), indent=1)
    ref = json.load(open(fn))["D"]
    for k in ("D", "D_raw", "D_adj"):
        v["HCI" + k[1:]] = [cp.scale_score(cp.hci_percentile(x, ref)) for x in v[k]]
    return C.merge(v[["date", "id", "D_raw", "D_adj", "alpha", "D", "HCI", "HCI_raw", "HCI_adj"]], on=["date", "id"], how="left")


# ----------------------------------------------------------------------------- bests
def power_bests(R, c, acts):
    rows = []
    items = [dict(r) for _, r in c[c.kind != "run"].iterrows()]
    for r in acts[(acts.date < DATA_START) & (acts.type == "Ride")].itertuples():
        if isinstance(r.file, str): items.append(dict(date=r.date, id=str(r.id), kind="ride", file="export:" + r.file, src="E"))
    for r in items:
        x = load_session(R, r); P = np.nan_to_num(x["P"])
        if P.max() <= 0: continue
        meter = "Stages" if (r["kind"] == "ride" or not str(r["file"]).startswith("export:")) else "KICKR"
        d = dict(date=r["date"], id=r["id"], kind=r["kind"], meter=meter, src=r["src"])
        cs = np.cumsum(np.concatenate([[0], P])); pm = P[x["mov"]]; cm = np.cumsum(np.concatenate([[0], pm]))
        for k, w in SEC.items():
            d["el_" + k] = float((cs[w:] - cs[:-w]).max() / w) if len(P) >= w else np.nan
            d["ro_" + k] = float((cm[w:] - cm[:-w]).max() / w) if len(pm) >= w else np.nan
        rows.append(d)
    return pd.DataFrame(rows).sort_values("date")


# ----------------------------------------------------------------------------- markdown helpers
def dd(s): d_ = pd.Timestamp(s); return "%d %s" % (d_.day, d_.strftime("%b"))
def f0(v, d="-"): return "%.0f" % v if v is not None and np.isfinite(v) else d
def f1(v, d="-"): return "%.1f" % v if v is not None and np.isfinite(v) else d
def f2(v, d="-"): return "%.2f" % v if v is not None and np.isfinite(v) else d
def sgn(v): return "%+.1f" % v if np.isfinite(v) else "-"
def hms(s): s = int(round(s)); return "%d:%02d:%02d" % (s // 3600, s % 3600 // 60, s % 60) if s >= 3600 else "%d:%02d" % (s // 60, s % 60)
def tbl(head, rows): return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]


def hrr_cell(r):
    parts = []
    for cat in ("mod", "max"):
        n = r["hrr_%s_n" % cat]
        parts.append("-" if not n else (f0(r["hrr_%s_avg" % cat]) if n == 1 else "%s, %s" % (f0(r["hrr_%s_avg" % cat]), f0(r["hrr_%s_best" % cat]))))
    return "; ".join(parts) if parts != ["-", "-"] else "-"


def dec_cell(r):
    if r["dec_flag"] == "u" or not np.isfinite(r["dec"]): return "u" if r["kind"] == "run" or r.get("has_power", True) else "-"
    return sgn(r["dec"]) + (" " + r["dec_flag"] if isinstance(r["dec_flag"], str) and r["dec_flag"] else "")


def hci_cell(r):
    if not isinstance(r.get("flag"), str) or r["flag"] == "-" or not np.isfinite(r.get("HCI", np.nan)): return "-"
    return f0(r["HCI"]) + (" u" if r["flag"] == "u" else "")


def dec_ok(df): return df[np.isfinite(df.dec) & df.dec_flag.fillna("").isin(["", "s"])]


def dec_summary(df):
    g = dec_ok(df)
    if not len(g): return "-"
    a = g.dec.values; return "%s, %s, %s" % (sgn(a[np.argmin(np.abs(a))]), sgn(a.mean()), sgn(a[np.argmax(np.abs(a))]))


def ef_summary(df):
    o = df[(df.kind == "ride")].ef; v = df[(df.kind == "vride")].ef; u = df[df.kind == "run"].ef
    return " / ".join(f2(np.nanmean(s)) if s.notna().any() else "-" for s in (o, v, u))


def hci_summary(df):
    h = df[df.flag.fillna("") == ""].HCI.dropna()
    return "-" if not len(h) else "%s (%s-%s)" % (f0(h.mean()), f0(h.min()), f0(h.max()))


def hrr_summary(df):
    out = []
    for cat in ("mod", "max"):
        v = [float(a) for s in df["hrr_%s_list" % cat].fillna("") for a in str(s).split(";") if a]
        out.append(f0(np.mean(v)) if v else "-")
    return "; ".join(out) if out != ["-", "-"] else "-"


# ----------------------------------------------------------------------------- markdown
def write_digest(out, M, PMC, B, pre, strava, asof, export_name, export_last, calib, hci_n):
    rides = M[(M.kind != "run") & M.has_power].copy(); runs = M[M.kind == "run"].copy()
    L = ["# History digest: Pat, cycling | running\n",
         "As of %s: %s, activities to %s; FIT files from the chat and the Strava connector (bests read %s). Generated with digest_tool.py v1 (cp_lib v1.16) from data/session_context.csv; tables: data/metrics.csv, data/hci.csv, data/pmc.csv, data/bests.csv.\n"
         % (dd(asof) + " " + asof[:4], export_name, dd(export_last), dd(strava.get("read", asof))),
         "## 0. Context and conventions\n",
         "- **Data basis** (Pat, 20 Nov): rides with power and HR and all runs from 1 Sep 2026: %d outdoor rides, %d indoor rides, %d runs. Rides without power (7-20 Aug, 26 Sep) and the 29-31 Aug rides with power but no HR count only in the load history (CTL/ATL, weekly table) and the bests."
         % (((M.kind == "ride") & M.has_power).sum(), ((M.kind == "vride") & M.has_power).sum(), len(runs)),
         "- **Source marker** after the date: (E) Strava export file, (F) FIT file from the chat (Edge; the 10 Nov run: the Strava-made FIT), (C) Strava connector only (a hand-copied reduced stream).",
         "- **Power meters:** outdoors the Stages (left-only). Indoors the Stages via the Edge file where there is one (7 Nov and from 11 Nov), otherwise the KICKR via the MyWhoosh file (3, 4, 6 and 8 Nov; marked VK). The KICKR reads about +5 W at Z2 power and about the same at threshold; outdoor and indoor bests are kept apart.",
         "- **FTP for load metrics:** Aug-Oct 170 W, Nov 175 W (Pat suggested Sep 165; raised to 170 because on 22 Sep he held 170.0 W for 60 min, stops excluded). Planning FTP 175 W (12 Nov hour test). Easy = at most 77% of FTP (Nov 135 W, the easy cap), tempo 77-90%, threshold+ above 90%; shares are of moving time (coasting counts as easy).",
         "- **TSS:** rides NP-based (moving samples, coasting kept); runs rTSS = h x IF^2 x 100 with IF = normalised speed / threshold speed (5:00/km, until a run threshold test). On stop-and-go outdoor rides with sprints NP runs high (VI 1.1-1.4), so IF and TSS of many September rides read high (IF 0.95-1.10 on 1-2.5 h rides is not the true intensity). August without power: moving h x 0.75^2 x 100 (estimate, marked e).",
         "- **CTL / ATL / TSB:** 42-day and 7-day exponential averages of the daily TSS (rides + runs), starting at 0 on 7 Aug (first Strava activity); TSB = CTL - ATL of the evening before (form going into the day). Values before mid-October still carry the zero start.",
         "- **HCI (HR consistency index, 0-100):** how well HR matched the achieved power (rides) or pace (runs), intervals included. A pooled HR model (lag up 20 s / down 60 s plus a 15-min slow component and drift) gives each session an HR level; the index combines level (45%%), within-session tracking (35%%) and zone agreement (20%%). Context counts partly: temperature, fan, feel, fatigue (ATL), RPE vs expected, altitude, illness give an expected HR shift; the adjusted and raw versions are blended with 35-60%% weight on the adjusted one (more when the context effect is large). Scale: median 75, P10 55, P90 88, P97.5 93, P2.5 30 of the reference set (%d sessions, calibrated %s); u = under 5 usable min or over 30%% of HR blanked; - = no usable HR." % (hci_n, calib),
         "- **HRR** (1-min HR recovery, bpm): drop from the HR peak after an effort (20 s at 90%+ FTP or faster than 5:30/km) to 60 s later, only when the next 60 s are a real recovery (rolling or standing, at most 65% FTP; runs slower than 7:30/km). mod = peak in Z3-Z4, max = peak in Z5. Cells: mod; max with avg, best (one value when there was one recovery).",
         "- **Decoupling** (%): efficiency of the first half over the second (NP/HR, runs speed/HR) without the first 10 min (runs 5) and the last 5 (runs 2); best = closest to 0. Meant for long easy rides. i = intervals or hard (distorted), s = short (under 40 min usable, runs 30), u = not enough data. Summaries use only unflagged and s values.",
         "- **EF** (efficiency factor): NP / average HR (W per bpm); runs metres per minute / HR. Indoor and outdoor EF are not comparable (fan, meter); compare like with like.",
         "- **HR:** cleaned before all HR metrics (manual strap ranges, artefact scan, model-based dropout pass). Cycling zones <=132 / 133-148 / 149-162 / 163-177 / >=178 (LTHR 172, max 195); running <=149 / 150-163 / 164-172 / 173-187 / >=188 (LTHR 181, max 200). HR max values are the cleaned ones; 30-s max in brackets.",
         "- **Bests:** elapsed-based = Strava's power-curve convention (paused seconds count as 0 W); stops excluded = only moving seconds (Strava's average-power convention), shown in brackets only when it is clearly higher (3%% and 4 W). W/kg at %.0f kg." % RIDER_KG,
         "- **Weather:** Open-Meteo historical forecast (hourly, Brühl and Bibbona) and the Strava export's weather fields (Leutkirch); indoor room temperature from Pat's values or the room model (start 15.5 C, rise with duration and intensity).\n"]
    # 1. lookup
    lk = dict(ef_out=cp.lookup_rows(rides[rides.kind == "ride"].ef), ef_in=cp.lookup_rows(rides[rides.kind == "vride"].ef), ef_run=cp.lookup_rows(runs.ef),
              hrr_mod=cp.lookup_rows([float(a) for s in M.hrr_mod_list.fillna("") for a in str(s).split(";") if a]),
              hrr_max=cp.lookup_rows([float(a) for s in M.hrr_max_list.fillna("") for a in str(s).split(";") if a]),
              dec=cp.lookup_rows(np.abs(dec_ok(M[M.kind != "run"]).dec), higher_better=False))
    ns = dict(ef_out=int(rides[rides.kind == "ride"].ef.notna().sum()), ef_in=int(rides[rides.kind == "vride"].ef.notna().sum()), ef_run=int(runs.ef.notna().sum()),
              hrr_mod=int(M.hrr_mod_n.sum()), hrr_max=int(M.hrr_max_n.sum()), dec=len(dec_ok(M[M.kind != "run"])))
    heads = dict(ef_out="EF outdoor ride", ef_in="EF indoor ride", ef_run="EF run", hrr_mod="HRR mod (bpm)", hrr_max="HRR max (bpm)", dec="Decoupling (abs %), rides")
    use = [k for k in heads if ns[k] >= 8]; skip = [k for k in heads if ns[k] < 8]
    L += ["## 1. Score lookup (Pat's 0-100 scale)\n",
          "Value of each metric at every 5th percentile of the sessions so far (higher percentile = better; decoupling by distance from 0), with the score of that percentile. The HCI is already on this scale. Weekly and monthly values are averages, so read them against these session values (averages sit closer to the middle). Columns need at least 8 values%s.\n"
          % ("; not yet: " + ", ".join("%s (n %d)" % (heads[k], ns[k]) for k in skip) if skip else "")]
    L += tbl(["Percentile", "Score"] + ["%s (n %d)" % (heads[k], ns[k]) for k in use],
             [[p, f0(cp.scale_score(p))] + [(f2 if k.startswith("ef") else f1)(lk[k][p]) for k in use] for p in range(95, 0, -5)]) + [""]
    # 2. bests
    o = B[B.kind == "ride"]; L += ["## 2. All-time bests\n", "### 2a. Outdoor rides (Stages)\n"]
    rr = []
    for k in SEC:
        e = o["el_" + k]; ro = o["ro_" + k]
        if not e.notna().any() or k == "180min": continue
        ev = e.max(); de = o.loc[e.idxmax(), "date"]; rv = ro.max() if ro.notna().any() else np.nan
        cell, dcell = f0(ev), dd(de) + " (%s)" % o.loc[e.idxmax(), "src"]
        if np.isfinite(rv) and rv >= ev * (1 + SIG[0]) and rv - ev >= SIG[1]: cell += " (%s)" % f0(rv); dcell += " (%s)" % dd(o.loc[ro.idxmax(), "date"])
        rr.append([k, cell, f2(ev / RIDER_KG), dcell])
    L += tbl(["Duration", "W (stops excl.)", "W/kg", "Date"], rr)
    sr = strava.get("Ride", {}); notes = []
    for k, v in sr.items():
        if k in SEC and o["el_" + k].notna().any() and round(v[0]) != round(o["el_" + k].max()): notes.append("%s %s W (%s)" % (k, f0(v[0]), dd(v[1])))
    txt = "\nThe values match Strava's Ride bests (read %s)" % dd(strava.get("read", asof))
    if notes: txt += ", except " + ", ".join(notes) + ": these come from an indoor session uploaded as a Ride (%s), not from outdoor efforts" % strava.get("ride_note", "check the sport type on Strava")
    L += [txt + ". The stops-excluded 20/30-min values of 16 Sep include short stops inside the window, so they overstate a continuous effort slightly.\n"]
    v = B[(B.kind == "vride") & (B.meter == "Stages")]; sv = strava.get("VirtualRide", {}); rr = []
    for k in SEC:
        e = v["el_" + k]; s = sv.get(k)
        if not e.notna().any() and not s: continue
        st = ("%s (%s)" % (f0(e.max()), dd(v.loc[e.idxmax(), "date"]))) if e.notna().any() else "-"
        rr.append([k, st, f2(e.max() / RIDER_KG) if e.notna().any() else "-", ("%s (%s)" % (f0(s[0]), dd(s[1]))) if s else "-"])
    L += ["### 2b. Indoor rides\n", "Stages = Edge files (7 Nov and from 11 Nov); KICKR = Strava's VirtualRide bests (MyWhoosh uploads, KICKR power). The two meters agree within about 1% at threshold; short sprints read differently (cadence, sampling).\n"]
    L += tbl(["Duration", "Stages W (date)", "W/kg", "KICKR W (date)"], rr) + [""]
    # 3. monthly bests
    cols = ["5s", "1min", "5min", "10min", "20min", "60min"]; rr = []
    for (mo, kind), g in B.assign(mo=B.date.str[:7]).groupby(["mo", "kind"]):
        if kind == "vride": g = g[g.meter == "Stages"]
        if not len(g): continue
        rr.append([mo + (" indoor" if kind == "vride" else "")] + [f0(g["el_" + k].max()) for k in cols])
    L += ["## 3. Bests by month (elapsed-based, W; indoor = Stages from the Edge files)\n"] + tbl(["Month"] + cols, rr) + [""]
    # 4. weekly / monthly
    A = M.copy(); A["wk"] = A.date.map(lambda s: (pd.Timestamp(s) - timedelta(days=pd.Timestamp(s).weekday())).strftime("%Y-%m-%d"))
    pr = pre.copy(); pr["wk"] = pr.date.map(lambda s: (pd.Timestamp(s) - timedelta(days=pd.Timestamp(s).weekday())).strftime("%Y-%m-%d"))
    PM = PMC.copy(); PM["wk"] = PM.date.map(lambda s: (pd.Timestamp(s) - timedelta(days=pd.Timestamp(s).weekday())).strftime("%Y-%m-%d")); PM["mo"] = PM.date.str[:7]
    A["mo"] = A.date.str[:7]; pr["mo"] = pr.date.str[:7]

    def load_row(g, gp):
        rd = g[g.kind != "run"]; ru = g[g.kind == "run"]; pw = rd[rd.has_power]; nV = int((rd.kind == "vride").sum())
        tss = list(g.tss.dropna()) + list(gp.tss); est = len(gp) and gp.how.str.startswith("estimate").any()
        sec = pw.sec.sum() + gp.sec_p.sum(); sh = lambda k: f0(((pw[k] * pw.sec).sum() + (gp[k].fillna(0) * gp.sec_p).sum()) / sec) if sec else "-"
        n_r = len(rd) + len(gp)
        return ["%d%s" % (n_r, " (%d V)" % nV if nV else ""), str(len(ru)) if len(ru) else "-", f0(rd.km.sum() + gp.km.sum()), f1(ru.km.sum()) if len(ru) else "-",
                f1((g.sec.sum() + gp["min"].sum() * 60) / 3600), (f0(sum(tss)) + (" e" if est else "")) if tss else "-",
                ("%s / %s / %s" % (f0(np.mean(tss)), f0(min(tss)), f0(max(tss)))) if tss else "-", sh("easy_pct"), sh("z3_pct"), sh("z4_pct")]

    def form_row(g, pm, weekly=True):
        if weekly:
            e = pm.iloc[-1]; nxt_tsb = e.ctl - e.atl
            form = [f0(e.ctl), f0(e.atl), "%s (%s)" % (f0(nxt_tsb), f0(min(pm.tsb.iloc[1:].min() if len(pm) > 1 else nxt_tsb, nxt_tsb)))]
        else:
            form = ["%s -> %s (%s)" % (f0(pm.ctl.iloc[0]), f0(pm.ctl.iloc[-1]), f0(pm.ctl.max())), "%s (%s)" % (f0(pm.atl.mean()), f0(pm.atl.max())),
                    "%s (%s, %s)" % (f0(pm.tsb.mean()), f0(pm.tsb.min()), f0(pm.tsb.max()))]
        q = g[g.date >= DATA_START]
        return form + ([hci_summary(q), hrr_summary(q), dec_summary(q[q.kind != "run"]), ef_summary(q)] if len(q) else ["-"] * 4)

    wks = sorted(set(A.wk) | set(pr.wk)); r4a, r4b = [], []
    for w in wks:
        g, gp, pm = A[A.wk == w], pr[pr.wk == w], PM[PM.wk == w]
        r4a.append([w] + load_row(g, gp)); r4b.append([w] + form_row(g, pm))
    L += ["## 4. Weekly and monthly summaries\n", "### 4a. Weekly load\n",
          "Rides incl. indoor (V); km rides / runs; TSS = rides + runs (e = includes August estimates); avg / min / max per session; intensity shares of ride moving time (rides with power).\n"]
    L += tbl(["Week of", "Rides", "Runs", "km ride", "km run", "Moving h", "TSS", "TSS avg / min / max", "Easy %", "Tempo %", "Thr+ %"], r4a) + [""]
    L += ["### 4b. Weekly form and quality\n", "CTL, ATL and TSB at the end of the week (TSB = form going into the next day; lowest daily TSB of the week in brackets). HCI avg (range); HRR avg mod; max; decoupling best, avg, worst (unflagged rides); EF outdoor / indoor / run.\n"]
    L += tbl(["Week of", "CTL", "ATL", "TSB (lowest)", "HCI", "HRR mod; max", "Decoupling", "EF out / in / run"], r4b) + [""]
    r4c, r4d = [], []
    for mo in sorted(set(A.mo) | set(pr.mo)):
        g, gp, pm = A[A.mo == mo], pr[pr.mo == mo], PM[PM.mo == mo]
        r4c.append([mo] + load_row(g, gp)); r4d.append([mo] + form_row(g, pm, weekly=False))
    L += ["### 4c. Monthly load\n"] + tbl(["Month", "Rides", "Runs", "km ride", "km run", "Moving h", "TSS", "TSS avg / min / max", "Easy %", "Tempo %", "Thr+ %"], r4c) + [""]
    L += ["### 4d. Monthly form and quality\n", "CTL first -> last day (highest); ATL average (highest); TSB average (lowest, highest); %s is month to date.\n" % asof[:7]]
    L += tbl(["Month", "CTL", "ATL", "TSB", "HCI", "HRR mod; max", "Decoupling", "EF out / in / run"], r4d) + [""]
    # 5. per ride
    rides = rides.sort_values(["date"]); r5a, r5b = [], []
    for _, r in rides.iterrows():
        tag = "%s (%s)" % (r.date, r.src); v = "" if r.kind == "ride" else ("VK" if r.src == "E" else "V")
        r5a.append([tag, v, f1(r.km), f0(r.sec / 60), f0(r.avg_w), f0(r.np_w), f2(r.IF), f0(r.easy_pct), f0(r.cad), f0(r.tss), f0(r.z3_pct), f0(r.z4_pct)])
        hr = "-" if not np.isfinite(r.hr_avg) else "%s/%s (%s)" % (f0(r.hr_avg), f0(r.hr_max), f0(r.hr30))
        r5b.append([tag, hr, hci_cell(r), hrr_cell(r), dec_cell(r), f2(r.ef)])
    L += ["## 5. Per ride (rides with power from 1 Sep; V = indoor, Stages; VK = indoor, KICKR)\n", "### 5a. Load\n"]
    L += tbl(["Date (src)", "", "km", "Moving min", "Avg W", "NP", "IF", "Easy %", "Cadence", "TSS", "Tempo %", "Thr+ %"], r5a) + [""]
    L += ["### 5b. HR and quality\n"] + tbl(["Date (src)", "HR avg/max (30 s max)", "HCI", "HRR mod; max", "Decoupling", "EF"], r5b) + [""]
    # 6. runs
    r6a, r6b = [], []
    for _, r in runs.sort_values("date").iterrows():
        tag = "%s (%s)" % (r.date, r.src)
        star = " *" if "reps" in r.notes else ""
        r6a.append([tag, f2(r.km), cp.fmt_t(r.sec), cp.fmt_t(r.pace) + "/km", cp.fmt_t(r.ns_pace) + "/km", f2(r.IF), f0(r.tss), (r.splits or "-") + star,
                    "%s / %s%s" % (cp.fmt_t(r.best_1k) if np.isfinite(r.best_1k) else "-", cp.fmt_t(r.best_5k) if np.isfinite(r.best_5k) else "-", star)])
        hr = "-" if not np.isfinite(r.hr_avg) else "%s/%s (%s)" % (f0(r.hr_avg), f0(r.hr_max), f0(r.hr30))
        r6b.append([tag, hr, hci_cell(r), hrr_cell(r), dec_cell(r), f2(r.ef)])
    L += ["## 6. Runs\n", "### 6a. Load and pace (moving time; splits per full km)\n"]
    L += tbl(["Date (src)", "km", "Moving", "Pace", "Norm. pace", "IF", "rTSS", "Splits per km", "Best 1K / 5K"], r6a)
    L += ["\n\\* Reps with walking recoveries (14 Oct): the pause rule removes the walks, so single splits and the windowed bests read too fast (Strava: best 1K 4:01; moving 39:06). 10 Nov: recorded 4.26 km (phone died at 4.25 km; about 5.06 km run); HR only from min 14 (strap without contact in lap 1).\n"]
    L += ["### 6b. HR and quality\n"] + tbl(["Date (src)", "HR avg/max (30 s max)", "HCI", "HRR mod; max", "Decoupling", "EF"], r6b)
    L += ["\nRun HCI: only 8 runs, so the run reference is thin; short fast reps (14 Oct) read low partly because HR cannot catch up with the pace.\n"]
    # 7. top sessions
    T = M[np.isfinite(M.tss)].sort_values("tss", ascending=False).head(10); rr = []
    for i, (_, r) in enumerate(T.iterrows(), 1):
        rr.append([i, "%s (%s)" % (r.date, r.src), {"ride": "Ride", "vride": "Indoor ride", "run": "Run"}[r.kind], f0(r.tss), hms(r.sec), f2(r.IF),
                   (f0(r.np_w) + " W NP") if r.kind != "run" else cp.fmt_t(r.ns_pace) + "/km norm."])
    L += ["## 7. Top sessions by TSS\n"] + tbl(["#", "Date (src)", "Type", "TSS", "Moving", "IF", "Intensity"], rr) + [""]
    # 8. notes
    L += ["## 8. Other data notes\n",
          "- Rides without power: 7-20 Aug (12 rides; Strava's 'average watts' for them are estimates, not measured) and 26 Sep (12 min). First measured power: 29 Aug; HR strap from 1 Sep.",
          "- HR strap problems handled in the cleaning: 5 Sep min 20-36, 10 Sep min 13-58, 29 Sep min 55-57.5, 16 Oct dropouts, 17 Oct (HR unusable), 23 Oct min 22-31 and 26 Oct min 17.3-20.7 (frozen values), 10 Nov until min 15.5 (first lap); plus dropouts found by the model pass (share in data/metrics.csv, hr_bad_pct).",
          "- Weather of the 21 and 22 Nov rides: the export's weather columns (Strava's provider; its apparent temperature as given, 8.9 and 4.2 C).",
          "- 12 Nov: the Edge file holds the test part only (60:03; the MyWhoosh file 61:40, 34.8 km). Indoor km: MyWhoosh distance where the Edge file has none.",
          "- The Garmin files also contain beat-to-beat (HRV) messages; cp_lib.hrv_quality() uses them to check strap artefacts.",
          "- Strava-made run FIT files: the 'speed' field runs far slower than distance-derived speed; use the distance field for pacing.",
          "- Refresh: python3 digest_tool.py --export <newest export zip> --out docs/history_digest.md (add new chat FITs to tests/ and their rows to data/session_context.csv first; --calibrate about monthly)."]
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n"); return len("\n".join(L))


def export_label(path, last):
    m = re.search(r"(\d\d)_(\d\d)", os.path.basename(path))
    if not m: return "Strava export " + os.path.basename(path)
    d_ = date(int(last[:4]), int(m.group(2)), int(m.group(1))); return "Strava export of %d %s (%s)" % (d_.day, d_.strftime("%b %Y"), os.path.basename(path).replace(".zip", ".zip"))


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--export", required=True); ap.add_argument("--out", default="docs/history_digest.md"); ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--asof", default=date.today().isoformat()); ap.add_argument("--tables", default=None, help="folder for the output tables (default data/)")
    ap.add_argument("--quiet", action="store_true"); ap.add_argument("--no-sync", action="store_true", help="do not append new export activities to the context")
    a = ap.parse_args(argv)
    R = Root(a.root, a.export); acts = cp.load_activities_csv(os.path.join(R.export, "activities.csv")); acts["id"] = acts["id"].astype(str)
    c, added = (read_context(R), []) if a.no_sync else sync_context(R, read_context(R), acts)
    if added and not a.quiet: print("added to session_context.csv (check feel / fan / notes):", [(x["date"], x["kind"]) for x in added])
    # HR model per sport on first-pass cleaned HR
    items = dict(ride=[], run=[]); sport_of = {}; hr_share = {}
    for _, r in c.iterrows():
        x = load_session(R, r); key = (r["date"], r["id"])
        if r["kind"] != "run" and not np.nan_to_num(x["P"]).max() > 0: continue
        H, bad, sh = cp.clean_hr(x, r["kind"], ranges(r["hr_bad"])); hr_share[key] = sh
        items["run" if r["kind"] == "run" else "ride"].append((key, r["kind"], x, H, cp.ftp_for(r["date"]))); sport_of[key] = r["kind"]
    models = {}; coefs = {}
    for sp, it in items.items():
        coefs[sp], mo = cp.hr_model_sessions(it); models.update(mo)
    M, events = session_metrics(R, c, models)
    pre = pre_basis_tss(R, acts); daily = {}
    for d_, t in list(zip(pre.date, pre.tss)) + list(zip(M.date, M.tss)):
        if np.isfinite(t): daily[d_] = daily.get(d_, 0) + t
    for r in M[(M.kind != "run") & ~M.has_power].itertuples():                       # rides without power from the data basis: estimate
        daily[r.date] = daily.get(r.date, 0) + r.sec / 3600 * 0.75 ** 2 * 100
    first = min(acts.date); end = max(a.asof, M.date.max())
    P = cp.pmc(daily, first, end); F = factors(R, c, M, P)
    F["_hr_bad_share"] = [hr_share.get((d_, i), 0.0) for d_, i in zip(F.date, F.id)]
    cal = calibrate(R, models, F) if a.calibrate else None
    C = hci_components(R, models, F, sport_of); S = hci_scores(R, C, recal=a.calibrate, asof=a.asof)
    M = M.merge(S[["date", "id", "flag", "HCI", "HCI_raw", "HCI_adj"]], on=["date", "id"], how="left")
    B = power_bests(R, c, acts)
    tdir = a.tables or R.data; os.makedirs(tdir, exist_ok=True)
    for name, df in (("metrics", M), ("pmc", P), ("factors", F), ("hci", S), ("bests", B)): df.to_csv(os.path.join(tdir, name + ".csv"), index=False)
    sb = os.path.join(R.data, "strava_bests.json"); strava = json.load(open(sb)) if os.path.exists(sb) else {}
    ref = json.load(open(os.path.join(R.data, "hci_reference.json")))
    n = write_digest(a.out if os.path.isabs(a.out) else os.path.join(R.root, a.out), M, P, B, pre, strava, a.asof,
                     export_label(a.export, acts.date.max()), acts.date.max(),
                     ref.get("calibrated", a.asof), ref["n"])
    if not a.quiet:
        print("HR model ride", np.round(coefs["ride"], 3), "run", np.round(coefs["run"], 3))
        if cal: print("calibration:", cal)
        print("digest written:", n, "characters;", len(M), "sessions")
    return M, S, P, B


if __name__ == "__main__":
    main()
