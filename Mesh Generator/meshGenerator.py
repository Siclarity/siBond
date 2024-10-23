# %%
import pyvista as pv
import numpy as np

# %%
#purpose of this class is to assign attributes to meshing objects
class Material:
    def __init__(self,material,shape,mesh):
        self.material=material
        self.shape=shape
        self.mesh=mesh
    def information(self):
        return "Material:",{self.material}, "Shape:",{self.shape}, "Mesh:",{self.mesh}

# %%
SiO2_l=10
SiO2_w=10
SiO2_h=15
SiO2_dimension=(SiO2_l,SiO2_w,SiO2_h)
SiO2=Material("SiO2",SiO2_dimension,"Normal")

# %%
Cu_r=1.99
Cu_h=9.99
Cu_dish=5e-3
Cu_dimension=(Cu_r,Cu_h)
Copper=Material("Cu",Cu_dimension,"Finer")

# %%
TiN_r=Cu_r+0.01
TiN_h=Cu_h+0.01
TiN_dimension=(TiN_r,TiN_h)
TiN=Material("TiN",TiN_dimension,"Finer")

# %%
#purpose of this class is to generate the SiO2 block with TiN hole
class gen_SiO2_block:
    def __init__(self,shape):
        self.length,self.width,self.height=shape
    def mesh_gen(self):
        SiO2_cube=pv.Cube(center=(0,0,0),bounds=(-(self.length/2),(self.length/2),-(self.width/2), (self.width/2), -(self.height/2), (self.height/2)))
        TiN_hole=pv.Cylinder(center=(0,0,0),radius=TiN_r,height=TiN_h)
        TiN_hole=TiN_hole.rotate_y(90)
        dist=abs(((TiN_h)/2)-(self.height/2))
        distance=round(dist,1)
        distance+=0.005
        TiN_hole=TiN_hole.translate((0,0,distance))
        SiO2_cube=SiO2_cube.triangulate()
        TiN_hole=TiN_hole.triangulate()
        SiO2_cube=SiO2_cube.boolean_difference(TiN_hole)
        plotter=pv.Plotter()
        plotter.add_mesh(SiO2_cube,color="cyan",opacity=0.75)
        plotter.show()
        return SiO2_cube

# %%
SiO2_block=gen_SiO2_block(SiO2_dimension)
SiO2_block=SiO2_block.mesh_gen()

# %%
#purpose of this class is to generate the TiN thin layer
class gen_TiN_layer:
    def __init__(self,shape):
        self.radius,self.height=shape
    def mesh_gen(self):
        TiN=pv.Cylinder(center=(0,0,0),radius=self.radius,height=self.height)
        Copper_rem=pv.Cylinder(center=(0,0,0), radius=Cu_r, height=Cu_h)
        Copper_rem=Copper_rem.translate((0.01,0,0))
        TiN=TiN.triangulate()
        Copper_rem=Copper_rem.triangulate()
        TiN=TiN.boolean_difference(Copper_rem)
        #rotate the TiN Layer to be upwards
        TiN=TiN.rotate_y(270)
        #testing to see if it makes an error when importing to COMSOL
        TiN=TiN.clean()
        TiN=TiN.decimate(0.125)
        TiN=TiN.clean()
        ###
        plotter2=pv.Plotter()
        plotter2.add_mesh(TiN,color="gray",style='wireframe', line_width=10,opacity=0.9)
        plotter2.show()
        return TiN

# %%
TiN_thin=gen_TiN_layer(TiN_dimension)
TiN=TiN_thin.mesh_gen()
TiN.save("TiN_class-parameterized.stl")

# %%
#purpose of this class is to generate the Copper with divit
class gen_Copper_divit:
    def __init__(self,shape):
        self.radius,self.height=shape
    def mesh_gen(self):
        # Define the ellipsoid parameters
        center = np.array([0,0,(Cu_h/2)])  # Center of the ellipsoid (x, y, z)
        radii = np.array([1,1,Cu_dish])  # Radii along x, y, and z axes
        # Create a mesh of the unit sphere (scaled to make it an ellipsoid)
        sphere = pv.Sphere(radius=Cu_r, theta_resolution=50, phi_resolution=50)
        # Apply scaling to transform the sphere into an ellipsoid
        transform = np.diag(radii.tolist() + [1])  # Scaling matrix
        ellipsoid = sphere.transform(transform, inplace=False)
        
        # Translate the ellipsoid to the desired coordinates
        ellipsoid.translate(center, inplace=True)
        
        # Ellipsoid with a long x axis
        # ellipsoid = pv.ParametricEllipsoid(10, 5, 5)
        Copper=pv.Cylinder(radius=Cu_r, height=Cu_h, center=(0,0,0))
        Copper=Copper.rotate_y(90)
        Copper=Copper.triangulate()
        Copper_dished = Copper.boolean_difference(ellipsoid)
        plotter3=pv.Plotter()
        #plotter3.add_mesh(ellipsoid,color="green",opacity=0.75)
        plotter3.add_mesh(Copper_dished,color="orange",opacity=0.9)
        plotter3.show()
        return Copper_dished

# %%
Copper_div=gen_Copper_divit(Cu_dimension)
Copper_div=Copper_div.mesh_gen()
