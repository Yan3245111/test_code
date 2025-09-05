import os
import sys
import pydicom
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication, QPushButton

import vtk
from vtk.util import numpy_support
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class LoadDCM(QMainWindow):
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.resize(1000, 1000)
        
        # WIDGET
        self._widget = QWidget()
        self.setCentralWidget(self._widget)
        layout = QVBoxLayout()
        self._widget.setLayout(layout)
        
        # QVTK交互
        self._vtk_widget = QVTKRenderWindowInteractor(self._widget)
        layout.addWidget(self._vtk_widget)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)
        self._btn_bone = QPushButton("BONE MODE")
        self._btn_soft = QPushButton("SOFT MODE")
        btn_layout.addWidget(self._btn_bone)
        btn_layout.addWidget(self._btn_soft)
        self._btn_bone.clicked.connect(self._set_bone_mode)
        self._btn_soft.clicked.connect(self._set_soft_mode)
        
        # VTK
        self._render = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._render)
        self._interactor = self._vtk_widget.GetRenderWindow().GetInteractor()
        self._interactor.SetInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera())
        
        self._volume = None
        self._volume_property = vtk.vtkVolumeProperty()
        
    def _set_bone_mode(self):
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-1000, 0, 0, 0)
        color_func.AddRGBPoint(300, 1, 1, 0.9)
        color_func.AddRGBPoint(1500, 1, 1, 1)
        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(200, 0.0)
        opacity_func.AddPoint(300, 0.9)
        opacity_func.AddPoint(1500, 1.0)
        self._volume_property.SetColor(color_func)
        self._volume_property.SetScalarOpacity(opacity_func)
        self._volume_property.ShadeOn()
        if self._volume:
            self._volume.SetProperty(self._volume_property)
            self._vtk_widget.GetRenderWindow().Render()
    
    def _set_soft_mode(self):
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-1000, 0, 0, 0)
        color_func.AddRGBPoint(-200, 0.2, 0.2, 0.2)
        color_func.AddRGBPoint(0, 0.6, 0.6, 0.6)
        color_func.AddRGBPoint(100, 0.9, 0.7, 0.6)
        color_func.AddRGBPoint(300, 1, 1, 1)
        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-1000, 0.0)
        opacity_func.AddPoint(-200, 0.0)
        opacity_func.AddPoint(0, 0.2)
        opacity_func.AddPoint(100, 0.6)
        opacity_func.AddPoint(300, 0.9)
        opacity_func.AddPoint(1000, 1.0)
        self._volume_property.SetColor(color_func)
        self._volume_property.SetScalarOpacity(opacity_func)
        self._volume_property.ShadeOn()
        if self._volume:
            self._volume.SetProperty(self._volume_property)
            self._vtk_widget.GetRenderWindow().Render()
        
    def load_dicom(self, path: str):
        dicom_files = list()
        for root, _, files in os.walk(path):
            for file in files:
                path = os.path.join(root, file)
                try:
                    ds = pydicom.dcmread(path, force=True)
                    if hasattr(ds, "pixel_array"):
                        dicom_files.append(ds)
                except:
                    continue
        dicom_volume = sorted(dicom_files, key=lambda x: float(x.ImagePositionPatient[2]))
        return dicom_volume
    
    # 存放行 列 层数
    def create_volume_data(self, dicom_volume):
        rows, cols = dicom_volume[0].Rows, dicom_volume[1].Columns
        slices = len(dicom_volume)
        volume_array = np.zeros((rows, cols, slices), dtype=np.int16)
        for i, ds in enumerate(dicom_volume):
            pixel = ds.pixel_array.astype(np.int16)
            slope = getattr(ds, "RescaleSlope", 1)
            intercrept = getattr(ds, "RescaleIntercept", 0)
            pixel = pixel * slope + intercrept
            volume_array[:, :, i] = pixel
        return volume_array
        
    def create_vtk_image_data(self, volume_array, dicom_volume):
        dx, dy = 1.0, 1.0
        if hasattr(dicom_volume[0], "PixelSpacing"):
            dx, dy = map(float, dicom_volume[0].PixelSpacing)
        dz = 1.0
        if len(dicom_volume) > 1 and hasattr(dicom_volume[0], "ImagePositionPatient"):
            z1 = float(dicom_volume[0].ImagePositionPatient[2])
            z2 = float(dicom_volume[1].ImagePositionPatient[2])
            dz = abs(z2 - z1)
        vtk_data = numpy_support.numpy_to_vtk(volume_array.ravel(order="F"), array_type=vtk.VTK_SHORT)
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(volume_array.shape[1], volume_array.shape[0], volume_array.shape[2])
        vtk_image.SetSpacing(dx, dy, dz)
        vtk_image.GetPointData().SetScalars(vtk_data)
        return vtk_image
    
    def setup_volume_rendering(self, vtk_image):
        mapper = vtk.vtkSmartVolumeMapper()
        mapper.SetInputData(vtk_image)
        self._volume = vtk.vtkVolume()
        self._volume.SetMapper(mapper)
        self._set_bone_mode()
        self._volume.SetProperty(self._volume_property)
        self._render.AddVolume(self._volume)
        self._render.ResetCamera()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_dcm = LoadDCM()
    load_dcm.show()
    
    dicom_path = os.path.expanduser("~") + "\spine\dataStore\dicom_data"
    dicom_volume = load_dcm.load_dicom(path=dicom_path)
    volume_array = load_dcm.create_volume_data(dicom_volume=dicom_volume)
    vtk_image = load_dcm.create_vtk_image_data(volume_array=volume_array, dicom_volume=dicom_volume)
    load_dcm.setup_volume_rendering(vtk_image=vtk_image)

    sys.exit(app.exec_())
