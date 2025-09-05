import os
import sys
import numpy as np

import vtk
from vtk.util import numpy_support

import pydicom
from pydicom.dataset import Dataset

# 使用pydicom读取dcm

class DICOM3DViewer:
    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        
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
    
    def setup_volume_rendering(self, vtk_image):
        """设置体绘制，只显示骨骼"""
        scalar_range = vtk_image.GetScalarRange()
        print(f"VTK图像标量范围: {scalar_range}")
        min_val, max_val = scalar_range

        # === 颜色映射（只保留骨骼 HU > 300 部分）===
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(-1000, 0.0, 0.0, 0.0)   # 空气黑色透明
        color_func.AddRGBPoint(0, 0.0, 0.0, 0.0)       # 软组织透明
        color_func.AddRGBPoint(300, 1.0, 1.0, 0.9)     # 骨骼白色
        color_func.AddRGBPoint(1500, 1.0, 1.0, 1.0)    # 高密度骨骼更亮

        # === 不透明度映射（骨骼高透明度，其他接近 0）===
        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(-1000, 0.0)   # 空气透明
        opacity_func.AddPoint(0, 0.0)       # 软组织完全透明
        opacity_func.AddPoint(200, 0.0)     # 仍然透明
        opacity_func.AddPoint(300, 0.9)     # 骨骼快速变得不透明
        opacity_func.AddPoint(1500, 1.0)    # 高密度骨骼完全不透明

        # === 体绘制属性 ===
        volume_property = vtk.vtkVolumeProperty()
        volume_property.SetColor(color_func)
        volume_property.SetScalarOpacity(opacity_func)
        volume_property.ShadeOn()
        volume_property.SetInterpolationTypeToLinear()
        volume_property.SetAmbient(0.4)
        volume_property.SetDiffuse(0.6)
        volume_property.SetSpecular(0.2)

        # Mapper
        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetInputData(vtk_image)

        # Volume Actor
        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)

        return volume


    
    def setup_slice_view(self, vtk_image):
        """设置切片视图作为备选方案"""
        # 创建切片映射器
        slice_mapper = vtk.vtkImageResliceMapper()
        slice_mapper.SetInputData(vtk_image)
        slice_mapper.SliceFacesOn()
        slice_mapper.SliceAtFocalPointOn()
        
        # 创建切片演员
        slice_actor = vtk.vtkImageSlice()
        slice_actor.SetMapper(slice_mapper)
        
        # 设置窗口/级别
        property = slice_actor.GetProperty()
        scalar_range = vtk_image.GetScalarRange()
        window = scalar_range[1] - scalar_range[0]
        level = (scalar_range[1] + scalar_range[0]) / 2
        property.SetColorWindow(window)
        property.SetColorLevel(level)
        
        return slice_actor
    
    def visualize(self, directory_path, mode='volume'):
        """主可视化函数"""
        dicom_series = self.load_dicom_series(directory_path)
        if not dicom_series:
            print("请检查DICOM文件路径是否正确")
            return
        
        # 创建体积数据
        volume_array = self.create_volume_data(dicom_series)
        
        # 创建VTK图像数据
        vtk_image = self.create_vtk_image_data(volume_array, dicom_series)
        
        if mode == 'volume':
            # 尝试体绘制
            try:
                volume = self.setup_volume_rendering(vtk_image)
                self.renderer.AddVolume(volume)
                print("使用体绘制模式")
            except Exception as e:
                print(f"体绘制失败: {e}")
                print("切换到切片模式")
                slice_actor = self.setup_slice_view(vtk_image)
                self.renderer.AddActor(slice_actor)
        elif mode == 'slice':
            # 切片模式
            slice_actor = self.setup_slice_view(vtk_image)
            self.renderer.AddActor(slice_actor)
            print("使用切片模式")
        
        # 设置渲染器
        self.renderer.SetBackground(0.1, 0.2, 0.3)
        self.renderer.ResetCamera()
        
        # 设置渲染窗口
        self.render_window.SetSize(800, 600)
        self.render_window.SetWindowName("DICOM 3D Viewer")
        
        # 开始交互
        self.render_window.Render()
        
        # 添加一些调试信息
        print("渲染窗口已创建，请检查是否显示图像")
        print("如果仍然看不到图像，请尝试:")
        print("1. 检查DICOM文件是否包含有效的图像数据")
        print("2. 尝试使用 'slice' 模式: python script.py your_dicom_folder slice")
        print("3. 调整传输函数参数")
        
        self.interactor.Start()

def main():
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
