"""Layout census of an ebusd raw log (Ariston Bridgenet). Usage: census.py RAWLOG [ARISTON_CSV]"""
import re, sys
from collections import Counter, defaultdict

RE = re.compile(r"^(\S+ \S+) <([0-9a-f]+)$")


def unescape(b):
    out, i = [], 0
    while i < len(b):
        if b[i] == 0xA9 and i + 1 < len(b):
            out.append(0xA9 if b[i + 1] == 0 else 0xAA)
            i += 2
        else:
            out.append(b[i]); i += 1
    return out


def width(rid):
    b = int(rid[:2], 16)
    if b <= 0x1F or 0xC0 <= b <= 0xDF:
        return 1
    if 0x40 <= b <= 0x7F:
        return 2
    return None


def is_master(a):
    lo, hi = a & 0xF, a >> 4
    return lo in (0, 1, 3, 7, 0xF) and hi in (0, 1, 3, 7, 0xF)


def parse(b):
    if len(b) < 6:
        return None
    qq, zz, pb, sb, nn = b[:5]
    if len(b) < 5 + nn + 1:
        return None
    data = b[5:5 + nn]
    t = dict(qq=qq, zz=zz, pbsb=f"{pb:02x}{sb:02x}", data=data, resp=None)
    rest = b[5 + nn + 1:]
    if zz != 0xFE and not is_master(zz) and len(rest) >= 2:
        n2 = rest[1]
        if len(rest) >= 2 + n2:
            t["resp"] = rest[2:2 + n2]
    return t


def ids_of(t):
    d, p = t["data"], t["pbsb"]
    h = lambda i: f"{d[i]:02x}{d[i+1]:02x}"
    if p in ("2000", "2001"):
        return [h(i) for i in range(0, len(d) - 1, 2)]
    if p in ("200f", "2010"):
        ids, i = [], 0
        while i + 1 < len(d):
            rid = h(i); w = width(rid)
            if w is None:
                ids.append(rid + "?"); break
            ids.append(rid); i += 2 + w + 1
        return ids
    if p == "2020":
        ids, i = [], 0
        while i + 1 < len(d):
            rid = h(i); w = width(rid)
            if w is None:
                ids.append(rid + "?"); break
            ids.append(rid); i += 2 + w
        return ids
    if p == "200e":
        return [h(0)] if len(d) >= 2 else []
    return []


def main():
    lay = Counter()
    first = {}
    for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
        m = RE.match(line.strip())
        if not m:
            continue
        raw = bytes.fromhex(m.group(2)) if len(m.group(2)) % 2 == 0 else None
        if raw is None:
            continue
        t = parse(unescape(list(raw)))
        if not t or t["pbsb"][:2] != "20":
            continue
        key = (f"{t['qq']:02x}", f"{t['zz']:02x}", t["pbsb"], "+".join(ids_of(t)))
        lay[key] += 1
        first.setdefault(key, (m.group(1), m.group(2)))
    # which layouts does the current config key on? (ZZ, PBSB, ID prefix)
    keys = []
    if len(sys.argv) > 2:
        for row in open(sys.argv[2], encoding="utf-8"):
            if row.startswith(("u,", "b,")):
                f = row.split(",")
                keys.append((f[0], f[2], f[4], f[5], f[6], f[7]))
    for (qq, zz, pbsb, ids), n in sorted(lay.items(), key=lambda kv: (kv[0][2], kv[0][0], -kv[1])):
        idhex = ids.replace("+", "")
        hit = [k[1] for k in keys if k[3] == zz and k[4] == pbsb and (not k[2] or k[2] == qq)
               and idhex.startswith(k[5])]
        print(f"{qq} {zz} {pbsb} {n:4d}  {ids:40s} {'<- ' + ','.join(hit) if hit else ''}")


main()
