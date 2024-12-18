import pyvista as pv
import numpy as np

#These are the variables that are independent variables/grabbed from gds file
SiO2_w_top=25
SiO2_d_top=25
SiO2_h_top=30

Cu_r_top=2
Cu_h_top=10
Cu_dish_top=1000e-3

SiO2_w_bot=20
SiO2_d_bot=20
SiO2_h_bot=40

Cu_r_bot=4
Cu_h_bot=5
Cu_dish_bot=2500e-3

offset_x=0
offset_y=0

recess_shape="ellipse"
square_param_l=2
square_param_w=1
shift_recess_top=0
shift_recess_bot=0
CD=0
temp=300
pv.global_theme.allow_empty_mesh = True
class Material:
    def __init__(self,material,shape,mesh):
        self.material=material
        self.shape=shape
        self.mesh=mesh
    def information(self):
        return "Material:",{self.material}, "Shape:",{self.shape}, "Mesh:",{self.mesh}


#purpose of this class is to generate the SiO2 block with TiN hole
class gen_SiO2_block:
    def __init__(self,shape,position):
        self.width,self.depth,self.height=shape
        self.position=position
    def mesh_gen(self):
        SiO2_cube=pv.Cube(center=(0,0,0),bounds=(-(self.width/2),(self.width/2),-(self.depth/2), (self.depth/2), -(self.height/2), (self.height/2)))
        if (self.position=='top'):#need to make sure that we have the correct TiN for the correct SiO2 block
            TiN_hole=pv.Cylinder(center=(0,0,0),radius=TiN_r_top,height=TiN_h_top)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=(TiN_h_top)/2-(self.height/2)
            dist-=0.1
            distance=round(dist,1)
            TiN_hole=TiN_hole.translate((offset_x,offset_y,distance))
        elif(self.position=='bot'):
            TiN_hole=pv.Cylinder(center=(-offset_x,-offset_y,0),radius=TiN_r_bot,height=TiN_h_bot)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=abs((TiN_h_bot)/2-(self.height/2))
            dist+=0.1
            distance=round(dist,1)
            TiN_hole=TiN_hole.translate((-offset_x,-offset_y,distance))
        SiO2_cube=SiO2_cube.triangulate()
        TiN_hole=TiN_hole.triangulate()
        SiO2_cube_fin=SiO2_cube.boolean_difference(TiN_hole)
        # plotter=pv.Plotter()
        # plotter.add_mesh(SiO2_cube_fin,color="cyan",opacity=0.75)
        # #plotter.add_mesh(TiN_hole,color="gray",opacity=0.9)
        # plotter.show()
        return SiO2_cube_fin

#purpose of this class is to generate the TiN thin layer
class gen_TiN_layer:
    def __init__(self,shape,position):
        self.radius,self.height=shape
        self.position=position
    def mesh_gen(self):
        if (self.position=='top'):#need to make sure that we have the correct TiN for the correct SiO2 block
            TiN_hole=pv.Cylinder(center=(0,0,0),radius=self.radius,height=self.height)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=(TiN_h_top)/2-(SiO2_h_top/2)
            dist-=0.1
            Copper_rem=pv.Cylinder(center=(0,0,0), radius=Cu_r_top, height=Cu_h_top)
            Copper_rem=Copper_rem.rotate_y(90)
        elif(self.position=='bot'):
            TiN_hole=pv.Cylinder(center=(0,0,0),radius=self.radius,height=self.height)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=abs((TiN_h_bot)/2-(SiO2_h_bot/2))
            dist+=0.1
            Copper_rem=pv.Cylinder(center=(0,0,0), radius=Cu_r_bot, height=Cu_h_bot)
            Copper_rem=Copper_rem.rotate_y(90)
        
        distance=round(dist,1)
        print("TiN movement:",distance)
        if(self.position=='top'):
            TiN_hole=TiN_hole.translate((offset_x,offset_y,distance+0.1))
            Copper_rem=Copper_rem.translate((offset_x,offset_y,distance))
        else:
            TiN_hole=TiN_hole.translate((-offset_x,-offset_y,distance-0.1))
            Copper_rem=Copper_rem.translate((-offset_x,-offset_y,distance))
        TiN_hole=TiN_hole.triangulate()
        Copper_rem=Copper_rem.triangulate()
        TiN=TiN_hole.boolean_difference(Copper_rem)
        #TiN=TiN.clean()
        # plotter2=pv.Plotter()
        # if(self.position=='top'):
        #     color='lightblue'
        # else:
        #     color='gray'
        # plotter2.add_mesh(TiN,color,style="wireframe",line_width=10,opacity=0.75)
        # plotter2.show()
        return TiN



