from pathlib import Path
import shutil
r=Path(__file__).resolve().parent;base=r.parent/'shaft-clamp-r8-2026-10-25'
s=(base/'package_prints.py').read_text()
for a,b in [('Fan-R8-M3-axle-clamp.stl','Fan-R9-forward-fan.stl'),('Upper-jaw-R8-M3-axle-clamp.stl','Upper-jaw-R9-M3-axle-clamp.stl'),('TEST-FIRST-R8-lower-jaw.stl','TEST-FIRST-R9-lower-jaw.stl'),('R8-M3-Axle-Clamp-Print-Kit.zip','R9-Forward-Fan-Print-Kit.zip'),('Thruster-R8-M3-axle-clamp.step','Thruster-R9-forward-fan.step'),('R8-clamp-detail.png','R9-side-layout.png'),('R8-complete-assembly.png','R9-complete-assembly.png')]:s=s.replace(a,b)
s=s.replace("('Fan-R9-forward-fan.stl',90)","('Fan-R9-forward-fan.stl',-90)")
(r/'package_prints.py').write_text(s)
shutil.copyfile(base/'Upper-jaw-R8-M3-axle-clamp.stl',r/'Upper-jaw-R9-M3-axle-clamp.stl')
print('R9 package builder prepared; unchanged upperjaw mesh copied')
