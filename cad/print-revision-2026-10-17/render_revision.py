from pathlib import Path
import sys
sys.path.insert(0,'C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/.vendor')
import vtk
r=Path(__file__).resolve().parent
w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1260,540);w.SetMultiSamples(4)
names=[('Nozzle-360-wire-ring-R2.stl','360 DEGREE WIRE RING',(.8,-2.4,1.1)),
       ('Propeller-71mm-sweep-R2.stl','71 mm BLADE SWEEP',(.8,2.8,1.1)),
       ('Motor-insert-22p6mm-R2.stl','22.6 mm SPACER',(.8,2.5,.9))]
for i,(file,label,direction) in enumerate(names):
    rd=vtk.vtkSTLReader();rd.SetFileName(str(r/'printable-STLs'/file));rd.Update()
    ren=vtk.vtkRenderer();ren.SetViewport(i/3,0,(i+1)/3,1);ren.SetBackground(.965,.975,.985)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(rd.GetOutputPort())
    act=vtk.vtkActor();act.SetMapper(mapper);act.GetProperty().SetColor(.24,.46,.62);act.GetProperty().SetSpecular(.2);act.GetProperty().SetSpecularPower(25);ren.AddActor(act)
    bounds=rd.GetOutput().GetBounds();center=[(bounds[2*j]+bounds[2*j+1])/2 for j in range(3)];size=max(bounds[2*j+1]-bounds[2*j] for j in range(3))
    cam=ren.GetActiveCamera();cam.SetFocalPoint(*center);cam.SetPosition(*(center[j]+size*direction[j] for j in range(3)));cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();ren.ResetCamera();cam.Zoom(.82);cam.SetWindowCenter(0,-.08)
    txt=vtk.vtkTextActor();txt.SetInput(label);txt.SetPosition(18,28);txt.GetTextProperty().SetFontSize(22);txt.GetTextProperty().SetColor(.1,.18,.24);txt.GetTextProperty().BoldOn();ren.AddViewProp(txt);w.AddRenderer(ren)
w.Render();img=vtk.vtkWindowToImageFilter();img.SetInput(w);img.SetInputBufferTypeToRGB();img.ReadFrontBufferOff();img.Update();out=vtk.vtkPNGWriter();out.SetFileName(str(r/'R2-printable-parts.png'));out.SetInputConnection(img.GetOutputPort());out.Write();w.Finalize()
