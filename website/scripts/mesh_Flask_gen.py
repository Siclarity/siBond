import pyvista as pv
import numpy as np
from json import dumps,load
import ast
from os.path import join,exists
from os import remove
from shutil import move
#This will convert all of the stringified dictionary to integers when coming from gds upload
def convert_to_dict_and_keys(input_dict):
    for key, value in list(input_dict.items()):
        # Convert the key to an integer
        int_key = int(key)
        value = value.replace(";", ",")
        # Safely evaluate the string to convert it to a dictionary
        input_dict[int_key] = ast.literal_eval(value)
        # Remove the old string key
        del input_dict[key]
    return input_dict

def create_mesh(JSON_st):
    pv.global_theme.allow_empty_mesh = True
    site_information={}
    Js_in=JSON_st
    print(f'In Mesh_Flask_gen {Js_in}')
    keys=[]
    #Converts the string to either integer, double, or stay as string
    for key, value in Js_in.items():
        # print(key)
        keys.append(key)
        if key=='Dictionary':
            Js_in_dict=convert_to_dict_and_keys(Js_in['Dictionary'])
            print(f'Unique Sites:{Js_in_dict}')
        else:
            try:
                Js_in[key] = int(value)
            except ValueError:
                try:
                    Js_in[key] = float(value)
                except ValueError:
                    pass
    print(f'Converted Dict:{Js_in}')
    number_of_meshes=0
    meshes_directory =join('static', 'meshes')
    gds=False
    if keys[0]=='Dictionary':
        print("From GDS")
        number_of_meshes=len(Js_in_dict)
        gds=True
        print(f'{number_of_meshes} unique meshes')
        dbUnit=Js_in['DBUnit']
        print(dbUnit)
    else:
        print("From Create your own mesh")
        number_of_meshes=1
    count=0
    while count< number_of_meshes:
        #if this was from the GDS then there is a difference 
        if(gds):
            print(Js_in_dict[count])
            current_count=Js_in_dict[count]
            s1=current_count.get('Shape 1 bounds:',None)
            if s1:
                x1,y1,x2,y2=s1
                s1_width=x2-x1
                s1_height=y2-y1
            s2=current_count.get('Shape 2 bounds:',None)
            if s2:
                x1,y1,x2,y2=s2
                s2_width=x2-x1
                s2_height=y2-y1
            #Top is s2, Bot is s1
            SiO2_w_top=abs(Js_in['OffsetM2'])
            SiO2_d_top=abs(Js_in['OffsetM2'])
            SiO2_h_top=abs(Js_in['HeightM2'])
            Cu_r_top_type=current_count.get('Shape 2 type:')
            Cu_r_top=s2_width*dbUnit
            Cu_h_top=s2_height*dbUnit
            Cu_dish_top=abs(Js_in['HeightV1V2'])

            SiO2_w_bot=abs(Js_in['OffsetM1'])
            SiO2_d_bot=abs(Js_in['OffsetM1'])
            SiO2_h_bot=abs(Js_in['HeightM1'])
            #Will need this for later different shapes types of Copper
            Cu_r_bot_type=current_count.get('Shape 1 type:')
            Cu_r_bot=s1_width*dbUnit
            Cu_h_bot=s1_height*dbUnit
            Cu_dish_bot=abs(Js_in['HeightV1V2'])

            offset_x=abs(Js_in['OffsetV1V2'])
            offset_y=0

            recess_shape="ellipse"
        #if this is just the Create your own mesh we can assign from the dictionary 
        else:
            SiO2_w_top=Js_in['TSiO2w']
            SiO2_d_top=Js_in['TSiO2h']
            SiO2_h_top=Js_in['TSiO2l']
            Cu_r_top_type='Cylinder'
            Cu_r_top=Js_in['TCopperR']
            Cu_h_top=Js_in['TCopperH']
            Cu_dish_top=Js_in['TRecess']*0.001

            SiO2_w_bot=Js_in['BSiO2w']
            SiO2_d_bot=Js_in['BSiO2h']
            SiO2_h_bot=Js_in['BSiO2l']
            Cu_r_bot_type='Cylinder'
            Cu_r_bot=Js_in['BCopperR']
            Cu_h_bot=Js_in['BCopperH']
            Cu_dish_bot=Js_in['BRecess']*0.001
            if Js_in['O_x']=='':
                offset_x=0
            else:
                offset_x=Js_in['O_x']
            if Js_in['O_y']=='':
                offset_y=0
            else:
                offset_y=Js_in['O_y']
            recess_shape=Js_in['BRecessShape']
            # SiO2_w_top=Js_in.get('TSiO2w',None)
            # SiO2_d_top=Js_in.get('TSiO2h',None)
            # SiO2_h_top=Js_in.get('TSiO2l',None)
            # Cu_r_top_type='Cylinder'
            # Cu_r_top=Js_in.get('TCopperR',None)
            # Cu_h_top=Js_in.get('TCopperH',None)
            # Cu_dish_top=Js_in.get('TRecess',0)*0.001

            # SiO2_w_bot=Js_in.get('BSiO2w',None)
            # SiO2_d_bot=Js_in.get('BSiO2h',None)
            # SiO2_h_bot=Js_in.get('BSiO2l',None)
            # Cu_r_bot_type='Cylinder'
            # Cu_r_bot=Js_in.get('BCopperR',None)
            # Cu_h_bot=Js_in.get('BCopperH',None)
            # Cu_dish_bot=Js_in.get('BRecess',0)*0.001
            # if Js_in['O_x']=='':
            #     offset_x=0
            # else:
            #     offset_x=Js_in.get('O_x',0)
            # if Js_in['O_y']=='':
            #     offset_y=0
            # else:
            #     offset_y=Js_in.get('O_y',0)
            # recess_shape=Js_in['BRecessShape']
            
        
        shift_recess_top=0
        shift_recess_bot=0
        CD=0
        temp=300
        print(SiO2_w_top,SiO2_d_top,SiO2_h_top,Cu_r_top,Cu_h_top,Cu_dish_top,SiO2_h_bot,SiO2_w_bot,SiO2_d_bot,Cu_r_bot,Cu_h_bot,Cu_dish_bot, offset_x,offset_y,recess_shape, Cu_dish_top,Cu_dish_bot)
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
        SiO2_top=SiO2_top.mesh_gen(TiN_r_top,TiN_h_top,offset_x,offset_y)
        SiO2_top=SiO2_top.translate((0,0,top_TiN_movement))
        #generates the Bottom SiO2 block
        SiO2_bot_dimension=(SiO2_w_bot,SiO2_d_bot,SiO2_h_bot)
        SiO2_bot_mat=Material("SiO2",SiO2_bot_dimension,"Normal")
        SiO2_bot=gen_SiO2_block(SiO2_bot_mat.shape,'bot')
        SiO2_bot=SiO2_bot.mesh_gen(TiN_r_bot,TiN_h_bot,offset_x,offset_y)
        #Displays the 2 SiO2 blocks
        # plot=pv.Plotter()
        # plot.add_mesh(SiO2_top,color='cyan',opacity=0.75)
        # plot.add_mesh(SiO2_bot,color='red',opacity=0.75)
        # plot.show()
        #generates the Top Thin TiN layer
        TiN_dimension_top=(TiN_r_top,TiN_h_top)
        TiN_top_mat=Material("TiN",TiN_dimension_top,"Finer")
        TiN_top=gen_TiN_layer(TiN_top_mat.shape,'top')
        TiN_top=TiN_top.mesh_gen(Cu_r_top,Cu_h_top,offset_x,offset_y,SiO2_h_top)
        TiN_top=TiN_top.translate((0,0,top_TiN_movement))
        #generates the Bottom Thin TiN layer
        TiN_dimension_bot=(TiN_r_bot,TiN_h_bot)
        TiN_bot_mat=Material("TiN",TiN_dimension_bot,"Finer")
        TiN_bot=gen_TiN_layer(TiN_bot_mat.shape,'bot')
        TiN_bot=TiN_bot.mesh_gen(Cu_r_bot,Cu_h_bot,offset_x,offset_y,SiO2_h_bot)
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
        Copper_top=Copper_top.mesh_gen(shift_recess_top,TiN_h_top,SiO2_h_top,offset_x,offset_y,top_TiN_movement)
        #generates the Bottom Copper
        Cu_bot_dimension=(Cu_r_bot,Cu_h_bot)
        Copper_bot_mat=Material("Cu",Cu_bot_dimension,"Finer")
        Copper_bot=gen_Copper_piece(Copper_bot_mat.shape,Cu_dish_bot,'bot',recess_shape)
        Copper_bot=Copper_bot.mesh_gen(shift_recess_bot,TiN_h_bot,SiO2_h_bot,offset_x,offset_y,0)

        #generates the full assembly
        # plot=pv.Plotter()
        # plot.add_mesh(SiO2_bot,color='cyan',opacity=0.25)
        # plot.add_mesh(TiN_bot,color='silver',opacity=0.5)
        # plot.add_mesh(Copper_bot,color='red',opacity=1)
        # plot.add_mesh(SiO2_top,color='cyan',opacity=0.25)
        # plot.add_mesh(TiN_top,color='black',opacity=0.5)
        # plot.add_mesh(Copper_top,color='yellow',opacity=1)
        # plot.show()
        count+=1
        
        meshes = [
            ("SiO2_bot", SiO2_bot),
            ("TiN_bot", TiN_bot),
            ("Copper_bot", Copper_bot),
            ("SiO2_top", SiO2_top),
            ("TiN_top", TiN_top),
            ("Copper_top", Copper_top)
        ]
        # Loop through each mesh and save it, then move to the meshes directory
        for mesh_name, mesh_obj in meshes:
            # Save the mesh file
            file_name = f'{mesh_name}{count}.vtk'
            mesh_obj.save(file_name)
            # Move the saved mesh to the static/meshes directory
            target_path = join(meshes_directory, file_name)
            if exists(target_path):
                remove(target_path)
                print("Mesh Deleted")
            move(file_name, target_path) 

        site_information[count]={"Top SiO2 Width":SiO2_w_top,"Top SiO2 Height":SiO2_d_top,"Top SiO2 Depth":SiO2_h_top,"Top Cu Radius":Cu_r_top,"Top Cu Height":Cu_h_top, "Top Recess Value":Cu_dish_top, "Bot SiO2 Width":SiO2_w_bot, "Bot SiO2 Height":SiO2_d_bot,"Bot SiO2 Depth":SiO2_h_bot,"Bot Cu Radius":Cu_r_bot,"Bot Cu Height":Cu_h_bot, "Bot Recess Value":Cu_dish_bot, "Offset X":offset_x,"Offset Y":offset_y}
    return site_information

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
    def mesh_gen(self,TiN_r,TiN_h,offset_x,offset_y):
        SiO2_cube=pv.Cube(center=(0,0,0),bounds=(-(self.width/2),(self.width/2),-(self.depth/2), (self.depth/2), -(self.height/2), (self.height/2)))
        if (self.position=='top'):#need to make sure that we have the correct TiN for the correct SiO2 block
            TiN_hole=pv.Cylinder(center=(0,0,0),radius=TiN_r,height=TiN_h)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=(TiN_h)/2-(self.height/2)
            dist-=0.1
            distance=round(dist,1)
            TiN_hole=TiN_hole.translate((offset_x,offset_y,distance))
        elif(self.position=='bot'):
            TiN_hole=pv.Cylinder(center=(-offset_x,-offset_y,0),radius=TiN_r,height=TiN_h)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=abs((TiN_h)/2-(self.height/2))
            dist+=0.1
            distance=round(dist,1)
            TiN_hole=TiN_hole.translate((-offset_x,-offset_y,distance))
        SiO2_cube=SiO2_cube.triangulate()
        TiN_hole=TiN_hole.triangulate()
        SiO2_cube_fin=SiO2_cube.boolean_difference(TiN_hole)
        # plotter=pv.Plotter()
        # plotter.add_mesh(SiO2_cube_fin,color="cyan",opacity=0.75)
        #plotter.add_mesh(TiN_hole,color="gray",opacity=0.9)
        # plotter.show()
        return SiO2_cube_fin

