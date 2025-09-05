import os
import vtk

path = os.path.join(os.path.dirname(__file__), "STL")


class LoadSTL:
    def __init__(self):
        self._car_actor = self.load_stl(stl_path=path + "/BMW_X3.stl")
        floor_actor = self.load_stl(stl_path=path + "/Floor.stl")
        house_actor = self.load_stl(stl_path=path + "/House.stl")
        
        # 渲染
        render = vtk.vtkRenderer()
        render.AddActor(self._car_actor)
        render.AddActor(floor_actor)
        render.AddActor(house_actor)
        
        # 模型对齐
        car_center = self._car_actor.GetCenter()
        floor_center = floor_actor.GetCenter()
        house_center = house_actor.GetCenter()
        car_bounds = self._car_actor.GetBounds()
        floor_bounds = floor_actor.GetBounds()
        house_bounds = house_actor.GetBounds()
        
        # 汽车和地板对齐
        c_x = floor_center[0] - car_center[0]  # 计算平移是对的
        c_y = floor_bounds[3] - car_bounds[2] # Y要用地板的最高-车的最低计算平移
        c_z = floor_center[2] - car_center[2]
        self._car_actor.SetPosition(c_x, c_y, c_z)
        
        # 房子和地板对齐
        h_x = floor_center[0] - house_center[0]
        h_y = floor_bounds[3] - house_bounds[2]
        h_z = floor_center[2] - house_center[2]
        house_actor.SetPosition(h_x, h_y, h_z)
        
        # REN_WIN
        ren_win = vtk.vtkRenderWindow()
        ren_win.AddRenderer(render)
        ren_win.SetSize(2000, 2000)
        # I_REN
        i_ren = vtk.vtkRenderWindowInteractor()
        i_ren.SetInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera())
        i_ren.SetRenderWindow(ren_win)
        # TIMER
        i_ren.Initialize()  # 必须初始化，不然不动, 此方法在使用鼠标交互的时候 汽车就不动了
        ren_win.Render()
        i_ren.AddObserver("TimerEvent", self._render_timer)
        i_ren.CreateRepeatingTimer(30)  # 改成一次性定时器


        i_ren.Start()
        
    def load_stl(self, stl_path: str):
        # READER
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_path)
        reader.Update()
        # MAPPER
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        # ACTOR
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
    
    def car_move(self):
        pass
        
    def _render_timer(self, obj, event):
        self._car_actor.AddPosition(0.01, 0, 0)
        obj.GetRenderWindow().Render()


if __name__ == "__main__":
    load_stl = LoadSTL()
