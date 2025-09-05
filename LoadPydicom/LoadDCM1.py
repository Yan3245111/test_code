import os
import vtk

# vtk自带读取dcm函数
dicom_path = os.path.expanduser("~") + "\spine\dataStore\dicom_data"
print(dicom_path)


class LoadPydicom:
    
    def __init__(self):
        dicom_reader = vtk.vtkDICOMImageReader()
        dicom_reader.SetDirectoryName(dicom_path)
        dicom_reader.Update()
        
        # 提取模型
        iso = vtk.vtkMarchingCubes()
        iso.SetInputConnection(dicom_reader.GetOutputPort())
        iso.SetValue(0, 200) # 设置CT阈值范围 低于200的不会显示
        
        # 光滑处理
        smooth = vtk.vtkSmoothPolyDataFilter()
        smooth.SetInputConnection(iso.GetOutputPort())
        smooth.SetNumberOfIterations(20)
        smooth.SetRelaxationFactor(0.1)
        
        # mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(smooth.GetOutputPort())
        mapper.ScalarVisibilityOff()
        
        # actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 1, 0.9)
        
        # renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.1, 0.2)
        
        # render_win
        ren_win = vtk.vtkRenderWindow()
        ren_win.AddRenderer(renderer)
        ren_win.SetSize(1000, 1000)
        
        # iren
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(ren_win)
        iren.SetInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera())
        
        # start
        renderer.ResetCamera()
        ren_win.Render()
        iren.Start()
    
    
if __name__ == "__main__":
    load_dcm = LoadPydicom()
