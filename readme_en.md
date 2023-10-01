# GeoAI_QGIS Plugin
<table align="center">
    <p align = "center">
      <a href="https://www.linkedin.com/in/luisedpg/"><img alt="LuisGeo" src="https://img.shields.io/badge/AUTOR-Luis%20Eduardo%20Perez%20Graterol-brightgreen"></a>
      <a href="https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FluisCartoGeo%2FQGIS_Dashboard%2F"><img alt="Twitter" src="https://img.shields.io/twitter/url?label=TWITTER&style=social&url=https%3A%2F%2Ftwitter.com%2FLuiseperezg"></a>
      </P>
</table>

Leer en Español: https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/README.md<br>

<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/fondoimagen.png" style="max-width:80%;"></center>
<h2><b>GeoAI Plug-in Repository</b></h2><br>
<STRONG>GeoAI</STRONG> is an plug_in under development for QGIS whose objective is to allow to exploit with versatility the capabilities of the Artifical Intelligence (AI) models
in geospatial data processing, starting with the <strong>Segment Anything image segmentation model (SAM) )</strong> developed by <strong>META)</strong>.<br><br>

<strong>Segment Anything</strong> is a pre-trained artificial intelligence model that allows to generate masks on recognized objects in images for highlighting or extraction.
(Source [pagina del proyecto SAM](https://segment-anything.com/), [github SAM project](https://github.com/facebookresearch/segment-anything)).<br>
<strong>Segment Anything</strong>  produces high-quality object masks from inputs such as dots or boxes, and can be used to generate masks for all objects in an image. 
It has been trained on a dataset of 11 million images and 1.1 billion masks, and offers great performance on a wide variety of segmentation tasks 
Source [SAM project page](https://segment-anything.com/), [github SAM project](https://github.com/facebookresearch/segment-anything)).
<hr></hr>

### Quotes and contributions
When using the text and/or code add to the quote:<br>
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8313393.svg)](https://doi.org/10.5281/zenodo.8313393)

If you want to make a contribution to this development you can send it to <strong>PayPal</strong> account: luisepg3176@gmail.com<br>
Write in the note your name and <i>"Contribution to the development of the GeoAI plugin"</i><br>
<hr></hr>

### License
The plugin is licensed under: [GNU General Public License v3.0](https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/LICENSE.txt)

### What are the advantages of GeoAI to apply the SAM model?
Although, <strong>GeoAI</strong> is a plugin under development, in this first version I have bet on four (04) fundamental aspects:
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/graf_caracte.png" width=350></center>
<br>
<ul>
    <li><strong>Functionality</strong></li>
    <strong>GeoAI</strong>It can work on 8-byte RGB georeferenced images (format accepted by the model) and also on uniband and multiband images such as satellite and drone images, 
     which can have different formats. For this purpose the plugin performs a transformation process.<br>
    After configuring the images the user can segment the images using two modules:<br>
    1.- Segmentation of the whole image<br>
    It allows to segment the whole image, the user can do it using the default settings or by altering the advanced parameters. <strong>CAUTION</strong> modifying the parameters may alter the results and execution times.<br>
    2.-  Interactive segmentation<br>
    This is the most complete and intuitive tool. It displays a wizard through which it is possible to segment objects in the image by selecting them on the screen using points and/or areas (drawing a rectangle). It also has the option to obtain a single segment per selection, multiple segments or the one with the largest area. On the other hand, the user can store the segments in a new layer or an existing one, even create fields and save an attribute. It is an advanced digitizing tool.<br>
    <li><strong>Versatility</strong></li>
    The user interfaces have been designed for ease of use while exploiting the capabilities of the model, providing various configurations which are made available when appropriate.<br>
    <li><strong>Compatibility</strong></li>
    <center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/logos.png" width=350></center><br>
    <strong>GeoAI</strong> has been tested on Windows 10 and 11 operating systems, QGIS versions 3.10, 3.16, 3.22 and the latest LTR 3.28.<br>
    <li><strong>Easy installation and portability</strong></li>
    The plug-in file is lightweight, weighing less than 2 megabytes, and its installation requirements are the minimum required to use the SAM model, such as: install PyTorch, download the pre-trained model files (checkpoints).<br>
    You can download the plugin zip file from this repository and then install it in QGIS with the Install via Zip option..<br>
</ul>

However, there are aspects that could be improved, highlighting:
<ul>
    <li>Complete the documentation</li>
    <li>Translating the interface and documentation into English and other languages</li>
    <li>Explore in implementing the optimization options offered by the SAM model, Python and PyQGIS</li>
    <li>Add more functionalities</il>
</ul>

## Table of contents

- [Requirements](#Requirements)
    - [Installation requirements](#Installation-requirements)
    - [Hardware requirements](#Hardware-requirements)
    - [Recommendations for better use of the plugin](#Recommendations-for-Better-use-of-the-plugin)
- [Installation](#Installation)
    - [PyTorch installation procedure](#PyTorch-installation-procedure)
      - [Installation method](#Installation-method)
      - [PyTorch installation procedure using PIP](#PyTorch-installation-procedure-using-PIP)
        - [1. Check the working environment](#1.-Check-the-working-environment)
        - [2. Update pip](#2.-Update-pip)
        - [3. Select the appropriate version of PyTorch for your computer](#3.-Select-the-appropriate-version-of-PyTorch-for-your-computer)
    - [Correcting a previous installation](#Correcting-a-previous-installation)
    - [Procedure to download and install the plugin](#Procedure-to-download-and-install-the-plugin)
      - [Download plugin](#Download-plugin)
      - [Plugin installation](#Plugin-installation)
    - [Pre-trained models (check points)](#Pre-trained-models-(check-points))
 - [<b>Quick Tutorial</b>](#Quick-Tutorial)
    - [Interactive Segmentation](#Interactiv-Segmentation)
    - [Row and plant extraction and counting](#Row-and-plant-extraction-and-counting)
    - [Extraction of cultivation and irrigation areas](#Extraction-of-cultivation-and-irrigation-areas)
- [Tutorial](#Tutorial)
  
# Requirements
## Installation requirements
<strong>GeoAI</strong> is designed to minimize installation requirements. To use the plugin you only need to meet two requirements:<br>
<ol>
    <li>Install the <strong>appropriate</strong> version of the PyTorch library</li>
    <li>Download and place in an accessible directory the Check Points of the SAM model.</li>
</ol>

## Requerimientos de Hardware
SAM is a densely trained NLP neural network model (11 million images), so the control points are +/- 2 Gb files. These models have a high consumption of RAM memory and processing capacity..<br>
However, this does not restrict the use in lower performance equipment, but the process will obviously take longer. <br><br>
<strong>Which parts of the process require more processing and therefore take longer?</strong><br>
<ol>
    <li>The model/image pre-loading process</li>
    <li>The process of segmenting the entire image, especially if the density of sampling points is increased.</li>
</ol>
As you may notice the process of pre-loading the model/image, is the process that I have found most demanding of resources, to give a clear example, I will describe how long the process takes for the same image on the two computers on which I have tested it:
<ol>
    <li><strong>Processor</strong>: AMD Ryzen 3 3200U</li>
    <STRONG>Video card</STRONG> Radeon Vega Mobile Fx 2.6 Gb<br>
    <strong>RAM</strong>: 8 Gb<br>
    <strong>Hard disk</strong>: applications SSD, <STRONG>Storage</strong>: HDD here are the checkpoints<br>
    <strong>Duration of preloading process model/image:</strong> +/- 20 minutes<br><br>
    <li><strong>Processor</strong>: intel i5-12500H </li>
    <STRONG>Video card</STRONG> Ge Force RTX3050TI<br>
    <strong>RAM</strong>: 16 Gb<br>
    <strong>Hard disk</strong> SSD here are the checkpoints<br>
     <strong>Duration of preloading process model/image:</strong> +/- 2 minutes<br>
</ol>
## Recommendations for a better use of the plugin
<ul>
    <li>Keep the RAM as free as possible when preloading, close all other applications.</li>
    <li>Place the check points on the solid state drive (SSD) if you have one.</li>
    <li>Let the computer work while the preloading process is being performed.</li>
</ul>

# Installation
## PyTorch installation procedure
Performing a proper installation of PyTorch is the fundamental step to use the plugin without major problems. To do this it is necessary to select the appropriate version of PyTorch, the following describes the PyTorch installation that I have done on Windows10 and 11, for different versions of QGIS.<br>
<strong>A common mistake</strong> install the latest version of PyTorch from the official website, although this version can run the SAM model correctly, the pre-installed libraries in QGIS will not necessarily cover the requirements of that version of PyTorch, for example, the pre-installed version of Numpy.<br>

### Installation method
We will perform the installation from the OSGEO shell using pip. The OSGEO shell is the command window (CMD) installed with QGIS through it we can perform library installations and other tasks.<br>
<strong>How to access the OSGEO shell? </strong><br>
Go to the windows icon located in the lower left corner this will display a list of all programs, select the folder that corresponds to your QGIS installation. Then select OSGeo4wShell as shown in the image.<br>
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/shell.png" width=800></center><br>
This will display the MS DOS window where we will enter the installation code.<br>

### PyTorch installation procedure using PIP
#### 1. Check the working environment
Before proceeding to install any Python library we must verify if it is required to configure the working environment. <br>
Older versions of QGIS, including 3.16, we must enter the following code for the installation of the library to be performed properly, however, for newer versions it is not necessary. <br>

```
py3_env
```
Enter the following code in the shell, independently of the result returned by the shell, proceed with the following steps
#### 2. Update pip
```
python -m pip install -U pip
```
If you are on a very old version of QGIS and the above code throws error use this one<br>
```
python -m pip install --upgrade pip
```

#### 3. Select the appropriate version of PyTorch for your computer
The SAM model specifications state that a minimum of python>=3.8, pytorch>=1.7 and torchvision>=0.8 is required. <br>
In theory the Python version limits the QGIS version where we could install and run the model, however, it has worked fine in QGIS 3.10 whose version is Python 3.7. Therefore, any QGIS version equal or superior to 3.10 is possible to use the plugin.<br>

The installation of PyTorch will depend on the specifications of your computer.:<br>

1.- Intel processor with Nvidia graphics card</li>
    For proper GPU usage you should check your Nvidia driver version:<br><br>
a.- To use CUDA 10.2, Nvidia Driver version must be >= 441.22<br>
In that case enter this code<br>
    
```                                   
pip3 install torch==1.8.1+cu102 torchvision==0.9.1+cu102 torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```
b.-  In order to use CUDA 11.1, the Nvidia Driver version must be >= 456.38<br>
In that case enter this code<br>
        
``` 
pip3 install torch==1.8.1+cu111 torchvision==0.9.1+cu111 torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```

2.- Other processors and video cards<br>
Use the following code, in this case you will use the SAM model only with the CPU option (don't worry so far I have only used it this way)<br>
    
``` 
pip3 install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```
    
3.- Verify the installation of PyTorch
Enter this code and it should return information about the installed library.<br>
    
    ``` 
    pip3 show torch
    ``` 
    
Another option, open QGIS activate the Python console run import torch if nothing is returned, it is installed.<br>

### Correcting a previous installation
If you have a PyTorch installation that does not allow you to run the plugin you should remove it and replace it with the ones recommended here.<br> 
You can remove it using pip, be sure to include everything previously installed, including torchvision and torchaudio.<br>
To uninstall the versions recommended here, repeat from step 1 and enter the following code<br>
``` 
pip3 uninstall torch torchvision torchaudio
``` 
You must accept when it asks you if you are sure to uninstall<br>

## Procedure to download and install the plugin
### Download plugin
The first step is to download the plug-in, the process is very simple click on the green button with the text <strong>CODE</strong>, drop down a menu and select <strong>Download ZIP</strong>  this will download a zip file which you can use directly to install in QGIS. You can also download the add-in from the Version option located at the bottom right, download the latest published version.<br>
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/instal1.png" width=500></center>

### Plugin installation
After downloading the Zip file containing the plugin, you can activate the QGIS program and perform the following steps:
<ol>
    <li>Select the Plug-ins menu, then "Manage and install plug-ins".</li>
    <li>In the window that appears, select the "Install from Zip" tab located in the left pane.</li>
    <li>Select the button on the right with three dots, it will allow you to locate the Zip file in your computer, then click on the button "Install plug-in".</li>
    <center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/instal2.png" width=500></center>
    <li>After installation it is recommended to restart the QGIS program, activate the Plugins dialog box, select the Installed tab, you will find the GeoAI plugin, activate it.</li>
</ol>

## Pre-trained models (check points)
In order to run SAM we must download the checkpoints, which are required during the model/image preloading process.<br>
You can download the available checkpoints by clicking on the following links:<br><br>

1. Generally the most used vit_h: ([modelo ViT-H SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth))<br>
2. vit_l: [Modelo ViT-L SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth)<br>
3. vit_b: [Modelo ViT-B SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth)<br>
# Quick Tutorial
## Interactive Segmentation
   - [Link Video](https://youtu.be/TXPBrG-KUzg?si=TuzZuP90piUy0eot)<br>

## Row and plant extraction and counting
   - [Link Video](https://www.youtube.com/watch?v=AnQiqTYvdcA)<br>

## Extraction of cultivation and irrigation areas
 - [Link Video](https://youtu.be/h-ijSHcaP_4)<br>
