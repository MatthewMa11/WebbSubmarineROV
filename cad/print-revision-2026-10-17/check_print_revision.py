"""Check the actual exported meshes against the new physical-fit requirements.

The old set must fail the tip, insert and annular cable-route requirements.
Allowances are design assumptions, not measurements of the user's printer.
"""
from pathlib import Path
import json, sys, math
sys.path.insert(0, 'C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/.vendor')
import numpy as np
import vtk

def mesh(path):
    reader=vtk.vtkSTLReader();reader.SetFileName(str(path));reader.MergingOn();reader.Update()
    p=vtk.vtkPolyData();p.DeepCopy(reader.GetOutput());assert p.GetNumberOfCells()>0
    return p

def points(p):
    from vtk.util.numpy_support import vtk_to_numpy
    return vtk_to_numpy(p.GetPoints().GetData()).astype(float)

def occupied(p, coordinates):
    pts=vtk.vtkPoints()
    for xyz in coordinates:pts.InsertNextPoint(*xyz)
    data=vtk.vtkPolyData();data.SetPoints(pts)
    f=vtk.vtkSelectEnclosedPoints();f.SetSurfaceData(p);f.SetInputData(data);f.SetTolerance(1e-7);f.Update()
    return [bool(f.IsInside(i)) for i in range(len(coordinates))]

def main():
    folder=Path(sys.argv[1]);report=Path(sys.argv[2]);checks=[]
    def check(name, passed, **detail):
        checks.append(dict(check=name,passed=bool(passed),detail=detail))
        print(('PASS ' if passed else 'FAIL ')+name,flush=True)
    files={}
    for path in folder.glob('*.stl'):
        name=path.name.lower()
        key=next((k for k in ('nozzle','propeller','insert','cover') if k in name),None)
        if key:assert key not in files;files[key]=path
    p={k:mesh(v) for k,v in files.items()};v={k:points(x) for k,x in p.items()}
    tip=float(np.linalg.norm(v['propeller'][:,[0,2]],axis=1).max())
    insert=float(np.linalg.norm(v['insert'][:,[0,2]],axis=1).max())
    check('blade swept diameter is at most 71 mm',tip<=35.501,swept_diameter_mm=2*tip)
    check('spacer fits inside a 22.6 mm cylindrical envelope',insert<=11.301,envelope_diameter_mm=2*insert)
    # The old duct's conservative inner radius over the blade span is 37.9505.
    # Also allow .5 mm axis eccentricity, .3 mm inward duct print error,
    # .2 mm blade print growth and a 1 degree tilt over 30 mm axial reach.
    nominal=37.9505-tip
    remaining=nominal-(.5+.3+.2+30*math.sin(math.radians(1)))
    check('blade-to-duct allowance remains above 0.75 mm under stated error budget',remaining>=.75,
          nominal_radial_gap_mm=nominal,allowance_remaining_mm=remaining,
          assumptions_mm=dict(axis_offset=.5,duct_error=.3,blade_growth=.2,tilt_reach=30),tilt_degrees=1)
    opening=[];rim=[]
    for i in range(720):
        a=2*math.pi*i/720
        for y in (-27,-26,-25):
            for r in (16,20,24,27.4):opening.append((r*math.cos(a),y,r*math.sin(a)))
        rim.append((30*math.cos(a),-26,30*math.sin(a)))
    obstruction=sum(occupied(p['nozzle'],opening));solid=sum(occupied(p['nozzle'],rim))
    check('annular wire exit is open all around the motor at the rear ring',obstruction==0,
          obstructed_probes=obstruction,probe_count=len(opening),opening_radial_span_mm=[16,27.4])
    check('wire guide has a continuous surrounding rim',solid==len(rim),solid_probes=solid,probe_count=len(rim))
    for k,poly in p.items():
        edges=vtk.vtkFeatureEdges();edges.SetInputData(poly);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
        conn=vtk.vtkPolyDataConnectivityFilter();conn.SetInputData(poly);conn.SetExtractionModeToAllRegions();conn.Update()
        check(k+' is one closed printable mesh',edges.GetOutput().GetNumberOfCells()==0 and conn.GetNumberOfExtractedRegions()==1,
              bad_edges=edges.GetOutput().GetNumberOfCells(),components=conn.GetNumberOfExtractedRegions(),triangles=poly.GetNumberOfCells())
    report.write_text(json.dumps(checks,indent=2))
    return 0 if all(c['passed'] for c in checks) else 1

if __name__=='__main__':raise SystemExit(main())
