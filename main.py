# Script for Generating The MatSeg Dataset
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
import MaterialMapping 
import SetScene
import time
import json

################################################################################################################################################################

#                                   Input Parameters: Input and OutPut paths

###################################################################################################################################################################



#------------------------Input parameters---------------------------------------------------------------------
MainOutDir="out_generated_data/" # folder where out put will be save
if not os.path.exists(MainOutDir): os.mkdir(MainOutDir)

# Hdri background folder, 3d object folder, Pbr materials folder, Images folder use to generate the UV map 
# Example HDRI_BackGroundFolder and PBRMaterialsFolder  and ObjectsFolder folders should be in the same folder as the script. 

HDRI_BackGroundFolder=r"HDRI_BackGround/" # Background hdri folder (taken from HDRI Haven site)
ObjectFolder=r"Objects/" #Folder of objects (like shapenet) 
pbr_folders = [r"PBRMaterials/"] # PBR materials folders to read PBR from, could contain few folders  
natural_image_dir=r"Natural_Images/"#random images that will be used to generate the materials UV map

material_dic_file = MainOutDir + "/Materials_Dictinary.json" # contain wich material appear in which image not currently used

NumSetsToRender=10 # How many set to render before you finish (how many images to create)
use_priodical_exits = False # Exit blender once every few sets to avoid memory leaks, assuming that the script is run inside sh Run.sh loop that will imidiatly restart blender fresh (use this if the generation seem to get slower over time).

 


#########################################################################################################################################################

#------------------Set material handling structures--------------------------------------------------------------------------
 
#material loader class
mat_loader=Materials.MaterialHandler(pbr_folders,material_dic_file)

#---------------List of materials that are part of the blender structure and will not be deleted between scenes------------------------------------------
 
MaterialsList=["Multiphase_Graph","Material_Group1","Material_Group","TwoPhaseFromImage","White","Black","PbrMaterial1","PbrMaterial2","TwoPhaseMaterial","GroundMaterial","TransparentLiquidMaterial","BSDFMaterial","BSDFMaterialLiquid","Glass","PBRReplacement"] # Materials that will be used
#---------------------------------------------------------------------------------------------------------

images_paths=[]
for fl in os.listdir(natural_image_dir): images_paths.append(natural_image_dir+"/"+fl)

#------------------------------------Create list with all hdri files in the folder (this used for backgroun image and illumination)-------------------------------------
hdr_list=[]
for hname in os.listdir(HDRI_BackGroundFolder): 
   if ".hdr" in hname:
         hdr_list.append(HDRI_BackGroundFolder+"//"+hname)


#-------------------------Create output folder--------------------------------------------------------------

if not os.path.exists(MainOutDir): os.mkdir(MainOutDir)

#==============Rendering engine parameters ==========================================

bpy.context.scene.render.engine = 'CYCLES' # 
bpy.context.scene.cycles.device = 'GPU' # If you have GPU 
bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL' # Not sure if this is really necessary but might help with sum surface textures
bpy.context.scene.cycles.samples = 120 #200, #900 # This work well for rtx 3090 for weaker hardware this can take lots of time
bpy.context.scene.cycles.preview_samples = 900 # This work well for rtx 3090 for weaker hardware this can take lots of time

bpy.context.scene.render.resolution_x = 1600 # image resulotion 
bpy.context.scene.render.resolution_y = 1600

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



#----------------------------Create list of Objects that will be loaded during the simulation---------------------------------------------------------------
ObjectList={}
ObjectList=Objects.CreateObjectList(ObjectFolder)
print("object list len",len(ObjectList))
#ClearMaterials(KeepMaterials=MaterialsList)
#main_phase_graph, uv,  MaterialDictionary = CreateMultiphaseMaterialGraph()
#----------------------------------------------------------------------
######################Main loop##########################################################\



