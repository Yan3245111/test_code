import vtk
import numpy as np


class PointCloud:
    def __init__(self, max_points=10000):
        self.max_points = max_points

        # VTK 数据结构
        self._vtk_points = vtk.vtkPoints()
        self._vtk_cells = vtk.vtkCellArray()
        self._vtk_depth = vtk.vtkDoubleArray()

        # POLYDATA
        self._poly_data = vtk.vtkPolyData()
        self._poly_data.SetPoints(self._vtk_points)
        self._poly_data.SetVerts(self._vtk_cells)
        self._poly_data.GetPointData().SetScalars(self._vtk_depth)

        # MAPPER
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self._poly_data)

        # ACTOR
        self._actor = vtk.vtkActor()
        self._actor.SetMapper(mapper)

        # RENDERER
        self._renderer = vtk.vtkRenderer()
        self._renderer.SetBackground(0, 0, 0)
        self._renderer.AddActor(self._actor)

        # RENDER WINDOW
        self._ren_win = vtk.vtkRenderWindow()
        self._ren_win.AddRenderer(self._renderer)
        self._ren_win.SetSize(1000, 1000)

        # INTERACTOR
        self._interactor = vtk.vtkRenderWindowInteractor()
        self._interactor.SetRenderWindow(self._ren_win)

        # 定时回调
        self._interactor.AddObserver("TimerEvent", self._timer_callback)
        self._interactor.Initialize()
        self._interactor.CreateRepeatingTimer(50)  # 每 50ms 更新一次

    def add_point(self, point):
        if self._vtk_points.GetNumberOfPoints() < self.max_points:
            point_id = self._vtk_points.InsertNextPoint(point)
            self._vtk_depth.InsertNextValue(point[2])
            self._vtk_cells.InsertNextCell(1)
            self._vtk_cells.InsertCellPoint(point_id)
        else:
            # 随机更新已有点
            r = np.random.randint(0, self.max_points)
            self._vtk_points.SetPoint(r, point)

        # 标记数据更新
        self._vtk_cells.Modified()
        self._vtk_depth.Modified()
        self._vtk_points.Modified()

    def _timer_callback(self, obj, event):
        for _ in range(200):  # 一次加 200 个点
            point = 20 * (np.random.rand(3) - 0.5)
            self.add_point(point)
        obj.GetRenderWindow().Render()

    def start(self):
        self._renderer.ResetCamera()
        self._ren_win.Render()
        self._interactor.Start()


if __name__ == "__main__":
    pc = PointCloud(max_points=10000)
    pc.start()
