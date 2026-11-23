import sys
rows=[]
for fn in sys.argv[1:]:
    for l in open(fn,encoding="utf-8"):
        if l.startswith(("u,","b,")):
            f=l.split(","); rows.append((fn.split("/")[-1],f[0],f[1],f[2],f[4],f[5],f[6],f[7],len(f)))
names={}
for r in rows:
    k=(r[2],r[3]); 
    if k in names: print("DUP NAME",k,names[k],r[0])
    names[k]=r[0]
for i,a in enumerate(rows):
    for b in rows[i+1:]:
        if a[5]==b[5] and a[6]==b[6] and (a[7].startswith(b[7]) or b[7].startswith(a[7])):
            print("KEY", a[0],a[3],a[7],"|",b[0],b[3],b[7])
print(len(rows),"definitions")