scounter=0 # Count how many scene have been made in this run of the script (if folder exist and cnt have skipped one this will not be increased (cnt will)
cnt=0# counter name of output  this will be used as the name of the output folder
while(True):# Each cycle of this loop generate one image and segmentation map
 
        cnt+=1
        OutputFolder=MainOutDir+"/"+str(cnt)+"/" # sub outpur folder
       
        if  os.path.exists(OutputFolder): continue # Dont over run existing folder, if folder exist go to next number 
        if  not os.path.exists(OutputFolder):  os.mkdir(OutputFolder)
        
        mat_loader.initiate_scene_data(OutputFolder,cnt) # class for loading and handling materials
        scounter+=1
        

        
        #if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation folder to free space
        
        if scounter>NumSetsToRender: break
    
    
#================================Create scene load object and set material=============================================================================
        print("==========================================Start Scene Generation======================================================")
        print("Simulation number:"+str(cnt)+" Remaining:"+ str(NumSetsToRender))
        SetScene.CleanScene()  # Clear scence, Delete all objects in scence
   
      
#------------Load random object into scene center these are the main objects where the materials will map to---------------------------------
        print("Load main object")
        #MainObjectName=Objects.LoadRandomObject(ObjectList,random.uniform(30,50),[0,0,0])
        if np.random.rand()<0.5: # single main object
               MainObjectName = Objects.LoadRandomObject(ObjectList,random.uniform(40,60),[0,0,0])
        elif np.random.rand()<0.5:# multiple scatter main objects (merged to one object) 
               MainObjectName = Objects.LoadNMainObjects(ObjectList,NumObjects=np.random.randint(6)+1,MnPos=[-20,-20,-2],MxPos=[20,20,10],MnScale=10,MxScale=60)
        else:
               MainObjectName = Objects.LoadNMainObjects(ObjectList,NumObjects=np.random.randint(11)+1,MnPos=[-30,-30,-5],MxPos=[30,30,15],MnScale=10,MxScale=30)
#=============Remove double vertics (this is issue in some 3d  model that ruin UV mapping)=================================================================        
        
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[MainObjectName].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[MainObjectName]
        bpy.ops.object.editmode_toggle() #edit mode
        bpy.ops.mesh.remove_doubles() #remove overlapping faces
       
        bpy.ops.uv.smart_project(island_margin=0.03)
        bpy.ops.object.editmode_toggle() #back to object mode

#*************Create multiphase maps and materias, use random image to create UV map and apply this to ************************************************************        
        print("Load create UV map ")
        SetScene.ClearMaterials(KeepMaterials=MaterialsList)
        if np.random.rand()<0.85:
            main_phase_graph = MaterialMapping.CreateMultiphaseMaterialGraph(num_phases  = random.randint(2,8),material_loader=mat_loader,images_paths=images_paths) # map 2-8 materials to object
        else:
             main_phase_graph = MaterialMapping.CreateMultiphaseMaterialGraph(num_phases  = 2,material_loader=mat_loader,images_paths=images_paths)  # map 2 materials to object
        #x=ssfsfsfds
        MainObject = bpy.data.objects[MainObjectName]
       
#***************************SMOOTH objec (optional)******************************************************************
        if np.random.rand()<0.0:
            MainObject.select_set(True)
            bpy.context.view_layer.objects.active = MainObject
            bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
            bpy.context.object.modifiers["Subdivision"].levels = 2
            bpy.context.object.modifiers["Subdivision"].render_levels = 2
#**************************Replace the object materials*****************************************************************        
        print("Set Scene Creating enviroment and background and set camera")
        Materials.ReplaceMaterial(MainObject,main_phase_graph) # replace material on object
        
        MaxZ=MaxXY=20 # Size of object
       #-------------------------------------------Create ground plane and assign materials to it (optional)----------------------------------
        if np.random.rand()<0.25:
            PlaneSx,PlaneSy= SetScene.AddGroundPlane("Ground",x0=0,y0=0,z0=0,sx=MaxXY,sy=MaxXY) # Add plane for ground
            if np.random.rand()<10.9:
                   mat_loader.load_random_PBR_material(bpy.data.materials['GroundMaterial'].node_tree)
                   Materials.ReplaceMaterial(bpy.data.objects["Ground"],bpy.data.materials['GroundMaterial']) # Assign PBR material to ground plane (Physics based material) from PBRMaterialsFolder
