
# Generate the MatSim Dataset 
# note that this script run with the blend file and refers to some
###############################Dependcies######################################################################################

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import json
import sys
filepath = bpy.data.filepath
homedir = os.path.dirname(filepath)
sys.path.append(homedir) # So the system will be able to find local imports
os.chdir(homedir)
import MaterialsHandling as Materials
import ObjectsHandling as Objects
import RenderingAndSaving as RenderSave
import SetScene
import time

################################################################################################################################################################

#                                    Main 

###################################################################################################################################################################


#------------------------Input parameters---------------------------------------------------------------------

# Example HDRI_BackGroundFolder and PBRMaterialsFolder  and ObjectsFolder folders should be in the same folder as the script. 
# Background hdri folder
HDRI_BackGroundFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/4k/" 
#
#"HDRI_BackGround/"
#r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/4k/" 
#ObjectFolder=r"/home/breakeroftime/Documents/Datasets/Shapenet/ShapeNetCoreV2/"
#Folder of objects (like shapenet) 
ObjectFolder=r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/" 
#r"Objects/"
#r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/" 
# folder where out put will be save
OutFolder="OutFolder/" # folder where out put will be save
pbr_folders = [r"/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR/",
r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/']
#r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/',
#r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/']
image_dir=r"/home/breakeroftime/Documents/Datasets/ADE20K_Parts_Pointer/Eval/Image/"
images_paths=[]
for fl in os.listdir(image_dir): images_paths.append(image_dir+"/"+fl)

NumSetsToRender=10
use_priodical_exits = False # Exit blender once every few sets to avoid memory leaks, assuming that the script is run inside Run.sh loop that will imidiatly restart blender fresh
 


#------------------Create PBR list-------------------------------------------------------- 
materials_lst = [] # List of all pbr materials folders path
for fff,fold in enumerate(pbr_folders): # go over all super folders 
    materials_lst.append([]) 
    for sdir in  os.listdir(fold): # go over all pbrs in folder
        pbr_path=fold+"//"+sdir+"//"
        if os.path.isdir(pbr_path):
              materials_lst[fff].append(pbr_path)
#------------------------------------Create list with all hdri files in the folder-------------------------------------
hdr_list=[]
for hname in os.listdir(HDRI_BackGroundFolder): 
   if ".hdr" in hname:
         hdr_list.append(HDRI_BackGroundFolder+"//"+hname)
####################################################################################################

#           Create material segmentation map turn all materials to black except 1 which is white do it only for the materials in the object their name in  appear in object names

###############################################################################################
def SaveMaterialsMasks(objnames,out_folder, MaterialDictionary):
      bpy.context.scene.render.engine = 'BLENDER_EEVEE'
      bpy.context.scene.render.image_settings.file_format = 'PNG'#'OPEN_EXR' # output format
      bpy.context.scene.world= bpy.data.worlds['BackgroundBlack'] # Set Background to black
    #-----set all background objects to black-----------------------------------
      for obj in   bpy.data.objects:
          if not obj.type=='MESH': continue
          if obj.name in objnames: continue
          obj.data.materials.clear()
          obj.data.materials.append(bpy.data.materials["Black"]) 
    
      mat_dic={} # data about material in each mask
#    #-----------Set all materials to black----------------------------------             
      for grp in  list(bpy.data.node_groups):
           if 'Material_Group.0' in grp.name:
               grp.nodes["Value"].outputs[0].default_value=0
               grp.links.new(grp.nodes["Value"].outputs[0],grp.nodes["Group Output"].inputs[0])
    #------turn one material white and save----------------------------------------
      for i,grp in  enumerate(list(bpy.data.node_groups)):
           if 'Material_Group.0' in grp.name:
               grp.nodes["Value"].outputs[0].default_value=255
               grp.links.new(grp.nodes["Value"].outputs[0],grp.nodes["Group Output"].inputs[0])
               bpy.context.scene.render.filepath = out_folder + "//mask"+str(i)+".png"
               bpy.ops.render.render(write_still=True)
               grp.nodes["Value"].outputs[0].default_value=0
               # Save material data to dictionary
#               for ky in MaterialDictionary:
#                   if MaterialDictionary[ky].name==grp.name:
#                        mat_dic["mask"+str(i)+".png"]=MaterialDictionary[grp.name]
#      with open(OutputFolder+'/MaterialsData.json', 'w') as fp: json.dump(mat_dic, fp)     
#################################Other parameters#########################################################
########################################################################################

def ClearMaterials(KeepMaterials): # clean materials from scene all materials except the ones in KeepMaterials
    print("Clearing materials from memory")
    mtlist=[]
    for nm in bpy.data.materials: 
        if nm.name not in KeepMaterials: mtlist.append(nm)
    for nm in mtlist:
        bpy.data.materials.remove(nm)
    
    group_list=[]
    for nm in bpy.data.node_groups: 
        if nm.name not in KeepMaterials: group_list.append(nm)
    for nm in group_list:
        bpy.data.node_groups.remove(nm)
###########################################################################################333
def load_materials(materials_dict):
    print("Load material")
#------set uve mapping mode
    rn=random.random()
    if rn<0.70:
       uv='camera'
    elif rn<0.47: 
       uv='object' 
    else: 
        uv='uv'
#--------------------------------------------------
    MaterialDictionary={}
    for mat_name in materials_dict:
        # Pick material type PBR/bsdf
        if random.random()<0.815: 
               matype1='pbr'
        else:
               matype1='bsdf'
        if random.random()<0.815: 
               matype2='pbr'
        else:
               matype2='bsdf'
        print("mat name",mat_name," mat ",materials_dict[mat_name])
        Materials.ChangeUVmapping(materials_dict[mat_name].node_tree,uvmode = uv) # set uv mapping in the material graph
        MaterialDictionary[mat_name]=Materials.ChangeMaterialMode(materials_dict[mat_name].node_tree,matype1,materials_lst)
    return  MaterialDictionary
###################################################################################################        
def SetPhaseSplitFromImage(phase_sep,images_paths):
    print("Set Phase spli uv map")
    x=3
  #  phase_sep.nodes["Separate Color"]
    # set color ramp
    phase_sep.nodes["Separate Color"].mode={0:'RGB',1:'HSV',2:'HSL'}[random.randint(0,2)]
  #  phase_sep.nodes["ColorRamp"].color_ramp.color_mode="HSV"# [‘RGB’, ‘HSV’, ‘HSL’]
    pos1=random.random()*0.4+0.3
    pos2=pos1#min([pos1+(random.random()**2)*0.2,0.8])
    phase_sep.nodes["ColorRamp"].color_ramp.elements[0].position=pos1
    phase_sep.nodes["ColorRamp"].color_ramp.elements[1].position=pos2
    phase_sep.nodes["ColorRamp"].color_ramp.interpolation = "LINEAR" #[‘EASE’, ‘CARDINAL’, ‘LINEAR’, ‘B_SPLINE’, ‘CONSTANT’
     
    indx=random.randint(0,len(images_paths)-1)
    phase_sep.nodes["Image Texture"].image=bpy.data.images.load(images_paths[indx])  
    # Translate
    phase_sep.nodes["Mapping"].inputs[1].default_value[0] = random.uniform(0, 30)
    phase_sep.nodes["Mapping"].inputs[1].default_value[1] = random.uniform(0, 30)
    phase_sep.nodes["Mapping"].inputs[1].default_value[2] = random.uniform(0, 30)
    # Rotate
    phase_sep.nodes["Mapping"].inputs[2].default_value[0] = random.uniform(0, 6.28318530718)
    phase_sep.nodes["Mapping"].inputs[2].default_value[1] = random.uniform(0, 6.28318530718)
    phase_sep.nodes["Mapping"].inputs[2].default_value[2] = random.uniform(0, 6.28318530718)
    # scale
#    scl=1
    #if random.random()<0.4:
    scl=10**random.uniform(-1, 0.2)
    phase_sep.nodes["Mapping"].inputs[3].default_value[0] = scl
    phase_sep.nodes["Mapping"].inputs[3].default_value[1] = scl
    phase_sep.nodes["Mapping"].inputs[3].default_value[2] = scl
    # choos which of the HSV channels will be use to generate the map
    map_mode= random.randint(0,2) 
    phase_sep.links.new(phase_sep.nodes["Separate Color"].outputs[random.randint(0,2)],phase_sep.nodes["ColorRamp"].inputs[0])
    
    
    #------set uve mapping mode
    uv_mode={0:'generated',1:'object',2:'uv'}[random.randint(0,2)]
    Materials.ChangeUVmapping(phase_sep,uv_mode)
################################################################################################################3
#def CreateMultiphaseMaterialGraph():
#    print("set main material multiphase graph")
#    mat = bpy.data.materials.new("Multiphase_Graph")
#    mat.use_nodes = True
#    nodes = mat.node_tree.nodes

#    phase_maps = {}
#    materials = {}
#    for i in range(1,6):
#        phase_maps[i] = nodes.new("ShaderNodeGroup")
#        phase_maps[i].node_tree = bpy.data.node_groups['TwoPhaseFromImage'].copy()
#        phase_maps[i].name = "Phase Map"+str(i)
#       ### bpy.data.materials['Main Material'].node_tree.nodes[""phase "+str(i)"]
#        phase_maps[i].location = [-i*200,0]
#        
#        materials[i] = nodes.new("ShaderNodeGroup")
#        materials[i].node_tree = bpy.data.node_groups["Material_Group"].copy()
#        materials[i].name = "Material "+str(i)
#       ### bpy.data.materials['Main Material'].node_tree.nodes[""phase "+str(i)"]
#        materials[i].location = [-i*200,200]
##------------------Create links--------------------------------------------
#    ntree=mat.node_tree
#    ntree.links.new(ntree.nodes["Material 1"].outputs[0],ntree.nodes["Phase Map1"].inputs[0])
#    ntree.links.new(ntree.nodes["Material 1"].outputs[1],ntree.nodes["Phase Map1"].inputs[2]) 
#    ntree.links.new(ntree.nodes["Material 2"].outputs[0],ntree.nodes["Phase Map1"].inputs[1])
#    ntree.links.new(ntree.nodes["Material 2"].outputs[1],ntree.nodes["Phase Map1"].inputs[3])          
#    
#    ntree.links.new(ntree.nodes["Phase Map1"].outputs[0],ntree.nodes["Material Output"].inputs[0])
#    ntree.links.new(ntree.nodes["Phase Map1"].outputs[1],ntree.nodes["Material Output"].inputs[2])   
##---------------------------set materials properties----------------------------------------------------------------
#    MaterialDictionary = load_materials(materials)
##--------------Set phase seperator---------------------------------------------------------------------------------
#    for ky in phase_maps:
#        SetPhaseSplitFromImage(phase_maps[ky].node_tree,images_paths)
#    return mat,  MaterialDictionary
################################################################################################################

# Reccursive create phase splits

#################################################################################################################
def GenerateNodeGraph(ntree,num_phases,bsdf_out, displacement_out,phase_maps = {},materials = {}, num_mats=0, num_splits=0):
     
     #  Add material
     if num_phases==1:
         num_mats  += 1
         mat = ntree.nodes.new("ShaderNodeGroup")
         materials[num_mats]=mat
         print("***********ADDing mat",num_mats,"\n\n\n\n",mat)
         mat.node_tree = bpy.data.node_groups["Material_Group"].copy()
         mat.name = "Material "+str(num_mats)
         ##ntree = materials[num_mats].node_tree
         ntree.links.new(mat.outputs[0],bsdf_out)
         ntree.links.new(mat.outputs[1],displacement_out)            
       ### bpy.data.materials['Main Material'].node_tree.nodes[""phase "+str(i)"]
         mat.location = [-(num_mats+num_splits)*200,num_splits*200]
         
         return materials,phase_maps, num_mats, num_splits
    
     #  Add phase split
     num_splits += 1
     print("CREATIng split",num_splits,"**********&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
     phsplit = ntree.nodes.new("ShaderNodeGroup")
     phase_maps[num_splits] = phsplit 
     phsplit.node_tree = bpy.data.node_groups['TwoPhaseFromImage'].copy()
     phsplit.name = "Phase Map"+str(num_splits)
     phsplit.location = [-num_splits*200,0]
     ntree.links.new(phsplit.outputs[0],bsdf_out)
     ntree.links.new(phsplit.outputs[1],displacement_out)
#       phase_maps[num_splits] = ntree.nodes.new("ShaderNodeGroup")
#     phase_maps[num_splits].node_tree = bpy.data.node_groups['TwoPhaseFromImage'].copy()
#     phase_maps[num_splits].name = "Phase Map"+str(num_splits)
#     phase_maps[num_splits].location = [-num_splits*200,0]
#     ntree.links.new(phase_maps[num_splits].outputs[0],bsdf_out)
#     ntree.links.new(phase_maps[num_splits].outputs[1],displacement_out)
     
     num_phases1 = int(np.floor(num_phases/2))
     num_phases2 = int(np.ceil(num_phases/2))
     print("Numphases:",num_phases1,num_phases2)
     materials, phase_maps, num_mats, num_splits = GenerateNodeGraph(ntree=ntree,num_phases=num_phases1,bsdf_out=phsplit.inputs[0], 
                        displacement_out=phsplit.inputs[2],phase_maps = phase_maps,materials = materials, num_mats = num_mats, num_splits = num_splits)
     materials, phase_maps, num_mats, num_splits = GenerateNodeGraph(ntree=ntree,num_phases=num_phases2,bsdf_out=phsplit.inputs[1], 
                       displacement_out=phsplit.inputs[3],phase_maps = phase_maps,materials = materials, num_mats = num_mats , num_splits = num_splits)
     return materials,phase_maps, num_mats, num_splits
     
     
     

################################################################################################################3

# Main function for creating phases seperation graph

###############################################################################################################
def CreateMultiphaseMaterialGraph(num_phases = 2):
    print("set main material multiphase graph")
    mat = bpy.data.materials.new("Multiphase_Graph")
    mat.use_nodes = True
#    nodes = mat.node_tree.nodes
#    phase_maps = {}
#    materials = {}
    ntree=mat.node_tree
    materials, phase_maps, num_mats, num_splits = GenerateNodeGraph(ntree=ntree,num_phases=num_phases,bsdf_out=ntree.nodes["Material Output"].inputs[0], displacement_out=ntree.nodes["Material Output"].inputs[2],materials={},phase_maps={})
#    for i in range(1,6):
#        phase_maps[i] = nodes.new("ShaderNodeGroup")
#        phase_maps[i].node_tree = bpy.data.node_groups['TwoPhaseFromImage'].copy()
#        phase_maps[i].name = "Phase Map"+str(i)
#       ### bpy.data.materials['Main Material'].node_tree.nodes[""phase "+str(i)"]
#        phase_maps[i].location = [-i*200,0]
#        
#        materials[i] = nodes.new("ShaderNodeGroup")
#        materials[i].node_tree = bpy.data.node_groups["Material_Group"].copy()
#        materials[i].name = "Material "+str(i)
#       ### bpy.data.materials['Main Material'].node_tree.nodes[""phase "+str(i)"]
#        materials[i].location = [-i*200,200]
##------------------Create links--------------------------------------------
#    ntree=mat.node_tree
#    ntree.links.new(ntree.nodes["Material 1"].outputs[0],ntree.nodes["Phase Map1"].inputs[0])
#    ntree.links.new(ntree.nodes["Material 1"].outputs[1],ntree.nodes["Phase Map1"].inputs[2]) 
#    ntree.links.new(ntree.nodes["Material 2"].outputs[0],ntree.nodes["Phase Map1"].inputs[1])
#    ntree.links.new(ntree.nodes["Material 2"].outputs[1],ntree.nodes["Phase Map1"].inputs[3])          
#    
#    ntree.links.new(ntree.nodes["Phase Map1"].outputs[0],ntree.nodes["Material Output"].inputs[0])
#    ntree.links.new(ntree.nodes["Phase Map1"].outputs[1],ntree.nodes["Material Output"].inputs[2])   
#---------------------------set materials properties----------------------------------------------------------------
    MaterialDictionary = load_materials(materials)
#--------------Set phase seperator---------------------------------------------------------------------------------
    print("phase map",phase_maps)
    for ky in phase_maps:
        print("KEY",ky)
        SetPhaseSplitFromImage(phase_maps[ky].node_tree,images_paths)

    return mat,  MaterialDictionary  
         
    
##########################################################################################################################



NumSimulationsToRun=2              # Number of simulation to run

#==============Set Rendering engine parameters (for image creaion)==========================================

bpy.context.scene.render.engine = 'CYCLES' # 
bpy.context.scene.cycles.device = 'GPU' # If you have GPU 
bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL' # Not sure if this is really necessary but might help with sum surface textures
bpy.context.scene.cycles.samples = 120 #200, #900 # This work well for rtx 3090 for weaker hardware this can take lots of time
bpy.context.scene.cycles.preview_samples = 900 # This work well for rtx 3090 for weaker hardware this can take lots of time

bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000

#bpy.context.scene.eevee.use_ssr = True
#bpy.context.scene.eevee.use_ssr_refraction = True
bpy.context.scene.cycles.caustics_refractive=True
bpy.context.scene.cycles.caustics_reflective=True
bpy.context.scene.cycles.use_preview_denoising = True
bpy.context.scene.cycles.use_denoising = True #****************************


# get_devices() to let Blender detects GPU device
#bpy.context.preferences.addons["cycles"].preferences.get_devices()
#print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
#for d in bpy.context.preferences.addons["cycles"].preferences.devices:
#    d["use"] = 1 # Using all devices, include GPU and CPU
#    print(d["name"], d["use"])

#---------------List of materials that are part of the blender structure and will not be deleted------------------------------------------
MaterialsList=["Multiphase_Graph","Material_Group1","Material_Group","TwoPhaseFromImage","White","Black","PbrMaterial1","PbrMaterial2","TwoPhaseMaterial","GroundMaterial","TransparentLiquidMaterial","BSDFMaterial","BSDFMaterialLiquid","Glass","PBRReplacement"] # Materials that will be used

#-------------------------Create output folder--------------------------------------------------------------



if not os.path.exists(OutFolder): os.mkdir(OutFolder)

#----------------------------Create list of Objects that will be loaded during the simulation---------------------------------------------------------------
ObjectList={}
ObjectList=Objects.CreateObjectList(ObjectFolder)
print("object list len",len(ObjectList))
#ClearMaterials(KeepMaterials=MaterialsList)
#main_phase_graph, uv,  MaterialDictionary = CreateMultiphaseMaterialGraph()
#----------------------------------------------------------------------
######################Main loop##########################################################\
# loop 1: select materials, loop 2: create scences, loop 3: set materials ratios and render
 # Set the device_type
#bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA" # or "OPENCL"


scounter=0 # Count how many scene have been made
for cnt in range(8):#NumSetsToRender):
##---------------------------create folder-----------------------------------------   
        OutputFolder=OutFolder+"/"+str(cnt)+"/"
#        if  os.path.exists(OutputFolder): continue # Dont over run existing folder continue from where you started
        if  not os.path.exists(OutputFolder):  os.mkdir(OutputFolder)
        scounter+=1

        ##MainOutputFolder
        print("Add material")

        
        #if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation folder to free space
        if NumSimulationsToRun==0: break
    
    #    #================================Create scene load object and set material=============================================================================
        print("=========================Start====================================")
        print("Simulation number:"+str(cnt)+" Remaining:"+ str(NumSimulationsToRun))
        SetScene.CleanScene()  # Delete all objects in scence
   
      
    #    #------------------------------Load random object into scene center---------------------------------

        MainObjectName=Objects.LoadRandomObject(ObjectList,random.uniform(30,50),[0,0,0])
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[MainObjectName].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[MainObjectName]
        bpy.ops.object.editmode_toggle() #edit mode
        bpy.ops.mesh.remove_doubles() #remove overlapping faces
       
        bpy.ops.uv.smart_project(island_margin=0.03)
        bpy.ops.object.editmode_toggle() #back to object mode
 
#*************Create multiphase maps and materiasl************************************************************        

        ClearMaterials(KeepMaterials=MaterialsList)
        main_phase_graph,   MaterialDictionary = CreateMultiphaseMaterialGraph(num_phases = random.randint(1,6))
        MainObject = bpy.data.objects[MainObjectName]
#***************************SMOOTH optional******************************************************************
        if np.random.rand()<0.0:
            MainObject.select_set(True)
            bpy.context.view_layer.objects.active = MainObject
            bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
            bpy.context.object.modifiers["Subdivision"].levels = 2
            bpy.context.object.modifiers["Subdivision"].render_levels = 2
#**************************Replace the object materials*****************************************************************        
        print("material", main_phase_graph)
        Materials.ReplaceMaterial(MainObject,main_phase_graph) # replace material on object
        
        MaxZ=MaxXY=20 # Size of object
       #-------------------------------------------Create ground plane and assign materials to it----------------------------------
        if np.random.rand()<0.25:
            PlaneSx,PlaneSy= SetScene.AddGroundPlane("Ground",x0=0,y0=0,z0=0,sx=MaxXY,sy=MaxXY) # Add plane for ground
            if np.random.rand()<0.9:
                   Materials.load_random_PBR_material(bpy.data.materials['GroundMaterial'].node_tree,materials_lst)
                   Materials.ReplaceMaterial(bpy.data.objects["Ground"],bpy.data.materials['GroundMaterial']) # Assign PBR material to ground plane (Physics based material) from PBRMaterialsFolder
            
            else: 
                Materials.AssignMaterialBSDFtoObject(ObjectName="Ground",MaterialName="BSDFMaterial") 
        else: 
            with open(OutputFolder+'/NoGroundPlane.txt', 'w'): print("No Ground Plane")
        PlaneSx,PlaneSy=MaxXY*(np.random.rand()*4+2), MaxXY*(np.random.rand()*4+2)
    #------------------------Load random background hdri---------------------------------------------------------------   
        SetScene.AddBackground(hdr_list) # Add randonm Background hdri from hdri folder

    #..............................Create load  n objects into scene as background....................................................
        if np.random.rand()<0.25:
                 Objects.LoadNObjectsToScene(ObjectList,AvoidPos=[0,0,0],AvoidRad=0,NumObjects=np.random.randint(8),MnPos=[-PlaneSx/2,-PlaneSy/2,-1],MxPos=[PlaneSx/2,PlaneSy/2,3],MnScale=(np.random.rand()*0.8+0.2)*MaxXY,MxScale=np.max([MaxXY,MaxZ])*(1+np.random.rand()*4))    
                
      
    #-----------------Save materials properties as json files------------------------------------------------------------
#        if not  os.path.exists(OutputFolder): os.mkdir(OutputFolder)
#        print("+++++++++++++++++++++Content material++++++++++++++++++++++++++++++")
#        print(ContentMaterial)
#        if ContentMaterial["TYPE"]!="NONE":
#                  with open(OutputFolder+'/ContentMaterial.json', 'w') as fp: json.dump(ContentMaterial, fp)
#    
#        


    #...........Set Scene and camera postion..........................................................
        SetScene.RandomlySetCameraPos(name="Camera",VesWidth = MaxXY,VesHeight = MaxZ)
        with open(OutputFolder+'/CameraParameters.json', 'w') as fp: json.dump( SetScene.CameraParamtersToDictionary(), fp)
                
#######################################################################################################################3
#            #-------------------------------------------------------Save images--------------------------------------------------------------    
                
        bpy.context.scene.render.engine = 'CYCLES'
        print("Saving Images")
        print(OutputFolder)
       # x=sfsfsfs
        RenderSave.RenderImageAndSave(FileNamePrefix="RGB_",OutputFolder=OutputFolder) # Render image and save

        print("DONE SAVING")
        

           #------------------Save Segmentation mask-----------------------------------------------------------------------------
        SaveMaterialsMasks([MainObjectName],OutputFolder,MaterialDictionary)
        RenderSave.SaveObjectVisibleMask([MainObject.name],OutputFolder +"/ObjectMaskOcluded") #mask of only visible region
    
        print("DONE SAVING")
        
        open(OutputFolder+"/Finished.txt","w").close()
        objs=[]
        #-------------Delete all objects from scene but keep materials---------------------------
        for nm in bpy.data.objects: objs.append(nm)
        for nm in objs:  
                bpy.data.objects.remove(nm)
       
    #------------------------------Finish and clean data--------------------------------------------------
        

        print("Cleaning")

        open(OutputFolder+"/Finished.txt","w").close()
        
        # Clean images
        imlist=[]
        for nm in bpy.data.images: imlist.append(nm) 
        for nm in imlist:
            bpy.data.images.remove(nm)
        # Clean materials

        ClearMaterials(KeepMaterials=MaterialsList)
        print("========================Finished==================================")
        SetScene.CleanScene()  # Delete all objects in scence
#        if use_priodical_exits and scounter>=12: # Break program and exit blender, allow blender to remove junk
#            #  print("Resting for a minute")
#            #  time.sleep(30)
#              break
##    if use_priodical_exits:
##       print("quit")
##       bpy.ops.wm.quit_blender()
##          #  break
