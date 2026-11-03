#!/usr/bin/env python3
"""routes_tool.py (v2) - GPX route geometry for the 'cycling | running' project (komoot / Strava GPX; needs numpy).

Python:  from routes_tool import analyse, stretches, moderate_bends, loop_closure, elevation_diag, compare_routes, route_entry_md, wind_rel, compass
CLI:     python3 routes_tool.py [DIR]                    table of every route in DIR (default gpx/)
         python3 routes_tool.py --compare A.gpx B.gpx    differences between two versions of a route
         python3 routes_tool.py --diag FILE.gpx          elevation / data-quality diagnostics
         python3 routes_tool.py --entry FILE.gpx [ID]    markdown entry for routes_and_courses.md
Method notes (validated on the 4DP loop: 17 turns with merge_km=0.35 as in the first chat, 19 without; positions/angles within 1-8 degrees):
  * route resampled every 20 m; a sharp turn = heading change >= 55 degrees between the 100 m before and the 100 m after (win);
  * merge_km > 0 merges turns closer than that (keeps the larger angle): merge_km=0.35 reproduces the first chat's counts;
  * elevation is smoothed over 60 m with EDGE padding (zero padding once created fake climbs at every route start) and counted with 2 m hysteresis;
    komoot elevation is noisy, so ascent is only +-10% and the steepest-500 m grade is the safer climb figure;
  * komoot GPX has no surface, crossing or traffic-light data: counts of turns only say how often the road bends.
"""
import re, glob, os, math
import numpy as np
R = 6371000.0
HOME = (50.8438, 6.8942)   # start of the 4dp loop, near home
COMP = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']


def parse(path):
    """GPX -> (lat, lon, ele, name) arrays; accepts lat/lon in either attribute order."""
    txt = open(path, encoding='utf-8').read()
    pts = re.findall(r'<trkpt[^>]*lat="(-?[\d.]+)"[^>]*lon="(-?[\d.]+)"[^>]*>(.*?)</trkpt>', txt, re.S)
    if not pts:   # lon before lat
        pts = [(b, a, c) for a, b, c in re.findall(r'<trkpt[^>]*lon="(-?[\d.]+)"[^>]*lat="(-?[\d.]+)"[^>]*>(.*?)</trkpt>', txt, re.S)]
    la = np.array([float(p[0]) for p in pts]); lo = np.array([float(p[1]) for p in pts])
    el = np.array([float((re.search(r'<ele>(-?[\d.]+)</ele>', p[2]) or [0, 'nan'])[1]) if re.search(r'<ele>', p[2]) else np.nan for p in pts])
    name = (re.search(r'<name>(.*?)</name>', txt, re.S) or [None, ''])[1].strip()
    return la, lo, el, name


