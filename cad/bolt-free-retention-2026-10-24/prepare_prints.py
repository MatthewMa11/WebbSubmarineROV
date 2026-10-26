from pathlib import Path
import sys,json,shutil
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from check_print_revision import mesh,vtk
out=r/'print';out.mkdir(exist_ok=True)
report=[]
for name,angle in [('Propeller-R7-bolt-free.stl',-90),('Compression-collar-R7.stl',90),('Jam-ring-R7.stl',90),('TEST-FIRST-external-sleeve-R7.stl',0)]:
 p=mesh(r/name);tr=vtk.vtkTransform();tr.RotateX(angle)
 a=vtk.vtkTransformPolyDataFilter();a.SetInputData(p);a.SetTransform(tr);a.Update();bounds=a.GetOutput().GetBounds()
 tr2=vtk.vtkTransform();tr2.Translate(-(bounds[0]+bounds[1])/2,-(bounds[2]+bounds[3])/2,-bounds[4])
 b=vtk.vtkTransformPolyDataFilter();b.SetInputConnection(a.GetOutputPort());b.SetTransform(tr2);b.Update()
 w=vtk.vtkSTLWriter();w.SetFileName(str(out/name));w.SetFileTypeToBinary();w.SetInputConnection(b.GetOutputPort());assert w.Write()
 final=mesh(out/name);edges=vtk.vtkFeatureEdges();edges.SetInputData(final);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
 c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(final);c.SetExtractionModeToAllRegions();c.Update()
 a_mass=vtk.vtkMassProperties();a_mass.SetInputData(p);a_mass.Update();b_mass=vtk.vtkMassProperties();b_mass.SetInputData(final);b_mass.Update()
 result=dict(file=name,triangles=final.GetNumberOfCells(),bad_edges=edges.GetOutput().GetNumberOfCells(),components=c.GetNumberOfExtractedRegions(),volume_before_mm3=a_mass.GetVolume(),volume_after_mm3=b_mass.GetVolume(),bounds_mm=list(final.GetBounds()),rotation_x_deg=angle)
 result['passed']=result['bad_edges']==0 and result['components']==1 and abs(result['volume_before_mm3']-result['volume_after_mm3'])<.01 and abs(result['bounds_mm'][4])<1e-4
 report.append(result);print(('PASS ' if result['passed'] else 'FAIL ')+name,flush=True)
old=out/'existing-parts-unchanged';old.mkdir(exist_ok=True)
for name in ('Nozzle-R6p1-flat-motor-boss.stl','Front-cap-R4-unchanged.stl'):shutil.copy2(r/name,old/name)
shutil.copy2(r/'READ-ME.txt',out/'READ-ME.txt')
(r/'print-mesh-checks.json').write_text(json.dumps(report,indent=2))
raise SystemExit(0 if all(q['passed'] for q in report) else 1)
