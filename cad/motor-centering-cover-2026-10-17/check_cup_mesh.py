"""Actual exported nozzle checks for the permanent stationary centering cup."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'print-revision-2026-10-17'))
from check_print_revision import mesh,occupied
import vtk

def main():
    p=mesh(Path(sys.argv[1]));checks=[]
    def check(name,ok,**detail):
        checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    guides=[];pilot=[];free=[];cables=[]
    for i in range(4):
        a=math.pi*i/2
        for y in (-10.5,-9,-7):guides.append((17.8*math.cos(a),y,17.8*math.sin(a)))
        pilot.append((14.5*math.cos(a),-10.5,14.5*math.sin(a)))
        free.append((14.1*math.cos(a),-10.5,14.1*math.sin(a)))
        b=a+math.pi/4;d=(math.cos(b),math.sin(b));u=(-d[1],d[0])
        # All four ports must pass a 9 x 2.6 mm wire-bundle envelope.
        for radius in (14.5,16,18,20):
            for tangent in (-4.5,0,4.5):
                for y in (-9.3,-8,-6.7):
                    cables.append((d[0]*radius+u[0]*tangent,y,d[1]*radius+u[1]*tangent))
    g=occupied(p,guides);q=occupied(p,pilot);f=occupied(p,free);wire=occupied(p,cables)
    check('four tapered guide sectors surround the motor base',all(g),solid_probes=sum(g),count=len(g))
    check('motor locator throat is present with a clear bore',all(q) and not any(f),locator_probes=q,bore_probes=f)
    check('all four cable windows pass the stated bundle envelope',not any(wire),obstruction_count=sum(wire),probe_count=len(wire),bundle_envelope_mm=[9,2.6])
    edges=vtk.vtkFeatureEdges();edges.SetInputData(p);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
    con=vtk.vtkPolyDataConnectivityFilter();con.SetInputData(p);con.SetExtractionModeToAllRegions();con.Update()
    check('nozzle and centering cup are one closed printable body',edges.GetOutput().GetNumberOfCells()==0 and con.GetNumberOfExtractedRegions()==1,
          bad_edges=edges.GetOutput().GetNumberOfCells(),components=con.GetNumberOfExtractedRegions(),triangles=p.GetNumberOfCells())
    Path(sys.argv[2]).write_text(json.dumps(checks,indent=2),encoding='utf-8')
    return 0 if all(c['passed'] for c in checks) else 1
if __name__=='__main__':raise SystemExit(main())
