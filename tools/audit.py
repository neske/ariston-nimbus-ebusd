"""Compare our observed layouts (layouts_ours.txt) with the layout each ariston.csv definition was made for."""
import re, sys

defs = []
prev = None
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"# (\w{4}) (?:read of|broadcast) ([0-9a-f+]+);", line)
    if m:
        prev = (m.group(1), m.group(2)); continue
    if line.startswith(("u,", "b,")):
        f = line.rstrip("\n").split(",")
        named = [f[i] for i in range(8, len(f), 6) if f[i]]
        defs.append(dict(kind=f[0], circ=f[1], name=f[2], qq=f[4], zz=f[5], pbsb=f[6], id=f[7],
                         layout=prev[1] if prev else "?", fields=named))
ours = []
for line in open(sys.argv[2], encoding="utf-8"):
    p = line.split()
    if len(p) >= 5 and "+" in p[4] or (len(p) >= 5 and re.fullmatch(r"[0-9a-f]{4}", p[4] or "")):
        ours.append((p[0], p[1], p[2], int(p[3]), p[4]))
for d in defs:
    hits = [o for o in ours if o[1] == d["zz"] and o[2] == d["pbsb"] and (not d["qq"] or d["qq"] == o[0])
            and o[4].replace("+", "").startswith(d["id"])]
    for o in hits:
        same = o[4] == d["layout"]
        print(f"{'OK  ' if same else 'DIFF'} {d['circ']}.{d['name']:34s} theirs={d['layout']:28s} ours={o[0]}>{o[1]} {o[4]} x{o[3]}  fields={'/'.join(d['fields'])}")