#            
#            else: 
#                Materials.AssignMaterialBSDFtoObject(ObjectName="Ground",MaterialName="BSDFMaterial") 
        else: 
            with open(OutputFolder+'/NoGroundPlane.txt', 'w'): print("No Ground Plane")
        PlaneSx,PlaneSy=MaxXY*(np.random.rand()*4+2), MaxXY*(np.random.rand()*4+2)
    #------------------------Load random background hdri---------------------------------------------------------------   
        SetScene.AddBackground(hdr_list) # Add randonm Background hdri from hdri folder

    #..............................Create load  n objects into scene as background and shadows....................................................
        if np.random.rand()<0.2:
                 Objects.LoadNObjectsToScene(ObjectList,AvoidPos=[0,0,0],AvoidRad=0,NumObjects=np.random.randint(8)+1,MnPos=[-PlaneSx/2,-PlaneSy/2,-1],MxPos=[PlaneSx/2,PlaneSy/2,3],MnScale=(np.random.rand()*0.8+0.2)*MaxXY,MxScale=np.max([MaxXY,MaxZ])*(1+np.random.rand()*4))    
                
        if np.random.rand()<0.15:
                             SetScene.add_random_point_light() # Add random light source (optional, most light come the HDRI anyway)
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
                
#######################################Saving and Image Rendering################################################################################3  
        print("Saving data:",OutputFolder)        
        bpy.context.scene.render.engine = 'CYCLES'
        
       # x=sfsfsfs
        RenderSave.RenderImageAndSave(FileNamePrefix="RGB_",OutputFolder=OutputFolder) # Render image and save

    
           #------------------Save Segmentation mask-----------------------------------------------------------------------------
        
        RenderSave.SaveMaterialsMasks([MainObjectName],OutputFolder) # Save segmentation maps of all materials 
        RenderSave.SaveObjectVisibleMask([MainObject.name],OutputFolder +"/ObjectMaskOcluded") #mask of only visible region
    
        #-------------Save material properties This isnt really used at this point (but help indentify same material in different images, not used and unchecked)----------------------------------------------------
        mat_loader.save_scene_data()
    
        mat_loader.save_full_material_data(MainOutDir+ "/materials_data") # This keep list 
        mat_loader.save_full_material_data(MainOutDir+ "/materials_data_back")
        if cnt%100==0: 
            mat_loader.save_full_material_data(OutputFolder+ "/materials_data_"+str(cnt))
        
    
      
        
        open(OutputFolder+"/Finished.txt","w").close()
        print("DONE SAVING")
##################################Finish and clean scene######################################################################################    
        
        objs=[]
            #------------------------------Finish and clean data--------------------------------------------------
        
       
        #-------------Delete all objects from scene but keep materials---------------------------
        for nm in bpy.data.objects: objs.append(nm)
        for nm in objs:  
                bpy.data.objects.remove(nm)
       

        print("Cleaning")

        open(OutputFolder+"/Finished.txt","w").close() # add in the end of image generation and used to confirmed that all data was created for this scene (if this doesnt exist in folder it mean that generation wasnt complete (due crashes or something)
        
        # Clean images
        imlist=[]
        for nm in bpy.data.images: imlist.append(nm) 
        for nm in imlist:
            bpy.data.images.remove(nm)
        # Clean materials
     
        SetScene.ClearMaterials(KeepMaterials=MaterialsList)
        print("======================================Finished===========================================")
        SetScene.CleanScene()  # Delete all objects in scence
#---------------------------------------------------------------------------------------------------------------------------------------
        if use_priodical_exits and scounter>=20: # Break program and exit blender, allow blender to remove junk use this if you feel the generation becoming slower with time, and if you use Run.sh, otherwise ignore. 
             print("quit")
             bpy.ops.wm.quit_blender()
             break
            # with time it seem that this script slowing down, not sure why, . 
            # A way to solve it is to close the program and restart it once in  awhile.
            # By setting use_priodical_exits=True  the program will exist after 20 generation.
            # If you run the the Run.sh script in the terminal it will rerun this script in a loop. 
            # If use_priodical_exits=True and you run Run.sh then the program wil terminate and restart every 20 images  solving the slowing down problem.
            # Note that this problem is far smaller in blender 4.0 so this part might not be necessary.