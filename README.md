# MatSeg Material Segmentation dataset generation script: Generate Images with materials distributed on objects and their segmentation maps
Generation script for the MatSeg Dataset for zero-shot class-agnostic material states segmentation.
This script will procedurally generate an image dataset of multiple materials  distributed on object surfaces. 
The distribution will be determined by patterns extracted from natural images and their segmentation maps. 

See the paper [Learning Zero-Shot Material States Segmentation, by Implanting Natural Image Patterns in Synthetic Data](https://arxiv.org/pdf/2403.03309.pdf) for more details. 

The generated dataset (generated using this script) can be found  at: [1](https://e.pcloud.link/publink/show?code=kZHCcnZOfzqInb3anSl7xzFBoqCDmkr2JKV),[2](https://icedrive.net/s/SBb3g9WzQ5wZuxX9892Z3R4bW8jw)

## What does this generate?

Generate the MatSim Dataset for class-independent zero-shot material segmentation: Random materials  distributed on scene and object according to natural patterns.
It will take a set of natural images and extract patterns from them it will use these patterns to map a set of random materials to random object surfaces. 
The resulting data set can be used to train the net for Zero-Shot Material Segmentation (segmentation of material and their states without needing to ever encounter the material class during training).
The general concept shown in Figures 1/2 and described in [Learning Zero-Shot Material States Segmentation, by Implanting Natural Image Patterns in Synthetic Data](https://arxiv.org/pdf/2403.03309.pdf) 
![Figure 1](/Figure1.jpg)
![Figure 2](/Figure2.jpg)


# What you need
## Hardware + Software
The script was run with Blender 4.0 with no add-ons, it can run with GPU or CPU but run much faster with a strong GPU.

## CGI Assets  
Objects Folder, HDRI background folder, and a folder of PBR materials. Example folders are supplied as: “HDRI_BackGround”, “PBRMaterials”,“Objects”, "NaturalImages". 
The script should run as is with these folders.
[Shapenet](https://shapenet.org/), [ObjaVerse](https://objaverse.allenai.org/)
Another input is  a folder of images from which the patterns will be extracted and injected to the scene. Images from  [apple/DMS](https://github.com/apple/ml-dms-dataset) dataset are good  images for this.



# How to use.

There are two ways to use this code one from within Blender and one from the command line.

To run from the command line, use the line:
blender DatasetGeneration.blend --background -noaudio -P  main.py

Or sh Run.sh

In this case, all the run parameters will be in main.py file.
To run from within blender, open DatasetGeneration.blend and run from main.py from within blender. 

Note for Blender4  the main.py you run from within Blender is stored inside the .blend file and is different from the main.py file in the code folder. 

If you change one, the other will not change. 
This can be very confusing. Blender python is very confusing in general.
Note that while running, Blender will be paralyzed and will not respond.
You will see the output images generated in the "/out_generated_data" dir (or whatever folder is in "MainOutDir=" in main.py)

*** Note all paths are set to the example folder supplied, running Run.sh or the main.py from the blender file should allow the script to run out of the box.

## Main run parameters 

The main running parameters are in the main.py in the Input parameters section in main.py.
This includes:

HDRI_BackGroundFolder = path to the HDRI background folder 

ObjectFolder = Path to the folder containing the object files (for example, shape net folder) 

OutFolder = path to output folder where generated dataset will be saved

pbr_folders  = path to a folder containing the PBRs textures subfolders

natural_image_dir = folder with natural images from which patterns will be extracted and will be used as UV maps.

Sample folders to all of these assets folder are supplied with the code and could be used as reference. 

In general, the code should run as is from the command line and from within Blender GUI.

For other parameters, see the documentation within the code.

## Rendering Parameters

This control rendering speed image quality and hardware use and are defined in section:"Rendering engine parameters" 
 
# Input folder structure:
See sample folders for example:

## Object Folder structure.
The object folder should contain the object in .obj or .gtlf format in the main folder or subfolder  of the .Obj  just using the Shapenet dataset as it should work. There are, in some cases, advantages in first converting the object to GTLF  format since its blender have some issues with obj materials.
But this is not essential.

## HDRI folder
This should just contain HDRI images for the background.

### PBR format
The PBR folder should contain subfolders, each containing PBR texture maps. 
Blender read texture maps by their name. Therefore untypical map names will be ignored. The texture maps names should contains one of the following: "OriginColor.","Roughness.","Normal.","Height.","Metallic.","AmbientOcclusion"r,"Specular.","Reflection","Glosinees".

The script: PBR_handling\StandartizePBR.py will automatically convert a set of PBR folders to standard PBR folders (mainly rename texture maps files to standard names)
## Natural image folder
Any images can be used here [apple/DMS](https://github.com/apple/ml-dms-dataset) give good results 

 

# Combining existing PBR texture maps to generate new PBRS
To increase the number of PBRs materials is possible to combine existing PBR materials. This is done by randomly mixing and combining existing PBR texture maps to generate new texture maps.
The script: PBR_Handling/CombinePBRMaterials.py. Take input pbr folders and mix them to generate new PBRS materials.


# Additional parameters 
In the “Input parameters” of "Main" DatasetGeneration  script (last section of the script)
"NumSetsToRender" determines how many different sets to render.



# Dealling with blender slowing done memory  issues and crashes
Given Blender’s tendency to crash, running this script alone can be problematic for large dataset creation. To avoid the need to restart the program every time Blender crashes, use the shell script Run.sh. This script will run the blender file in a loop, so it will restart every time Blender crashes (and continues from the last set). This can be run from shell/cmd/terminal: using: sh Run.sh. 
Also, in some case blender doesn't crash but  can start getting slower and slower, one way to solve it is to exit the blender once in  a while. Setting the parameter: use_priodical_exits
In the main.py to True, will cause Blender to exist every 10 sets. If this is run inside Run.sh blender will be immediately restarted and will start working cleanly. 



# Notes:
1) Running this script should paralyze Blender until the script is done, which can take a while.
2) The script refers to materials nodes and will only run as part of the blender file



# Sources for objects/HDRI/PBR materials
1) Objects were taken from [Shapenet](https://shapenet.org/)/[ObjaVerse](https://objaverse.allenai.org/). Blender has some issues with reading the  shapenet ".obj" files directly, so it might be easier (but not essential) to convert to GTLF format using the AddionalScripts\ConvertShapeNet.py script supplied. See [https://github.com/CesiumGS/obj2gltf](https://github.com/CesiumGS/obj2gltf).

3) HDRI backgrounds were downloaded from [PolyHaven](https://polyhaven.com/)
4) PBR materials textures were downloaded from [AmbientCg](https://ambientcg.com/) and [FreePBR](https://freepbr.com/) and [cgbookcases](https://www.cgbookcase.com/).
 and [TextureBox](https://texturebox.com/category). 
5) Natural images we used images from [apple/DMS](https://github.com/apple/ml-dms-dataset), any diverse image set likely to work


