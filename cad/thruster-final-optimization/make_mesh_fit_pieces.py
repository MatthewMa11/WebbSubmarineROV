"""Crop closed native print meshes into inexpensive, full-scale fit pieces."""
import sys,json,zipfile,math
from pathlib import Path
OLD=Path('C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/frame-fit-check')
sys.path.insert(0,str(OLD.parent/'.vendor'))
import vtk

r=Path(__file__).resolve().parent
full=r/'full-print-parts';small=r/'fit-check-first'
full.mkdir(exist_ok=True);small.mkdir(exist_ok=True)
with zipfile.ZipFile(OLD/'A2212-final-checked-parts.zip') as z:
    for name in ('Propeller-M3x8-socket-head.stl','Motor-insert-M3-pilots.stl','Front-cover-original-final-audit.stl'):
        (full/name).write_bytes(z.read(name))
(full/'Nozzle-PLA-complete.stl').write_bytes((r/'Nozzle-PLA-complete.stl').read_bytes())

def load(name):
    a=vtk.vtkSTLReader();a.SetFileName(str(full/name));a.MergingOn();a.Update()
    out=vtk.vtkPolyData();out.DeepCopy(a.GetOutput());return out

def crop(poly,bounds):
    planes=vtk.vtkPlaneCollection()
    # vtkClipClosedSurface retains the positive half-space of each plane.
    for i,side in enumerate(bounds):
        if side is None:continue
        axis=i//2;origin=[0.,0.,0.];origin[axis]=side
        normal=[0.,0.,0.];normal[axis]=1 if i%2==0 else -1
        plane=vtk.vtkPlane();plane.SetOrigin(*origin);plane.SetNormal(*normal);planes.AddItem(plane)
    f=vtk.vtkClipClosedSurface();f.SetInputData(poly);f.SetClippingPlanes(planes)
    f.GenerateFacesOn();f.TriangulationErrorDisplayOn();f.SetTolerance(1e-6);f.Update()
    out=vtk.vtkPolyData();out.DeepCopy(f.GetOutput());assert out.GetNumberOfCells()>0
    return out

def finish(poly,angle,path):
    tr=vtk.vtkTransform();tr.RotateX(angle)
    f=vtk.vtkTransformPolyDataFilter();f.SetInputData(poly);f.SetTransform(tr);f.Update()
    move=vtk.vtkTransform();move.Translate(0,0,-f.GetOutput().GetBounds()[4])
    g=vtk.vtkTransformPolyDataFilter();g.SetInputConnection(f.GetOutputPort());g.SetTransform(move);g.Update()
    triangles=vtk.vtkTriangleFilter();triangles.SetInputConnection(g.GetOutputPort());triangles.Update()
    clean=vtk.vtkCleanPolyData();clean.SetInputConnection(triangles.GetOutputPort());clean.SetTolerance(0);clean.Update()
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(clean.GetOutputPort())
    normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.SplittingOff();normals.Update()
    out=normals.GetOutput()
    edges=vtk.vtkFeatureEdges();edges.SetInputData(out);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
    con=vtk.vtkPolyDataConnectivityFilter();con.SetInputData(out);con.SetExtractionModeToAllRegions();con.Update()
    mass=vtk.vtkMassProperties();mass.SetInputData(out);mass.Update()
    info={'file':path.name,'triangles':out.GetNumberOfCells(),'bad_edges':edges.GetOutput().GetNumberOfCells(),
          'components':con.GetNumberOfExtractedRegions(),'volume_mm3':mass.GetVolume(),'bounds_mm':list(out.GetBounds()),'scale':1}
    assert info['bad_edges']==0 and info['components']==1 and info['volume_mm3']>1,info
    writer=vtk.vtkSTLWriter();writer.SetInputData(out);writer.SetFileName(str(path));writer.SetFileTypeToBinary();assert writer.Write()==1
    return info

nozzle=load('Nozzle-PLA-complete.stl');prop=load('Propeller-M3x8-socket-head.stl');insert=load('Motor-insert-M3-pilots.stl')
disk=vtk.vtkDiskSource();disk.SetInnerRadius(1.75);disk.SetOuterRadius(6);disk.SetCircumferentialResolution(128);disk.SetRadialResolution(1);disk.Update()
extrude=vtk.vtkLinearExtrusionFilter();extrude.SetInputConnection(disk.GetOutputPort());extrude.SetExtrusionTypeToVectorExtrusion();extrude.SetVector(0,0,1);extrude.SetScaleFactor(15);extrude.CappingOn();extrude.Update()
def motor_gauge():
    # A simple seating gauge copies the exact 19 x 16 mm pattern, 5 mm mount
    # thickness, 7.6 mm access diameter and 3.3 mm clearance bores. Omitting the
    # curved tail shell avoids a fragile mesh trim through its nested cavities.
    from verify_pla_revision import t
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    from OCP.BRepCheck import BRepCheck_Analyzer
    s=BRepPrimAPI_MakeBox(t.gp_Pnt(-15,-15,0),30,30,8.9).Shape()
    for x,y in ((9.5,0),(-9.5,0),(0,8),(0,-8)):
        for radius,z,h in ((1.65,-.01,8.92),(3.8,-.01,3.91)):
            c=t.BRepPrimAPI_MakeCylinder(t.gp_Ax2(t.gp_Pnt(x,y,z),t.gp_Dir(0,0,1)),radius,h).Shape()
            s=t.boolean(t.BRepAlgoAPI_Cut,s,c)
    assert BRepCheck_Analyzer(s).IsValid()
    m=BRepMesh_IncrementalMesh(s,.015,False,.12,True);m.Perform()
    path=r/'motor-seating-gauge-source.stl';w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(s,str(path))
    a=vtk.vtkSTLReader();a.SetFileName(str(path));a.Update();out=vtk.vtkPolyData();out.DeepCopy(a.GetOutput());return out

