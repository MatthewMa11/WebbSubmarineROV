from pathlib import Path
import sys,json,math
from zipfile import ZipFile,ZIP_DEFLATED
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[2]/'robotic FTC 2026-2027/cad/.vendor'))
sys.path.insert(0,str(R.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
import vtk
from PIL import Image,ImageDraw,ImageFont

meta=json.loads((R/'frame-pod-verification.json').read_text())
layout=json.loads((R.parent/'eight-thruster-assembly-2026-10-17/assembly-verification.json').read_text())
def limits(s):
    b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
    return [[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
def poly_from_file(file):
    rd=vtk.vtkSTLReader();rd.SetFileName(str(file));rd.Update()
    poly=vtk.vtkPolyData();poly.DeepCopy(rd.GetOutput());return poly
new=[];cache=R/'preview-STL';cache.mkdir(exist_ok=True)
for item in meta['added_parts']:
    shape=TopoDS_Shape();assert BRepTools.Read_s(shape,str(R/'native-breps'/(item['name']+'.brep')),BRep_Builder())
    mesh=BRepMesh_IncrementalMesh(shape,.13,False,.24,True);mesh.Perform()
    filename=cache/(item['name']+'.stl');w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(shape,str(filename))
    new.append((item,poly_from_file(filename)))
p,h=read(layout['source_file']);oldmesh=R.parent/'eight-thruster-assembly-2026-10-17/preview-meshes'
colors={'nozzle':(.15,.19,.23),'cover':(.48,.51,.54),'propeller':(.28,.41,.53),'rotor':(.28,.52,.69),'stator':(.76,.59,.20),'insert':(.25,.28,.32)}
source=[]
for name,shape in list(p.items())+[(f'fastener-{i}',s) for i,s in enumerate(h)]:
    lo,hi=limits(shape);dims=[b-a for a,b in zip(lo,hi)]
    shifted=name.startswith('fastener') and ((abs(dims[2]-.8)<.01 and abs(dims[0]-9)<.01) or (abs(dims[2]-16)<.01 and 7<dims[0]<7.4))
    source.append((poly_from_file(oldmesh/(name+'.stl')),colors.get(name,(.34,.35,.36)),shifted))
def actor(poly,color,transform=None,opacity=1):
    m=vtk.vtkPolyDataMapper();m.SetInputData(poly);a=vtk.vtkActor();a.SetMapper(m)
    a.GetProperty().SetColor(*color);a.GetProperty().SetOpacity(opacity);a.GetProperty().SetSpecular(.3);a.GetProperty().SetSpecularPower(25)
    if transform:a.SetUserMatrix(transform)
    return a
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1500,1040);window.SetMultiSamples(4)
ren=vtk.vtkRenderer();ren.SetBackground(.96,.975,.985);window.AddRenderer(ren)
for e in layout['placements']:
    for poly,color,shifted in source:
        mat=vtk.vtkMatrix4x4();mat.Identity();m=e['transform_3x4']
        for i in range(3):
            for j in range(4):mat.SetElement(i,j,m[i][j]-(3*m[i][2] if shifted and j==3 else 0))
        ren.AddActor(actor(poly,color,mat))
for item,poly in new:ren.AddActor(actor(poly,item['color'],opacity=.36 if item['name'].startswith('POD01') else 1))
cam=ren.GetActiveCamera();cam.SetFocalPoint(0,0,45);cam.SetPosition(650,-930,660);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();ren.ResetCamera();cam.Zoom(.95)
for text,y,size in [('EASY-ASSEMBLY ROV',984,29),('5 panels  |  8 M4 frame joints  |  2 release straps',945,21)]:
    a=vtk.vtkTextActor();a.SetInput(text);a.SetPosition(30,y);a.GetTextProperty().SetFontSize(size);a.GetTextProperty().SetColor(.07,.18,.26)
    if size==29:a.GetTextProperty().BoldOn()
    ren.AddViewProp(a)
window.Render();im=vtk.vtkWindowToImageFilter();im.SetInput(window);im.SetInputBufferTypeToRGB();im.ReadFrontBufferOff();im.Update()
png=vtk.vtkPNGWriter();png.SetFileName(str(R/'easy-assembly-preview.png'));png.SetInputConnection(im.GetOutputPort());png.Write();window.Finalize()

# A labelled cutting-profile proof; the DXFs themselves contain CUT lines only.
im=Image.new('RGB',(1300,850),'white');draw=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);large=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',30)
draw.text((30,16),'THREE CUT SHAPES - FIVE 3 mm ALUMINUM PANELS',font=large,fill=(20,45,64))
draw.text((30,57),'Cut one base, two identical side plates, and two identical saddles. DXFs use millimetres.',font=font,fill=(65,80,91))
positions=[(45,115,.9),(650,135,1.9),(650,450,1.9)]
unique=[meta['laser_cut_parts'][i] for i in (0,1,3)]
for panel,(ox,oy,scale) in zip(unique,positions):
    width,height=panel['flat_size_mm']
    def xy(v):return (ox+v[0]*scale,oy+(height-v[1])*scale)
    for path in panel['paths']:
        if path['type']=='line':draw.line([xy(path['p1']),xy(path['p2'])],fill=(30,80,119),width=2)
        elif path['type']=='circle':
            x,y=xy(path['center']);rad=path['radius']*scale;draw.ellipse((x-rad,y-rad,x+rad,y+rad),outline=(30,80,119),width=2)
        elif path['type']=='arc':
            a=path['start_deg'];b=path['end_deg']
            if b<a:b+=360
            pts=[xy([path['center'][0]+path['radius']*math.cos(math.radians(a+(b-a)*i/100)),path['center'][1]+path['radius']*math.sin(math.radians(a+(b-a)*i/100))]) for i in range(101)]
            draw.line(pts,fill=(30,80,119),width=2)
    draw.text((ox,oy+height*scale+12),{'E01':'A - BASE x1','E02':'B - SIDE PLATE x2','E04':'C - OPEN SADDLE x2'}[panel['name'].split('-')[0]],font=font,fill=(20,45,64))
    draw.text((ox,oy+height*scale+39),f'{width:.0f} x {height:.0f} mm',font=font,fill=(65,80,91))
im.save(R/'laser-cut-profile-preview.png')
print('Rendered assembled frame and three unique cutting profiles.')