#purpose of this class is to generate the Copper with divit
class gen_Copper_piece:
    def __init__(self,shape,dim,position,indent):
        if(indent=='ellipse'):
            self.indent_radius=dim
        if(indent=='square'):
            self.indent_length,self.indent_width,self.indent_depth=dim
        elif(indent=='sphere'):
            self.indent_radius=dim
        self.position=position
        self.radius,self.height=shape
        self.indent=indent
    def mesh_gen(self):
        height_offset=0
        if(self.position=='top'):
            height_offset=self.height-shift_recess_top
            dist=(TiN_h_top+shift_recess_top)/2-(SiO2_h_top/2)
            dist-=0.1
        elif(self.position=='bot'):
            height_offset=self.height-shift_recess_bot
            dist=abs((TiN_h_bot+shift_recess_bot)/2-(SiO2_h_bot/2))
            dist+=0.1
        distance=round(dist,1)
        Copper=pv.Cylinder(radius=self.radius, height=height_offset, center=(0,0,0))
        Copper=Copper.rotate_y(90)
        Copper=Copper.triangulate()
        if(self.indent=='ellipse'):#seems to work
            # Define the ellipsoid parameters
            print(f"Z Center:{height_offset/2}")
            print(f"Recess value:{self.indent_radius}")
            center = np.array([0,0,height_offset/2])  # Center of the ellipsoid (x, y, z)
            print(f'Center:{center}')
            #radii = np.array([1,1,Cu_dish_top)
            radii = np.array([1,1,self.indent_radius/self.radius])  # Radii along x, y, and z axes
            print(f'Radii:{radii}')
            # Create a mesh of the unit sphere (scaled to make it an ellipsoid)
            sphere = pv.Sphere(radius=self.radius, theta_resolution=50, phi_resolution=50)
            # Apply scaling to transform the sphere into an ellipsoid
            transform = np.diag(radii.tolist() + [1])  # Scaling matrix
            print(f'Transform:{transform}')
            ellipsoid = sphere.transform(transform, inplace=False)
            print(f"Ellipse before translation:{ellipsoid}")
            # Translate the ellipsoid to the desired coordinates
            ellipsoid.translate(center, inplace=True)
            print(f"Ellipse after translation:{ellipsoid}")
            # Ellipsoid with a long x-axis
            # ellipsoid = pv.ParametricEllipsoid(10, 5, 5)
            if(self.position=='top'):
                #ellipsoid.translate((0,0,-1),inplace=True)
                Copper_dished=Copper.boolean_difference(ellipsoid)
                print(f'Top ellipsoid position:{ellipsoid}')
                Copper_dished=Copper_dished.rotate_y(180)
            else:
                # ellipsoid.translate(center, inplace=True)
                print(f'Bot ellipsoid position:{ellipsoid}')
                Copper_dished=Copper.boolean_difference(ellipsoid)
            plotter3=pv.Plotter()
            #plotter3.add_mesh(ellipsoid,color="green",opacity=0.75)
            plotter3.add_mesh(ellipsoid,color='black',opacity=0.9)
            plotter3.add_mesh(Copper_dished,color="orange",opacity=0.9)
            plotter3.show()
            
        elif(self.indent=='square'):
            Cu_cube=pv.Cube(center=(0,0,0),bounds=(-(self.indent_length),(self.indent_length),-(self.indent_width),(self.indent_width),-(self.indent_depth),(self.indent_depth)))
            Cu_cube=Cu_cube.triangulate()
            Cu_cube=Cu_cube.translate((0,0,height_offset/2))
            Copper_dished=Copper.boolean_difference(Cu_cube)
            if(self.position=='top'):
                Copper_dished=Copper_dished.rotate_y(180)
            plotter3=pv.Plotter()
            plotter3.add_mesh(Cu_cube,color='red',opacity=0.75)
            plotter3.add_mesh(Copper,color='orange',opacity=0.25)
            plotter3.add_mesh(Copper_dished,color='orange',opacity=0.5)
            plotter3.show()
        elif(self.indent=='sphere'):
            Cu_sphere=pv.Sphere(center=(0,0,0),radius=self.radius)
            Cu_sphere=Cu_sphere.translate((0,0,height_offset/2))
            Copper_dished=Copper.boolean_difference(Cu_sphere)
            if(self.position=='top'):
                Copper_dished=Copper_dished.rotate_y(180)
            plotter3=pv.Plotter()
            plotter3.add_mesh(Cu_sphere,color='black',opacity=0.75)
            plotter3.add_mesh(Copper,color='orange',opacity=0.25)
            plotter3.add_mesh(Copper_dished,color='orange',opacity=0.5)
            plotter3.show()
        if(self.position=='top'):
            #distance+=0.1
            Copper_dished=Copper_dished.translate((offset_x,offset_y,distance))
            Copper_dished=Copper_dished.translate((0,0,top_TiN_movement+0.1))
        else:
            Copper_dished=Copper_dished.translate((-offset_x,-offset_y,distance))
        return Copper_dished

