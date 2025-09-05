import os
import sys
import numpy as np

import vtk
from vtk.util import numpy_support

import pydicom
from pydicom.dataset import Dataset


# 使用pydicom读取dcm 并且s和b切换是否显示肌肉组织

class DICOM3DViewer:
    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        self.volume = None
        self.volume_property = vtk.vtkVolumeProperty()
        
    def load_dicom_series(self, directory_path):
        """加载DICOM系列文件"""
        print("正在读取DICOM文件...")
        
        dicom_files = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # 尝试读取文件，检查是否是DICOM文件
                    ds = pydicom.dcmread(file_path, force=True)
                    if hasattr(ds, 'pixel_array'):
                        dicom_files.append(ds)
                        print(f"成功加载: {file}")
                except:
                    continue
        
        if not dicom_files:
            print("未找到有效的DICOM文件!")
            return None
        
        # 按切片位置排序
        try:
            dicom_series = sorted(dicom_files, key=lambda x: float(x.ImagePositionPatient[2]))
        except:
            print("无法按位置排序，使用文件名排序")
            dicom_series = dicom_files
        
        print(f"成功加载 {len(dicom_series)} 个DICOM切片")
        return dicom_series
    
    def create_volume_data(self, dicom_series):
        """创建体积数据"""
        # 获取图像尺寸
        rows = dicom_series[0].Rows
        cols = dicom_series[0].Columns
        slices = len(dicom_series)
        
        print(f"图像尺寸: {rows} x {cols} x {slices}")
        
        # 创建numpy数组存储所有切片数据
        volume_array = np.zeros((rows, cols, slices), dtype=np.int16)
        
        # 提取像素数据并转换为Hounsfield单位
        for i, ds in enumerate(dicom_series):
            pixel_data = ds.pixel_array.astype(np.int16)
            
            # 应用rescale参数（如果存在）
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                rescale_slope = ds.RescaleSlope
                rescale_intercept = ds.RescaleIntercept
                pixel_data = pixel_data * rescale_slope + rescale_intercept
                print(f"切片 {i}: Rescale Slope={rescale_slope}, Intercept={rescale_intercept}")
            
            volume_array[:, :, i] = pixel_data
        
        # 打印数据范围用于调试
        print(f"数据范围: {volume_array.min()} 到 {volume_array.max()}")
        
        return volume_array
    
    def create_vtk_image_data(self, volume_array, dicom_series):
        """创建VTK图像数据"""
        # 获取间距信息
        if hasattr(dicom_series[0], 'PixelSpacing'):
            pixel_spacing = dicom_series[0].PixelSpacing
            dx, dy = float(pixel_spacing[0]), float(pixel_spacing[1])
        else:
            dx, dy = 1.0, 1.0
            print("警告: 未找到像素间距信息，使用默认值1.0")
        
        # 计算切片间距
        if len(dicom_series) > 1 and hasattr(dicom_series[0], 'ImagePositionPatient'):
            try:
                z1 = float(dicom_series[0].ImagePositionPatient[2])
                z2 = float(dicom_series[1].ImagePositionPatient[2])
                dz = abs(z2 - z1)
            except:
                dz = 1.0
                print("警告: 无法计算切片间距，使用默认值1.0")
        else:
            dz = 1.0
        
        print(f"像素间距: X={dx}, Y={dy}, Z={dz}")
        
        # 将numpy数组转换为VTK格式
        vtk_data = numpy_support.numpy_to_vtk(
            volume_array.ravel(order='F'),  # 使用Fortran顺序
            array_type=vtk.VTK_SHORT
        )
        
        # 创建VTK图像数据
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(volume_array.shape[1], volume_array.shape[0], volume_array.shape[2])
        vtk_image.SetSpacing(dx, dy, dz)
        vtk_image.GetPointData().SetScalars(vtk_data)
        
        return vtk_image

    # ====== 骨骼模式传输函数 ======
    def set_bone_mode(self):
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
        color_func.AddRGBPoint(0, 0.0, 0.0, 0.0)
        color_func.AddRGBPoint(300, 1.0, 1.0, 0.9)
        color_func.AddRGBPoint(1500, 1.0, 1.0, 1.0)

        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-1000, 0.0)
        opacity_func.AddPoint(0, 0.0)
        opacity_func.AddPoint(200, 0.0)
        opacity_func.AddPoint(300, 0.9)
        opacity_func.AddPoint(1500, 1.0)

        self.volume_property.SetColor(color_func)
        self.volume_property.SetScalarOpacity(opacity_func)
        self.volume_property.ShadeOn()
        self.volume_property.SetInterpolationTypeToLinear()
        self.volume_property.SetAmbient(0.4)
        self.volume_property.SetDiffuse(0.6)
        self.volume_property.SetSpecular(0.2)

        print("✅ 切换到骨骼模式")

    # ====== 软组织模式传输函数 ======
    def set_soft_tissue_mode(self):
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
        color_func.AddRGBPoint(-500, 0.3, 0.3, 0.3)
        color_func.AddRGBPoint(0, 0.7, 0.7, 0.7)
        color_func.AddRGBPoint(300, 1.0, 1.0, 1.0)

        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-1000, 0.0)
        opacity_func.AddPoint(-500, 0.0)
        opacity_func.AddPoint(0, 0.2)
        opacity_func.AddPoint(300, 0.7)
        opacity_func.AddPoint(1000, 0.9)

        self.volume_property.SetColor(color_func)
        self.volume_property.SetScalarOpacity(opacity_func)
        self.volume_property.ShadeOn()
        self.volume_property.SetInterpolationTypeToLinear()
        self.volume_property.SetAmbient(0.4)
        self.volume_property.SetDiffuse(0.6)
        self.volume_property.SetSpecular(0.2)

        print("✅ 切换到软组织模式")

    def setup_volume_rendering(self, vtk_image):
        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetInputData(vtk_image)

        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(volume_mapper)

        # 默认骨骼模式
        self.set_bone_mode()
        self.volume.SetProperty(self.volume_property)

        return self.volume

    def visualize(self, directory_path, mode='volume'):
        dicom_series = self.load_dicom_series(directory_path)
        if not dicom_series:
            print("请检查DICOM文件路径是否正确")
            return

        volume_array = self.create_volume_data(dicom_series)
        vtk_image = self.create_vtk_image_data(volume_array, dicom_series)

        if mode == 'volume':
            volume = self.setup_volume_rendering(vtk_image)
            self.renderer.AddVolume(volume)
            print("使用体绘制模式")

        # 键盘回调
        def keypress_callback(obj, event):
            key = obj.GetKeySym()
            if key == "s":   # soft tissue
                self.set_soft_tissue_mode()
                self.volume.SetProperty(self.volume_property)
                self.render_window.Render()
            elif key == "b":  # bone
                self.set_bone_mode()
                self.volume.SetProperty(self.volume_property)
                self.render_window.Render()

        self.interactor.AddObserver("KeyPressEvent", keypress_callback)

        self.renderer.SetBackground(0.1, 0.2, 0.3)
        self.renderer.ResetCamera()
        self.render_window.SetSize(800, 600)
        self.render_window.SetWindowName("DICOM 3D Viewer")

        self.render_window.Render()
        self.interactor.Start()


def main():
    print("按s使用肌肉模式，按b使用骨头模式")
    directory_path = os.path.expanduser("~") + "\spine\dataStore\dicom_data"
    mode = 'volume'
    
    if len(sys.argv) > 2:
        mode = sys.argv[2]
    
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录!")
        return
    
    viewer = DICOM3DViewer()
    viewer.visualize(directory_path, mode)


if __name__ == "__main__":
    main()