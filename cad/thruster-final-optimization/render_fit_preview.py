from pathlib import Path
import sys
sys.path.insert(0,'C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/.vendor')
import vtk
r=Path(__file__).resolve().parent
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1080,740);window.SetMultiSamples(4)
names=[('A-motor-guide-drive-keys.stl','A  MOTOR HUB / DRIVE KEYS'),
       ('B-motor-insert.stl','B  MOTOR INSERT'),
       ('C-M4-mount-pad.stl','C  M4 CORNER BOLT PAD'),
       ('D-shaft-bore-3p5mm.stl','D  3.5 mm SHAFT BORE'),
       ('E-cover-captive-nut-seat.stl','E  CAPTIVE COVER NUT SEAT'),
       ('F-motor-base-washer-seats.stl','F  MOTOR BASE SEATS')]
for i,(file,label) in enumerate(names):
    renderer=vtk.vtkRenderer();col=i%3;row=1-i//3
    renderer.SetViewport(col/3,row/2,(col+1)/3,(row+1)/2);renderer.SetBackground(.965,.975,.985)
    reader=vtk.vtkSTLReader();reader.SetFileName(str(r/'fit-check-first'/file));reader.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(reader.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(.27,.47,.63)
    actor.GetProperty().SetAmbient(.22);actor.GetProperty().SetDiffuse(.75);actor.GetProperty().SetSpecular(.2);actor.GetProperty().SetSpecularPower(25)
    renderer.AddActor(actor)
    b=reader.GetOutput().GetBounds();c=[(b[2*j]+b[2*j+1])/2 for j in range(3)];size=max(b[2*j+1]-b[2*j] for j in range(3))
    cam=renderer.GetActiveCamera();cam.SetFocalPoint(*c);cam.SetPosition(c[0]+size*1.6,c[1]-size*2.2,c[2]+size*( -1.8 if i==4 else 1.8));cam.SetViewUp(0,0,1)
    renderer.ResetCamera();cam.Zoom(.82);cam.SetWindowCenter(0,-.05)
    text=vtk.vtkTextActor();text.SetInput(label);text.SetPosition(14,15);text.GetTextProperty().SetFontSize(17);text.GetTextProperty().SetColor(.1,.18,.24);text.GetTextProperty().BoldOn();renderer.AddViewProp(text)
    window.AddRenderer(renderer)
window.Render();grab=vtk.vtkWindowToImageFilter();grab.SetInput(window);grab.SetInputBufferTypeToRGB();grab.ReadFrontBufferOff();grab.Update()
writer=vtk.vtkPNGWriter();writer.SetFileName(str(r/'fit-check-preview.png'));writer.SetInputConnection(grab.GetOutputPort());writer.Write();window.Finalize()
print('Rendered six full-scale fit-check pieces')
