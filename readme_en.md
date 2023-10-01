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
