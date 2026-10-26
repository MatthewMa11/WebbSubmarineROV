"""Dense bidirectional STL surface comparison, independent of invalid old STEP mass integrals."""
from pathlib import Path
import sys,json,hashlib,argparse
sys.path.insert(0,'C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/.vendor')
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'print-revision-2026-10-17'))
import vtk,numpy as np
from vtk.util.numpy_support import vtk_to_numpy,numpy_to_vtk
from check_print_revision import mesh
def profile_check(folder,shift=8.0):
 folder=Path(folder);candidate=folder/'Fan-R9-forward-fan.stl';reference=folder.parent/'shaft-clamp-r8-2026-10-25/Fan-R8-M3-axle-clamp.stl'
 old=mesh(reference);new=mesh(candidate)
 tr=vtk.vtkTransform();tr.Translate(0,-shift,0)
 f=vtk.vtkTransformPolyDataFilter();f.SetInputData(new);f.SetTransform(tr);f.Update()
 translated=vtk.vtkPolyData();translated.DeepCopy(f.GetOutput())
 def samples(poly):
  pts=vtk_to_numpy(poly.GetPoints().GetData()).astype(float)
  cells=vtk_to_numpy(poly.GetPolys().GetConnectivityArray()).reshape(-1,3)
  tri=pts[cells]
  allpts=np.vstack([pts,tri.mean(axis=1),(tri[:,0]+tri[:,1])/2,(tri[:,1]+tri[:,2])/2,(tri[:,2]+tri[:,0])/2])
  return allpts[np.linalg.norm(allpts[:,[0,2]],axis=1)>27.05]
 directions=[]
 for label,source,target in [('old-to-new',old,translated),('new-to-old',translated,old)]:
  locator=vtk.vtkImplicitPolyDataDistance();locator.SetInput(target)
  pts=samples(source);dist=np.fromiter((abs(locator.EvaluateFunction(tuple(p))) for p in pts),float,count=len(pts))
  directions.append(dict(direction=label,samples=len(pts),max_distance_mm=float(dist.max()),percentile99_mm=float(np.percentile(dist,99)),mean_distance_mm=float(dist.mean())))
 result=dict(check='outer blade sampled surfaces agree within 0.02 mm after specified translation',passed=all(d['max_distance_mm']<.02 for d in directions),shift_mm=shift,tolerance_mm=.02,minimum_sample_radius_mm=27.05,directions=directions,candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest())
 (folder/('profile-verification.json' if shift==8.0 else 'profile-negative-control.json')).write_text(json.dumps(result,indent=2))
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--shift',type=float,default=8.0);args=a.parse_args()
 result=profile_check(Path(__file__).resolve().parent,args.shift);print(json.dumps(result,indent=2),flush=True)
 raise SystemExit(0 if result['passed'] else 1)
