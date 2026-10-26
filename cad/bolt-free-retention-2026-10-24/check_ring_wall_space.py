from pathlib import Path
f=Path(__file__).resolve().parent/'verify_r7.py'
exec(f.read_text().split("p,rings,h=read(")[0])
p,rr,h=read(r/'Thruster-R7-bolt-free.step')
band=t.boolean(t.BRepAlgoAPI_Cut,cylinder(23,(0,-5.5,0),(0,1,0),8.85),cylinder(21.05,(0,-5.6,0),(0,1,0),9.05))
for n in ('propeller','nozzle','cover','stator'):
 v=t.volume(t.boolean(t.BRepAlgoAPI_Common,band,p[n]));gap=t.distance(band,p[n]);print(n,'overlap',v,'gap',gap,flush=True)
