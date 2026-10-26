from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parents[2]/'robotic FTC 2026-2027/cad/.vendor'))
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
import vtk
report=json.loads((r/'assembly-verification.json').read_text())
parts,hardware=read(report['source_file'])
meshes=r/'preview-meshes';meshes.mkdir(exist_ok=True)
data=[]
colors={'nozzle':(.18,.24,.29),'cover':(.48,.51,.54),'propeller':(.28,.41,.53),
        'rotor':(.28,.52,.69),'stator':(.76,.59,.20),'insert':(.25,.28,.32)}
for name,shape in list(parts.items())+[(f'fastener-{i}',s) for i,s in enumerate(hardware)]:
    path=meshes/(name+'.stl')
    if not path.exists():
        m=BRepMesh_IncrementalMesh(shape,.15,False,.35,True);m.Perform()
        w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(shape,str(path))
    rd=vtk.vtkSTLReader();rd.SetFileName(str(path));rd.Update()
    poly=vtk.vtkPolyData();poly.DeepCopy(rd.GetOutput())
    data.append((poly,colors.get(name,(.34,.35,.36))))
w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1500,920);w.SetMultiSamples(4)
for side in range(2):
    ren=vtk.vtkRenderer();ren.SetViewport(side*.5,0,(side+1)*.5,1);ren.SetBackground(.96,.975,.985)
    for e in report['placements']:
        mat=vtk.vtkMatrix4x4();mat.Identity()
        for i in range(3):
            for j in range(4):mat.SetElement(i,j,e['transform_3x4'][i][j])
        for poly,color in data:
            mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
            actor=vtk.vtkActor();actor.SetMapper(mapper);actor.SetUserMatrix(mat)
            actor.GetProperty().SetColor(*color);actor.GetProperty().SetSpecular(.23);actor.GetProperty().SetSpecularPower(24)
            ren.AddActor(actor)
        label=vtk.vtkBillboardTextActor3D();label.SetInput(e['tag']+(' UP' if e['axis'][2]>0 else ' DOWN' if e['axis'][2]<0 else ''))
        label.SetPosition(e['origin_mm'][0],e['origin_mm'][1],75)
        label.GetTextProperty().SetFontSize(18);label.GetTextProperty().SetColor(.06,.19,.27);label.GetTextProperty().BoldOn();ren.AddActor(label)
    cam=ren.GetActiveCamera();cam.SetFocalPoint(0,0,0)
    if side==0:cam.SetPosition(560,-720,650);cam.SetViewUp(0,0,1)
    else:cam.SetPosition(0,0,900);cam.SetViewUp(0,1,0)
    cam.ParallelProjectionOn();ren.ResetCamera();cam.Zoom(.88)
    title=vtk.vtkTextActor();title.SetInput('EIGHT THRUSTERS - R3' if side==0 else 'TOP VIEW - FOUR CORNER AXES')
    title.SetPosition(26,865);title.GetTextProperty().SetFontSize(25);title.GetTextProperty().SetColor(.07,.18,.26);title.GetTextProperty().BoldOn();ren.AddViewProp(title)
    subtitle=vtk.vtkTextActor();subtitle.SetInput('4 diagonal + 2 up + 2 down' if side==0 else 'Overall envelope: 488 x 446 x 108 mm')
    subtitle.SetPosition(26,827);subtitle.GetTextProperty().SetFontSize(19);subtitle.GetTextProperty().SetColor(.22,.33,.40);ren.AddViewProp(subtitle)
    w.AddRenderer(ren)
w.Render();img=vtk.vtkWindowToImageFilter();img.SetInput(w);img.SetInputBufferTypeToRGB();img.ReadFrontBufferOff();img.Update()
out=vtk.vtkPNGWriter();out.SetFileName(str(r/'eight-thruster-preview.png'));out.SetInputConnection(img.GetOutputPort());out.Write();w.Finalize()
print(r/'eight-thruster-preview.png')
