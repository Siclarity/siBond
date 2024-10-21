# %%
import pyvista as pv
import numpy as np

# %%
#Parameters that the user will input
SiO2_width=10
SiO2_depth=10
SiO2_height=15
Cu_height=9.99
Cu_dish_height=100e-3

# %%
#parameters that will be automatically calculated
Cu_radi=1.99
TiN_radi=Cu_radi+0.01
TiN_thin_height=Cu_height+0.01
TiN_height=Cu_height+0.02
#print(TiN_radi)
#print(TiN_height)
#min, max [width,height,depth]
#calculate the bounds for the SiO2 block 
SiO2_block=pv.Cube(center=(0,0,0),bounds=(-(SiO2_width/2),(SiO2_width/2),-(SiO2_depth/2), (SiO2_depth/2), -(SiO2_height/2), (SiO2_height/2)))
plotter = pv.Plotter()
plotter.add_mesh(SiO2_block, color='cyan', opacity=0.5)
plotter.show()

# %%
#Creates the TiN Cylinder and moves it to the the top
TiN_hole=pv.Cylinder(radius=TiN_radi,height=TiN_height,center=(0,0,0))
TiN_hole=TiN_hole.rotate_y(90)
dist=abs(((TiN_height)/2)-(SiO2_height/2))
#print(dist)
distance=round(dist,1)
#print(distance)
distance+=0.005
TiN_hole=TiN_hole.translate((0,0,distance))
SiO2_block=SiO2_block.triangulate()
TiN_hole=TiN_hole.triangulate()
SiO2=SiO2_block.boolean_difference(TiN_hole)
#Saves the SiO2 block as the file name below
SiO2.save("SiO2-parameter.stl")
plotter1 = pv.Plotter()
plotter1.add_mesh(SiO2,color="cyan",opacity=0.5)
plotter1.show()

# %%
# plotter.clear()
# plotter.add_mesh(SiO2,color="blue",opacity=0.5)
# plotter.show()

# %%
# plotter.clear()
plotter2 = pv.Plotter()
#TiN  now is equal to the TiN_hole which will share dimensions and positions
TiN=TiN_hole
#user the plotter2 to visualize how the objects are placed
#TiN=TiN.triangulate()
plotter2.add_mesh(SiO2,color="cyan",opacity=0.5)
plotter2.add_mesh(TiN,color="gray",opacity=0.9)
plotter2.show()

# %%
#plotter.clear()
# Copper_val=pv.Cylinder(radius=Cu_radi, height=Cu_height,center=(0,0,0))
# Copper_val=Copper_val.rotate_y(90)
# dist_Cu=abs((Cu_height/2)-(SiO2_height/2))
# print(dist_Cu)
# Copper_temp=Copper_val
# Copper_val=Copper_val.translate((0,0,dist_Cu+0.015))
# Copper=Copper_val
# Copper_val=Copper_val.triangulate()
# #TiN=TiN.triangulate()
# TiN=TiN.boolean_difference(Copper_val)
# TiN.save("TiN-parameter.stl")
# plotter3 = pv.Plotter()
# #plotter3.add_mesh(SiO2,color="cyan",opacity=0.5)
# plotter3.add_mesh(TiN,color="gray",opacity=1)
# plotter3.add_mesh(Copper,color="orange",opacity=0.75)
# plotter3.show()

#Create a copper cylinder based off the Copper Radius and the user inputted height
Copper_cyl=pv.Cylinder(radius=Cu_radi, height=Cu_height, center=(0,0,0))
#This is the TiN thin layer which is easier to make with the objects ontop of one another 
TiN_thin=pv.Cylinder(radius=TiN_radi, height=TiN_thin_height,center=(0,0,0))
Copper_cyl=Copper_cyl.triangulate()
#shifts over 0.01 so the copper will be flushed with the TiN thin layer allowing for the gap to be created
Copper_cyl=Copper_cyl.translate((0.01,0,0))
TiN_thin=TiN_thin.triangulate()
TiN=TiN_thin.boolean_difference(Copper_cyl)
TiN=TiN.rotate_y(270)
TiN=TiN.translate((0,0,distance))

#this is here to try and help import to COMSOL and allow for meshing
#TiN=TiN.subdivide(6)
# TiN=TiN.smooth()
# TiN=TiN.clean()
#This is used to see for visualization for the TiN thin sleeve
TiN=TiN.triangulate()
TiN.save("TiN-parameter.stl")
plotter3 = pv.Plotter()
#plotter3.add_mesh(TiN_thin,color="gray",opacity=1)
#plotter3.add_mesh(Copper_cyl,color="orange",opacity=0.75)
plotter3.add_mesh(TiN,color="gray",opacity=0.75)
plotter3.show()

# %%
#This is used to create the divit/concavity of the copper piece
sphere_a = pv.Sphere()

# Define the ellipsoid parameters
center = np.array([0,0,(Cu_height/2)])  # Center of the ellipsoid (x, y, z)
radii = np.array([1,1,Cu_dish_height])  # Radii along x, y, and z axes
# Create a mesh of the unit sphere (scaled to make it an ellipsoid)
sphere = pv.Sphere(radius=Cu_radi, theta_resolution=50, phi_resolution=50)

# Apply scaling to transform the sphere into an ellipsoid
transform = np.diag(radii.tolist() + [1])  # Scaling matrix
ellipsoid = sphere.transform(transform, inplace=False)

# Translate the ellipsoid to the desired coordinates
ellipsoid.translate(center, inplace=True)

# Ellipsoid with a long x axis
# ellipsoid = pv.ParametricEllipsoid(10, 5, 5)
Copper=pv.Cylinder(radius=Cu_radi, height=Cu_height, center=(0,0,0))
Copper=Copper.rotate_y(90)
Copper=Copper.triangulate()
#sphere_b = pv.Sphere(center=(-5, 0, 0) )
Copper_dished = Copper.boolean_difference(ellipsoid)
#Copper_dished=Copper_dished.clean()

#this is here to try and help import to COMSOL and allow for meshing
Copper_dished=Copper_dished.subdivide(6)
# Copper_dished=Copper_dished.smooth()
# Copper_dished=Copper_dished.clean()
####
Copper_dished=Copper_dished.triangulate()
Copper_dished.save("Copper-parameter.stl")

#plotter is used for visualization purposes
plotter4 = pv.Plotter()
# pl = pv.Plotter()
# _ = pl.add_mesh(
#     cylinder, color='r', line_width=3
# )
# _ = pl.add_mesh(
#     ellipsoid, color='b', line_width=3
# )
#_=plotter4.add_mesh(Copper,color='orange', opacity=0.5)
#_=plotter4.add_mesh(ellipsoid,color='blue', opacity=0.5)
_ = plotter4.add_mesh(Copper_dished, color='blue', opacity=0.75)
plotter4.show()

