import pyvista as pv
import numpy as np

plotter=pv.Plotter()
a=True #toggle to get offset match with an effective area or an offset match with a shared edge
s1_bounds=(-1400000,-1544000,-1396000,-1540000)
s2_bounds=(-1401000,-1545000,-1395000,-1539000)
s1_share_edge=(-1480000,-1512000,-1476000,-1508000)
s2_share_edge=(-1476000,-1516000,-1472000,-1512000)
if a:
    s1_x_min,s1_y_min,s1_x_max,s1_y_max=s1_bounds
    s2_x_min,s2_y_min,s2_x_max,s2_y_max=s2_bounds
else:
    s1_x_min,s1_y_min,s1_x_max,s1_y_max=s1_share_edge
    s2_x_min,s2_y_min,s2_x_max,s2_y_max=s2_share_edge


depth1=2000
depth2=2000
cube_top=pv.Cube(center=(0,0,1),bounds=(s1_x_min,s1_x_max,s1_y_min,s1_y_max,1,(depth1+1)))
cube_bot=pv.Cube(center=(0,0,0),bounds=(s2_x_min,s2_x_max,s2_y_min,s2_y_max,(-depth2),0))
plotter.clear()
plotter.add_mesh(cube_top,color='red',show_edges=True,opacity=0.75)
plotter.add_mesh(cube_bot, color='blue', show_edges=True,opacity=0.75)

# Show the 3D plot with all the Tetris pieces
plotter.show()

