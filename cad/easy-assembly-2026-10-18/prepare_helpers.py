"""Specialize the established STEP/export checks for this five-panel revision."""
from pathlib import Path
R=Path(__file__).resolve().parent
old=R.parent/'laser-frame-electronics-2026-10-17'
s=(old/'merge_native_assembly.py').read_text()
s=s.replace('Laser-cut frame and electronics pod','Easy frame and removable electronics pod')
s=s.replace('ROV - laser-cut frame and electronics cylinder','ROV - easy assembly - five panels')
s=s.replace('ROV-frame-and-cylinder.step','ROV-easy-assembly.step').replace('solids==415','solids==368')
(R/'merge_easy_assembly.py').write_text(s)
s=(old/'verify_cut_and_flow.py').read_text().replace('len(proof)==8','len(proof)==5')
s=s.replace('all eight DXFs','all five DXFs')
(R/'verify_cut_and_flow.py').write_text(s)
s=(old/'render_and_package.py').read_text()
s=s.replace('LASER-CUT ROV FRAME + ELECTRONICS CYLINDER','EASY-ASSEMBLY ROV')
s=s.replace('3 mm aluminum  |  Eight thrusters  |  OD160 x 200 mm hollow tube','5 panels  |  8 M4 frame joints  |  2 release straps')
s=s.replace('frame-and-cylinder-preview.png','easy-assembly-preview.png')
s=s.replace("(1500,1100)","(1300,850)")
s=s.replace('LASER-CUT FRAME PARTS - 3 mm ALUMINUM','THREE CUT SHAPES - FIVE 3 mm ALUMINUM PANELS')
s=s.replace('DXFs use millimetres at 1:1 scale. These profiles are not nested on stock.','Cut one base, two identical side plates, and two identical saddles. DXFs use millimetres.')
start=s.index('positions=[(45,115,.88)')
end=s.index('    width,height=',start)
s=s[:start]+"positions=[(45,115,.9),(650,135,1.9),(650,450,1.9)]\nunique=[meta['laser_cut_parts'][i] for i in (0,1,3)]\nfor panel,(ox,oy,scale) in zip(unique,positions):\n"+s[end:]
s=s.replace("panel['name'].split('-')[0]","{'E01':'A - BASE x1','E02':'B - SIDE PLATE x2','E04':'C - OPEN SADDLE x2'}[panel['name'].split('-')[0]]")
s=s.replace('eight cutting profiles','three unique cutting profiles')
(R/'render_easy_assembly.py').write_text(s)
print('Prepared native STEP merge, cutting/flow verification and render helpers.')