#purpose of this class is to generate the TiN thin layer
class gen_TiN_layer:
    def __init__(self,shape,position):
        self.radius,self.height=shape
        self.position=position
    def mesh_gen(self,Cu_r,Cu_h,offset_x,offset_y,offset_z):
        if (self.position=='top'):#need to make sure that we have the correct TiN for the correct SiO2 block
            TiN_hole=pv.Cylinder(center=(0,0,0),radius=self.radius,height=self.height)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=(self.height)/2-(offset_z/2)
            dist-=0.1
            Copper_rem=pv.Cylinder(center=(0,0,0), radius=Cu_r, height=Cu_h)
            Copper_rem=Copper_rem.rotate_y(90)
        elif(self.position=='bot'):
            TiN_hole=pv.Cylinder(center=(0,0,0),radius=self.radius,height=self.height)
            TiN_hole=TiN_hole.rotate_y(90)
            dist=abs((self.height)/2-(offset_z/2))
            dist+=0.1
            Copper_rem=pv.Cylinder(center=(0,0,0), radius=Cu_r, height=Cu_h)
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
            self.indent_depth=dim
        elif(indent=='sphere'):
            self.indent_radius=dim
        self.position=position
        self.radius,self.height=shape
        self.indent=indent
    def mesh_gen(self,recess,TiN_h,SiO2_h,offset_x,offset_y,offset_z):
        height_offset=0
        if(self.position=='top'):
            height_offset=self.height-recess
            dist=(TiN_h+recess)/2-(SiO2_h/2)
            dist-=0.1
        elif(self.position=='bot'):
            height_offset=self.height-recess
            dist=abs((TiN_h+recess)/2-(SiO2_h/2))
            dist+=0.1
        distance=round(dist,1)
        Copper=pv.Cylinder(radius=self.radius, height=height_offset, center=(0,0,0))
        Copper=Copper.rotate_y(90)
        Copper=Copper.triangulate()
        if(self.indent=='ellipse'):#seems to work
            # Define the ellipsoid parameters
            # print(f"Z Center:{height_offset/2}")
            # print(f"Recess value:{self.indent_radius}")
            center = np.array([0,0,height_offset/2])  # Center of the ellipsoid (x, y, z)
            # print(f'Center:{center}')
            #radii = np.array([1,1,Cu_dish_top)
            radii = np.array([1,1,self.indent_radius/self.radius])  # Radii along x, y, and z axes
            # print(f'Radii:{radii}')
            # Create a mesh of the unit sphere (scaled to make it an ellipsoid)
            sphere = pv.Sphere(radius=self.radius, theta_resolution=50, phi_resolution=50)
            # Apply scaling to transform the sphere into an ellipsoid
            transform = np.diag(radii.tolist() + [1])  # Scaling matrix
            # print(f'Transform:{transform}')
            ellipsoid = sphere.transform(transform, inplace=False)
            # print(f"Ellipse before translation:{ellipsoid}")
            # Translate the ellipsoid to the desired coordinates
            ellipsoid.translate(center, inplace=True)
            # print(f"Ellipse after translation:{ellipsoid}")
            # Ellipsoid with a long x-axis
            # ellipsoid = pv.ParametricEllipsoid(10, 5, 5)
            if(self.position=='top'):
                # ellipsoid.translate((0,0,-1),inplace=True)
                Copper_dished=Copper.boolean_difference(ellipsoid)
                # print(f'Top ellipsoid position:{ellipsoid}')
                Copper_dished=Copper_dished.rotate_y(180)
            else:
                # ellipsoid.translate(center, inplace=True)
                # print(f'Bot ellipsoid position:{ellipsoid}')
                Copper_dished=Copper.boolean_difference(ellipsoid)
            # plotter3=pv.Plotter()
            #plotter3.add_mesh(ellipsoid,color="green",opacity=0.75)
            # plotter3.add_mesh(ellipsoid,color='black',opacity=0.9)
            # plotter3.add_mesh(Copper_dished,color="orange",opacity=0.9)
            # plotter3.show()
            
        elif(self.indent=='square'):
            Cu_cube=pv.Cube(center=(0,0,0),bounds=(-(self.indent_depth),(self.indent_depth),-(self.indent_depth),(self.indent_depth),-(self.indent_depth),(self.indent_depth)))
            Cu_cube=Cu_cube.triangulate()
            Cu_cube=Cu_cube.translate((0,0,height_offset/2))
            Copper_dished=Copper.boolean_difference(Cu_cube)
            if(self.position=='top'):
                Copper_dished=Copper_dished.rotate_y(180)
            # plotter3=pv.Plotter()
            # plotter3.add_mesh(Cu_cube,color='red',opacity=0.75)
            # plotter3.add_mesh(Copper,color='orange',opacity=0.25)
            # plotter3.add_mesh(Copper_dished,color='orange',opacity=0.5)
            # plotter3.show()
        elif(self.indent=='sphere'):
            Cu_sphere=pv.Sphere(center=(0,0,0),radius=self.radius)
            Cu_sphere=Cu_sphere.translate((0,0,height_offset/2))
            Copper_dished=Copper.boolean_difference(Cu_sphere)
            if(self.position=='top'):
                Copper_dished=Copper_dished.rotate_y(180)
            # plotter3=pv.Plotter()
            # plotter3.add_mesh(Cu_sphere,color='black',opacity=0.75)
            # plotter3.add_mesh(Copper,color='orange',opacity=0.25)
            # plotter3.add_mesh(Copper_dished,color='orange',opacity=0.5)
            # plotter3.show()
        if(self.position=='top'):
            #distance+=0.1
            Copper_dished=Copper_dished.translate((offset_x,offset_y,distance))
            Copper_dished=Copper_dished.translate((0,0,offset_z+0.1))
        else:
            Copper_dished=Copper_dished.translate((-offset_x,-offset_y,distance-0.1))
        return Copper_dished