def captive_gauge():
    from verify_pla_revision import t
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Vec
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCP.TopAbs import TopAbs_EDGE
    s=t.BRepPrimAPI_MakeCylinder(t.gp_Ax2(t.gp_Pnt(0,0,0),t.gp_Dir(0,0,1)),6,10.25).Shape()
    for radius,z,h in ((1.65,-.01,10.27),(3.8,9.25,1.01)):
        tool=t.BRepPrimAPI_MakeCylinder(t.gp_Ax2(t.gp_Pnt(0,0,z),t.gp_Dir(0,0,1)),radius,h).Shape()
        s=t.boolean(t.BRepAlgoAPI_Cut,s,tool)
    poly= BRepBuilderAPI_MakePolygon()
    for i in range(6):
        a=math.radians(30+60*i);rr=5.8/math.sqrt(3)
        poly.Add(t.gp_Pnt(rr*math.cos(a),rr*math.sin(a),-.01))
    poly.Close();tool=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(),gp_Vec(0,0,7.41)).Shape()
    s=t.boolean(t.BRepAlgoAPI_Cut,s,tool)
    fillet=BRepFilletAPI_MakeFillet(s);ex=t.TopExp_Explorer(s,TopAbs_EDGE);count=0;seen=[]
    while ex.More():
        e=t.TopoDS.Edge(ex.Current());ex.Next();curve=BRepAdaptor_Curve(e);lo,hi=t.limits(e)
        if any(e.IsSame(q) for q in seen):continue
        seen.append(e)
        circle=str(curve.GetType()).endswith('Circle') and abs(curve.Circle().Radius()-3.8)<1e-6
        line=str(curve.GetType()).endswith('Line') and hi[2]-lo[2]>1 and abs(math.hypot(lo[0],lo[1])-5.8/math.sqrt(3))<1e-5
        if circle or line:fillet.Add(.15,e);count+=1
    assert count==8,count
    fillet.Build();assert fillet.IsDone();s=fillet.Shape();assert BRepCheck_Analyzer(s).IsValid()
    m=BRepMesh_IncrementalMesh(s,.015,False,.12,True);m.Perform()
    path=r/'cover-captive-gauge-source.stl';w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(s,str(path))
    a=vtk.vtkSTLReader();a.SetFileName(str(path));a.Update();out=vtk.vtkPolyData();out.DeepCopy(a.GetOutput());return out
jobs=[
 ('A-motor-guide-drive-keys.stl',lambda:crop(prop,(None,None,None,None,-18.2,18.2)),-90,'Native hub mating geometry; two short blade-root stubs remain.'),
 ('B-motor-insert.stl',lambda:insert,90,'Actual unchanged motor insert; prepare its four M3 pilots.'),
 ('C-M4-mount-pad.stl',lambda:crop(nozzle,(-22,22,-12,12,-51,-42)),0,'Actual mounting pad crop; use the four corner bolt positions.'),
 ('D-shaft-bore-3p5mm.stl',lambda:extrude.GetOutput(),0,'Nominal 3.5 mm x 15 mm bore gauge; not a redesigned gray cover.'),
 ('E-cover-captive-nut-seat.stl',captive_gauge,0,'Nominal replica of the nozzle retention pocket: exact AF5.8 nut seat, washer seat and 0.15 mm rounds; outside shell omitted.'),
 ('F-motor-base-washer-seats.stl',motor_gauge,180,'Nominal seating gauge: exact four motor axes, washer seats and mount thickness; curved access tunnel omitted.')]
report=[]
for name,get_poly,angle,note in jobs:
    print('Preparing '+name,flush=True)
    d=finish(get_poly(),angle,small/name);d['note']=note;report.append(d);print(json.dumps(d),flush=True)
(r/'fit-piece-manifest.json').write_text(json.dumps(report,indent=2))
with zipfile.ZipFile(r/'pla-all-print-meshes.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in (full,small):
        for file in sorted(folder.glob('*.stl')):z.write(file,str(file.relative_to(r)))