def hav(la1, lo1, la2, lo2):
    """Haversine distance in metres."""
    p1, p2 = np.radians(la1), np.radians(la2); dp = p2 - p1; dl = np.radians(lo2 - lo1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def bearing(la1, lo1, la2, lo2):
    """Initial bearing in degrees (0 = north)."""
    p1, p2 = np.radians(la1), np.radians(la2); dl = np.radians(lo2 - lo1)
    y = np.sin(dl) * np.cos(p2); x = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


def compass(b):
    """16-point compass name of a heading in degrees."""
    return COMP[int((b + 11.25) // 22.5) % 16]


def wind_rel(heading, wind_from):
    """Relation of a wind coming FROM `wind_from` (deg; south = 180, west = 270) to a ride heading: headwind ... tailwind."""
    c = math.cos(math.radians(heading - wind_from))
    if c >= 0.7: return 'headwind'
    if c >= 0.35: return 'quartering headwind'
    if c > -0.35: return 'crosswind'
    if c > -0.7: return 'quartering tailwind'
    return 'tailwind'


def _cmean(x):
    return np.degrees(np.angle(np.mean(np.exp(1j * np.radians(x)))))


def analyse(path, step=20.0, thr=55.0, win=100.0, merge_km=0.0):
    """Geometry of one route. Returns dict: name, km, asc, dsc, start, end, close_m, home_km, turns [(km, degrees)], longest_km (longest stretch without a turn),
    maxgrade (steepest 500 m window, %), mingrade, ele_min, ele_max, and the resampled arrays rla, rlo, rel (smoothed ele), s (m), b (bearings)."""
    la, lo, el, name = parse(path)
    d = hav(la[:-1], lo[:-1], la[1:], lo[1:]); cum = np.concatenate([[0], np.cumsum(d)]); L = cum[-1]
    s = np.arange(0, L, step); rla, rlo = np.interp(s, cum, la), np.interp(s, cum, lo)
    rel = np.interp(s, cum, np.nan_to_num(el, nan=np.nanmean(el))) if np.isfinite(el).any() else np.zeros_like(s)
    k = max(1, int(60 / step)); pad = np.pad(rel, (k, k), mode='edge'); sm = np.convolve(pad, np.ones(k) / k, mode='same')[k:-k]
    asc = dsc = 0.0; ref = sm[0]
    for v in sm[1:]:
        if v - ref >= 2.0: asc += v - ref; ref = v
        elif ref - v >= 2.0: dsc += ref - v; ref = v
    w = int(500 / step); g = np.array([(sm[i + w] - sm[i]) / 500 * 100 for i in range(0, len(sm) - w)]) if len(sm) > w else np.array([0.0])
    b = bearing(rla[:-1], rlo[:-1], rla[1:], rlo[1:]); kw = int(win / step); turns = []; i = kw
    while i < len(b) - kw:
        dlt = (_cmean(b[i:i + kw]) - _cmean(b[i - kw:i]) + 180) % 360 - 180
        if abs(dlt) >= thr:
            j = i; best = (abs(dlt), i, dlt)
            while j < len(b) - kw:
                dd = (_cmean(b[j:j + kw]) - _cmean(b[j - kw:j]) + 180) % 360 - 180
                if abs(dd) < thr: break
                if abs(dd) > best[0]: best = (abs(dd), j, dd)
                j += 1
            turns.append((s[best[1]] / 1000, best[2])); i = j + kw
        else: i += 1
    if merge_km > 0:
        m = []
        for p, c in turns:
            if m and p - m[-1][0] < merge_km:
                if abs(c) > abs(m[-1][1]): m[-1] = (p, c)
            else: m.append((p, c))
        turns = m
    gaps = np.diff([0.0] + [t[0] for t in turns] + [L / 1000])
    return dict(name=name, km=L / 1000, asc=asc, dsc=dsc, start=(la[0], lo[0]), end=(la[-1], lo[-1]), close_m=float(hav(la[0], lo[0], la[-1], lo[-1])),
                home_km=float(hav(la[0], lo[0], *HOME) / 1000), turns=turns, longest_km=float(gaps.max()), maxgrade=float(g.max()), mingrade=float(g.min()),
                ele_min=float(np.nanmin(el)) if np.isfinite(el).any() else float('nan'), ele_max=float(np.nanmax(el)) if np.isfinite(el).any() else float('nan'),
                rla=rla, rlo=rlo, rel=sm, s=s, b=b)


def stretches(r, min_km=0.0, by_length=False):
    """Stretches between sharp turns of an analyse() result: list of dicts k0, k1, L (km), hd (mean heading, deg), gr (mean grade %), in route order
    (by_length=True: longest first). The first/last 50 m of each stretch are ignored for heading and grade."""
    s, b, sm = r['s'], r['b'], r['rel']; tk = [0.0] + [t[0] for t in r['turns']] + [r['km']]; out = []
    for i in range(len(tk) - 1):
        lo, hi = tk[i] * 1000, tk[i + 1] * 1000; m = (s[:-1] >= lo + 50) & (s[:-1] < hi - 50)
        if m.sum() < 5 or tk[i + 1] - tk[i] < min_km: continue
        i0 = np.searchsorted(s, lo + 50); i1 = min(np.searchsorted(s, hi - 50), len(sm) - 1)
        out.append(dict(k0=tk[i], k1=tk[i + 1], L=tk[i + 1] - tk[i], hd=float(_cmean(b[m]) % 360), gr=float((sm[i1] - sm[i0]) / max(hi - lo - 100, 1) * 100)))
    return sorted(out, key=lambda x: -x['L']) if by_length else out


def moderate_bends(path, lo=35.0, hi=55.0, **kw):
    """Bends between lo and hi degrees (the ones that are not counted as sharp turns but still cost speed): list of (km, degrees)."""
    return [(k, d) for k, d in analyse(path, thr=lo, **kw)['turns'] if abs(d) < hi]


def loop_closure(path, search_km=8.0, max_gap_m=300.0):
    """For a file that does not close (e.g. komoot export with an approach / extension): find the early point nearest to the end point.
    Returns dict join_km, gap_m, loop_km, loop_asc, loop_dsc, ext_km, loop_ele (min, max) - or {'closed': False} if nothing within max_gap_m."""
    r = analyse(path); s, la, lo, el = r['s'], r['rla'], r['rlo'], r['rel']; d_end = hav(la, lo, la[-1], lo[-1])
    j = int(np.argmin(np.where(s < search_km * 1000, d_end, 1e9)))
    if d_end[j] > max_gap_m: return {'closed': False, 'nearest_gap_m': float(d_end[j])}
    asc = dsc = 0.0; ref = el[j]
    for v in el[j + 1:]:
        if v - ref >= 2.0: asc += v - ref; ref = v
        elif ref - v >= 2.0: dsc += ref - v; ref = v
    return dict(closed=True, join_km=float(s[j] / 1000), gap_m=float(d_end[j]), loop_km=float((s[-1] - s[j]) / 1000), loop_asc=asc, loop_dsc=dsc,
                ext_km=float(s[j] / 1000), loop_ele=(float(el[j:].min()), float(el[j:].max())))


def elevation_diag(path):
    """Data-quality check of the elevation profile: NaNs, range, biggest single-point jump (km), median point spacing, start-end difference, warnings."""
    la, lo, el, name = parse(path); d = hav(la[:-1], lo[:-1], la[1:], lo[1:]); cum = np.concatenate([[0], np.cumsum(d)]); jump = np.abs(np.diff(el))
    out = dict(points=len(la), nan=int(np.isnan(el).sum()), ele_min=float(np.nanmin(el)), ele_max=float(np.nanmax(el)), first=[float(x) for x in np.round(el[:4], 0)],
               max_jump_m=float(np.nanmax(jump)), max_jump_km=float(cum[np.nanargmax(jump)] / 1000), median_step_m=float(np.median(d)), start_end_diff_m=float(el[-1] - el[0]), warnings=[])
    if out['nan']: out['warnings'].append('%d points without elevation (filled with the mean: spikes)' % out['nan'])
    if out['max_jump_m'] > 25: out['warnings'].append('single-point elevation jump of %.0f m at km %.1f (DEM spike): ascent may be inflated' % (out['max_jump_m'], out['max_jump_km']))
    if out['median_step_m'] > 80: out['warnings'].append('sparse points (median %.0f m): elevation and turn detection are coarse' % out['median_step_m'])
    return out


def compare_routes(a, b, show=True, merge_km=0.0):
    """Compare two versions of a route: totals, turn lists (matched within 0.5 km and same direction), long stretches. Returns dict with only_a / only_b turns.
    Turn positions are matched by km, so once two versions diverge in length most later turns show as unmatched: read the totals and stretches first."""
    ra, rb = analyse(a, merge_km=merge_km), analyse(b, merge_km=merge_km)
    def unmatched(x, y): return [(k, d) for k, d in x['turns'] if not any(abs(k - k2) < 0.5 and d * d2 > 0 for k2, d2 in y['turns'])]
    out = dict(only_a=unmatched(ra, rb), only_b=unmatched(rb, ra), a=ra, b=rb)
    if show:
        for tag, r in (('A', ra), ('B', rb)):
            print('%s: %.1f km, +%.0f/-%.0f m, closes %.0f m, %d turns, longest straight %.1f km' % (tag, r['km'], r['asc'], r['dsc'], r['close_m'], len(r['turns']), r['longest_km']))
            print('   stretches >= 2.5 km: ' + '; '.join('%.1f-%.1f (%.1f km, %.0f deg %s, %+.1f%%)' % (x['k0'], x['k1'], x['L'], x['hd'], compass(x['hd']), x['gr']) for x in stretches(r, 2.5)))
        print('turns only in A:', ['%.1f(%+.0f)' % t for t in out['only_a']]); print('turns only in B:', ['%.1f(%+.0f)' % t for t in out['only_b']])
    return out


def route_entry_md(cid, path, title=None, src='', note='', good='', kind='ride'):
    """Markdown entry for routes_and_courses.md following the file's template (geometry computed; surface/crossings must be added by hand)."""
    r = analyse(path); st = stretches(r, by_length=True); fmt = lambda x: '%.1f km from km %.1f heading %.0f deg (%s), %+.1f%%' % (x['L'], x['k0'], x['hd'], compass(x['hd']), x['gr'])
    L = ['### %s: %s (%s)' % (cid, title or r['name'] or os.path.basename(path), src),
         '- Type: %s, %s, %.1f km, +%.0f/-%.0f m (my 60 m smoothing, 2 m hysteresis; komoot\'s own figure differs), steepest 500 m %+.1f%%, closing gap %.0f m.' % (
             kind, 'loop' if r['close_m'] < 300 else 'point-to-point / open', r['km'], r['asc'], r['dsc'], r['maxgrade'], r['close_m']),
         '- Start: %.4f N, %.4f E (%.1f km from home); highest point %.0f m.' % (r['start'][0], r['start'][1], r['home_km'], r['ele_max']),
         '- Surface/traffic/lights: not in the GPX (check komoot before use).',
         '- Geometry: %d sharp turns (>= 55 degrees within 100 m), %.2f per km; longest straights: %s.' % (len(r['turns']), len(r['turns']) / r['km'], '; '.join(fmt(x) for x in st[:3]))]
    if st and st[0]['L'] >= 4:
        h = st[0]['hd']; L.append('- Wind (longest straight, %.1f km, heading %.0f deg): south wind = %s; west wind = %s; reversed direction flips these.' % (st[0]['L'], h, wind_rel(h, 180), wind_rel(h, 270)))
    if note: L.append('- Notes: ' + note)
    if good: L.append('- Good for: ' + good)
    L.append('- Status: GPX imported (date to add); not yet ridden as part of the plan.')
    return '\n'.join(L)


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if args[:1] == ['--compare'] and len(args) == 3: compare_routes(args[1], args[2])
    elif args[:1] == ['--diag'] and len(args) == 2: print(elevation_diag(args[1]))
    elif args[:1] == ['--entry'] and len(args) >= 2: print(route_entry_md(args[2] if len(args) > 2 else 'C?', args[1]))
    else:
        for f in sorted(glob.glob(os.path.join(args[0] if args else 'gpx', '*.gpx'))):
            r = analyse(f)
            print('%-62s %6.1f km +%4.0f/-%4.0f  turns>=55: %2d  longest %5.1f km  start %.4f,%.4f (%5.1f km from home)  closes %5.0f m  steepest500m %4.1f%%' % (
                os.path.basename(f)[:62], r['km'], r['asc'], r['dsc'], len(r['turns']), r['longest_km'], r['start'][0], r['start'][1], r['home_km'], r['close_m'], r['maxgrade']))
