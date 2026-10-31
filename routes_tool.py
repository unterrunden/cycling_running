import re, glob, os, math
import numpy as np
R = 6371000.0
HOME = (50.8438, 6.8942)   # 4dp start, near home

def parse(path):
    txt = open(path, encoding='utf-8').read()
    pts = re.findall(r'<trkpt[^>]*lat="(-?[\d.]+)"[^>]*lon="(-?[\d.]+)"[^>]*>(.*?)</trkpt>', txt, re.S)
    if not pts:   # lon before lat
        pts = [(b, a, c) for a, b, c in re.findall(r'<trkpt[^>]*lon="(-?[\d.]+)"[^>]*lat="(-?[\d.]+)"[^>]*>(.*?)</trkpt>', txt, re.S)]
    la = np.array([float(p[0]) for p in pts]); lo = np.array([float(p[1]) for p in pts])
    el = np.array([float((re.search(r'<ele>(-?[\d.]+)</ele>', p[2]) or [0, 'nan'])[1]) if re.search(r'<ele>', p[2]) else np.nan for p in pts])
    name = (re.search(r'<name>(.*?)</name>', txt, re.S) or [None, ''])[1].strip()
    return la, lo, el, name

def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2); dp = p2 - p1; dl = np.radians(lo2 - lo1)
    a = np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

def bearing(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2); dl = np.radians(lo2 - lo1)
    y = np.sin(dl)*np.cos(p2); x = np.cos(p1)*np.sin(p2) - np.sin(p1)*np.cos(p2)*np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360

def analyse(path, step=20.0, thr=55.0, win=100.0):
    la, lo, el, name = parse(path)
    d = hav(la[:-1], lo[:-1], la[1:], lo[1:]); cum = np.concatenate([[0], np.cumsum(d)])
    L = cum[-1]
    s = np.arange(0, L, step)                       # resample every `step` m
    rla, rlo = np.interp(s, cum, la), np.interp(s, cum, lo)
    rel = np.interp(s, cum, np.nan_to_num(el, nan=np.nanmean(el))) if np.isfinite(el).any() else np.zeros_like(s)
    # ascent / descent on 50 m-smoothed elevation, 1 m hysteresis
    k = max(1, int(60/step)); pad = np.pad(rel, (k, k), mode='edge'); sm = np.convolve(pad, np.ones(k)/k, mode='same')[k:-k]
    asc = dsc = 0.0; ref = sm[0]
    for v in sm[1:]:
        if v - ref >= 2.0: asc += v - ref; ref = v
        elif ref - v >= 2.0: dsc += ref - v; ref = v
    # grade over 200 m windows
    g = []
    w = int(500/step)
    for i in range(0, len(sm)-w): g.append((sm[i+w]-sm[i])/500*100)
    g = np.array(g) if g else np.array([0.0])
    # turns: heading change between the stretch before and after, each `win` metres long
    b = bearing(rla[:-1], rlo[:-1], rla[1:], rlo[1:])
    kw = int(win/step)
    turns = []
    i = kw
    while i < len(b) - kw:
        b1 = np.degrees(np.angle(np.mean(np.exp(1j*np.radians(b[i-kw:i])))))
        b2 = np.degrees(np.angle(np.mean(np.exp(1j*np.radians(b[i:i+kw])))))
        dlt = (b2 - b1 + 180) % 360 - 180
        if abs(dlt) >= thr:
            j = i; best = (abs(dlt), i, dlt)
            while j < len(b) - kw and True:
                b1 = np.degrees(np.angle(np.mean(np.exp(1j*np.radians(b[j-kw:j]))))); b2 = np.degrees(np.angle(np.mean(np.exp(1j*np.radians(b[j:j+kw])))))
                dd = (b2 - b1 + 180) % 360 - 180
                if abs(dd) < thr: break
                if abs(dd) > best[0]: best = (abs(dd), j, dd)
                j += 1
            turns.append((s[best[1]]/1000, best[2])); i = j + kw
        else:
            i += 1
    tk = [0.0] + [t[0] for t in turns] + [L/1000]
    gaps = np.diff(tk)
    return dict(name=name, km=L/1000, asc=asc, dsc=dsc, start=(la[0], lo[0]), end=(la[-1], lo[-1]),
                close_m=float(hav(la[0], lo[0], la[-1], lo[-1])), home_km=float(hav(la[0], lo[0], *HOME)/1000),
                turns=turns, longest_km=float(gaps.max()), maxgrade=float(g.max()), mingrade=float(g.min()),
                ele_min=float(np.nanmin(el)) if np.isfinite(el).any() else float('nan'), ele_max=float(np.nanmax(el)) if np.isfinite(el).any() else float('nan'),
                rla=rla, rlo=rlo, rel=sm, s=s, b=b)

if __name__ == '__main__':
    import sys
    for f in sorted(glob.glob('gpx/*')):
        r = analyse(f)
        print('%-62s %6.1f km +%4.0f/-%4.0f  turns>=55: %2d  longest %5.1f km  start %.4f,%.4f (%5.1f km from home)  closes %5.0f m  maxgrade %4.1f%%' % (
            os.path.basename(f)[:62], r['km'], r['asc'], r['dsc'], len(r['turns']), r['longest_km'], r['start'][0], r['start'][1], r['home_km'], r['close_m'], r['maxgrade']))