#non-user interfaced code
TiN_r_top=Cu_r_top+0.01
TiN_h_top=Cu_h_top+0.01
TiN_r_bot=Cu_r_bot+0.01
TiN_h_bot=Cu_h_bot+0.01
bot_TiN_movement=(SiO2_h_bot)/2-(TiN_h_bot)
top_TiN_movement=(SiO2_h_bot)/2+(SiO2_h_top)/2
#generates the Top SiO2 block
SiO2_top_dimension=(SiO2_w_top,SiO2_d_top,SiO2_h_top)
SiO2_top_mat=Material("SiO2",SiO2_top_dimension,"Normal")
SiO2_top=gen_SiO2_block(SiO2_top_mat.shape,'top')
SiO2_top=SiO2_top.mesh_gen()
SiO2_top=SiO2_top.translate((0,0,top_TiN_movement))
#generates the Bottom SiO2 block
SiO2_bot_dimension=(SiO2_w_bot,SiO2_d_bot,SiO2_h_bot)
SiO2_bot_mat=Material("SiO2",SiO2_bot_dimension,"Normal")
SiO2_bot=gen_SiO2_block(SiO2_bot_mat.shape,'bot')
SiO2_bot=SiO2_bot.mesh_gen()
#Displays the 2 SiO2 blocks
# plot=pv.Plotter()
# plot.add_mesh(SiO2_top,color='cyan',opacity=0.75)
# plot.add_mesh(SiO2_bot,color='red',opacity=0.75)
# plot.show()
#generates the Top Thin TiN layer
TiN_dimension_top=(TiN_r_top,TiN_h_top)
TiN_top_mat=Material("TiN",TiN_dimension_top,"Finer")
TiN_top=gen_TiN_layer(TiN_top_mat.shape,'top')
TiN_top=TiN_top.mesh_gen()
TiN_top=TiN_top.translate((0,0,top_TiN_movement))
#generates the Bottom Thin TiN layer
TiN_dimension_bot=(TiN_r_bot,TiN_h_bot)
TiN_bot_mat=Material("TiN",TiN_dimension_bot,"Finer")
TiN_bot=gen_TiN_layer(TiN_bot_mat.shape,'bot')
TiN_bot=TiN_bot.mesh_gen()
#Displays the 2 TiN layers within the SiO2 blocks
# plot=pv.Plotter()
# plot.add_mesh(SiO2_bot,color='cyan',opacity=0.5)
# plot.add_mesh(TiN_bot,color='red',opacity=0.75)
# plot.add_mesh(SiO2_top,color='cyan',opacity=0.5)
# plot.add_mesh(TiN_top,color='green',opacity=0.75)
# plot.show()
#generates the Top Copper
Cu_top_dimension=(Cu_r_top,Cu_h_top)
Copper_top_mat=Material("Cu",Cu_top_dimension,"Finer")
Copper_top=gen_Copper_piece(Copper_top_mat.shape,Cu_dish_top,'top',recess_shape)
Copper_top=Copper_top.mesh_gen()
#generates the Bottom Copper
Cu_bot_dimension=(Cu_r_bot,Cu_h_bot)
Copper_bot_mat=Material("Cu",Cu_bot_dimension,"Finer")
Copper_bot=gen_Copper_piece(Copper_bot_mat.shape,Cu_dish_bot,'bot',recess_shape)
Copper_bot=Copper_bot.mesh_gen()

#generates the full assembly
plot=pv.Plotter()
plot.add_mesh(SiO2_bot,color='cyan',opacity=0.25)
plot.add_mesh(TiN_bot,color='silver',opacity=0.5)
plot.add_mesh(Copper_bot,color='red',opacity=1)
plot.add_mesh(SiO2_top,color='cyan',opacity=0.25)
plot.add_mesh(TiN_top,color='black',opacity=0.5)
plot.add_mesh(Copper_top,color='yellow',opacity=1)
plot.show()