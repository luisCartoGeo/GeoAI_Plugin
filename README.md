# GeoAI_QGIS Plugin
<table align="center">
    <p align = "center">
      <a href="https://www.linkedin.com/in/luisedpg/"><img alt="LuisGeo" src="https://img.shields.io/badge/AUTOR-Luis%20Eduardo%20Perez%20Graterol-brightgreen"></a>
      <a href="https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FluisCartoGeo%2FQGIS_Dashboard%2F"><img alt="Twitter" src="https://img.shields.io/twitter/url?label=TWITTER&style=social&url=https%3A%2F%2Ftwitter.com%2FLuiseperezg"></a>
      </P>
</table>

<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/fondoimagen.png" style="max-width:80%;"></center>
<h2><b>Repositorio del complemento GeoAI</b></h2><br>
<STRONG>GeoAI</STRONG> es un complemento en desarrollo para QGIS cuyo objetivo es permitir explotar con versatilidad las capacidades de los modelos de Inteligencia Artifical (IA)
en el procesamiento de datos Geo-espaciales, comenzando con el modelo de segmentación de imagenes <strong>Segment Anything (SAM)</strong> desarrollado por <strong>MET</strong>A.<br><br>

<strong>Segment Anything</strong> es un modelo de inteligencia artificial pre-entrenado que permite generar mascaras sobre objetos reconocidos en imágenes para su resalte o extracción 
(Fuente [pagina del proyecto SAM] (https://segment-anything.com/), [repositorio github del proyecto SAM](https://github.com/facebookresearch/segment-anything)).<br>
<strong>Segment Anything</strong> produce máscaras de objetos de alta calidad a partir de entradas como puntos o recuadros, y puede utilizarse para generar máscaras para todos los objetos de una 
imagen. Se ha entrenado con un conjunto de datos de 11 millones de imágenes y 1.100 millones de máscaras, 
y ofrece un gran rendimiento en una gran variedad de tareas de segmentación Fuente [pagina del proyecto SAM](https://segment-anything.com/), 
[repositorio github del proyecto SAM](https://github.com/facebookresearch/segment-anything)).
<hr></hr>

### Citas y aportes
Al utilizar el texto y/o codigo añadir a la cita:<br>
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8313393.svg)](https://doi.org/10.5281/zenodo.8313393)

Si deseas realizar una aporte a este desarrollo puedes enviarlo a la cuenta <strong>PayPal</strong>: luisepg3176@gmail.com<br>
Escribir en la nota tu nombre y <i>"Contribution to the development of the GeoAI plugin"</i><br>
<hr></hr>

### Licencia
El plugin esta bajo licencia: [Licencia pública general de GNU v3.0](https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/LICENSE.txt)

### ¿Qué ventajas tiene GeoAI para aplicar el modelo SAM?
Si bien, <strong>GeoAI</strong> es un complemento en desarrollo, en esta primera versión he apostado por cuatro (04) aspectos fundamentales:
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/graf_caracte.png" width=350></center>
<br>
<ul>
    <li><strong>Funcionalidad</strong></li>
    <strong>GeoAI</strong> puede trabajar sobre imagenes georeferenciadas RGB de 8 bytes (formato aceptado por el modelo) y tambien sobre imagenes unibanda y multibanda como las 
    imagenes de satelite y de drones, las cuales pueden poseer diversos formatos. Para ello el plugin realiza un proceso de transformación.<br>
    Luego de configuradas las imagenes el usuario puede segmentar las imagenes utilizando dos modulos:<br>
    1.- Segmentación de toda la imagen<br>
    Permite segmentar toda la imagen, el usuario puede realizarlo utilizando la configuración por defecto o alterando los parametros avanzados. <strong>PRECAUCION</strong> la modificación de los parametros puede alterar los resultados y los tiempos de ejecución.<br>
    2.- Segmentación interactiva<br>
    Esta es la herramienta más completa e intuitiva. Despliega un asistente mediante el cual es posible segmentar objetos de la imagen seleccionandolos en pantalla mediante puntos y/o areas (dibujando un rectangulo). Ademas cuenta con la opción de obtener un solo segmento por selección, múltiples segmentos o el de mayor superficie. Por otro lado, el usuario puede almacenar los segmentos en una nueva capa o una existente, incluso crear campos y guardar un atributo. Constituye una herramienta de digitalización avanzada.<br>
    <li><strong>Versatilidad</strong></li>
    Las interfaces de usuario han sido diseñadas para facilitar su uso al mismo tiempo que se explotan las capacidades del modelo, brindando diversas configuraciones las cuales se disponibilizan cuando es oportuno.<br>
    <li><strong>Compatibilidad</strong></li>
    <center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/logos.png" width=350></center><br>
    <strong>GeoAI</strong> ha sido probado en los sistemas operativos Windows10 y 11, en las versiones de QGIS 3.10, 3.16, 3.22 y la última LTR 3.28.<br>
    <li><strong>Facil instalación y portabilidad</strong></li>
    El archivo del complemento es ligero pesa menos de 2 megabytes, sus requisitos de instalación son los minimos requeridos para utilizar el modelo SAM, como son: instalar PyTorch, descargar los archivos de los modelos pre-entrenados (checkpoints).<br>
    Puede descargar el archivo zip del plugin de este repositorio y luego instalarlo en QGIS con la opción Instalar mediante Zip.<br>
</ul>

Sin embargo, hay aspectos mejorables, destacando:
<ul>
    <li>Completar la documentación</li>
    <li>Traducir la interfaz y documentación al ingles y otros idiomas</li>
    <li>Explorar en implementar las opciones de optimización que ofrece el modelo SAM, Python y PyQGIS</li>
    <li>Añadir mayores funcionalidades</il>
</ul>

## Tabla de contenido

- [Requerimientos](#Requerimientos)
    - [Requerimientos de instalación](#Requerimientos-de-instalación)
    - [Requerimientos de Hadware](#Requerimientos-de-Hadware)
    - [Recomendaciones para un mejor uso del plugin](#Recomendaciones-para-un-mejor-uso-del-plugin)
- [Instalación](#Instalación)
    - [Procedimiento para instalar PyTorch](#Procedimiento-para-instalar-PyTorch)
      - [Forma de instalación](#Forma_de_instalación)
      - [Procedimiento de instalación de PyTorch con PIP](#Procedimiento-de-instalación-de-PyTorch-con-PIP)
        - [1. Verifique el entorno de trabajo](#1.-Verifique-el-entorno-de-trabajo)
        - [2. Actualizar pip](#2.-Actualizar-pip)
        - [3. Seleccione la versión adecuada de PyTorch para su equipo](#3.-Seleccione-la-versión-adecuada-de-PyTorch-para-su-equipo)
    - [Corrigiendo una instalación previa](#Corrigiendo-una-instalación-previa)
    - [Procedimiento para descargar e instalar el plugin](#Procedimiento-para-descargar-e-instalar-el-plugin)
      - [Descarga del plugin](#Descarga-del-plugin)
      - [Instalación del plugin](#Instalación-del-plugin)
    - [Modelos pre entrenados (puntos de control o check points)](#Modelos-pre-entrenados-(puntos-de-control-o-check-points))
 - [<b>Tutorial rapido</b>](#Funcionalidad)
 - [Tutorial](#Funcionalidad)

# Requerimientos
## Requerimientos de instalación
<strong>GeoAI</strong> esta diseñado para minimizar los requsistos de instalación. Para utilizar el plugin solo debe cubrir dos requerimientos:<br>
<ol>
    <li>Instalar la versión <strong>adecuada</strong> de la libreria PyTorch</li>
    <li>Descargar y colocar en una directorio accesible los puntos de control (Check Points) del modelo SAM</li>
</ol>

## Requerimientos de Hadware
SAM es un modelo de redes neuronales NLP densamente entrenado (11 millones de imagenes), por lo cual, los puntos de control son archivos de +/- 2 Gb. Estos modelos presentan un alto consumo de memoria RAM y capacidad de procesamiento.<br>
Sin embargo, esto no restringe el uso en equipos de menores prestaciones, pero evidentemente el proceso tomara más tiempo. <br><br>
<strong>¿Cuales partes del proceso requieren mayor procesamiento, por lo tanto, demoran más?</strong><br>
<ol>
    <li>El proceso de pre-carga del modelo/imagen</li>
    <li>El proceso de segmentar toda la imagen, especialmente si se incrementa la densidad de puntos de muestreo</li>
</ol>
Como podra notar el proceso de pre-carga del modelo/imagen, es el proceso que he encontrado más demandante de recursos, para dar un ejemplo claro, describire cuanto demora el proceso para la misma imagen en los dos equipos en los que lo he probado:
<ol>
    <li><strong>Procesador</strong>: AMD Ryzen 3 3200U</li>
    <STRONG>Tarjeta de video</STRONG> Radeon Vega Mobile Fx 2.6 Gb<br>
    <strong>Memoria RAM</strong>: 8 Gb<br>
    <strong>Disco duro</strong>: aplicaciones SSD, <STRONG>Almacenamiento</strong>: HDD nota aqui se encuentran los puntos de control<br>
    <strong>Duración proceso de precarga modelo/imagen:</strong> +/- 20 minutos<br><br>
    <li><strong>Procesador</strong>: intel i5-12500H </li>
    <STRONG>Tarjeta de video</STRONG> Ge Force RTX3050TI<br>
    <strong>Memoria RAM</strong>: 16 Gb<br>
    <strong>Disco duro</strong> SSD nota aqui se encuentran los puntos de control<br>
     <strong>Duración proceso de precarga modelo/imagen:</strong> +/- 2 minutos<br>
</ol>

## Recomendaciones para un mejor uso del plugin
<ul>
    <li>Mantener lo más libre posible la RAM al realizar la pre-carga, cierre todas las otras aplicaciones</li>
    <li>Ubique los check points en el disco solido (SSD) si lo posee</li>
    <li>Deje trabajar el equipo mientras se realiza el proceso de pre-carga</li>
</ul>
 
# Instalación
## Procedimiento para instalar PyTorch
Realizar una adecuada instalación de PyTorch es el paso fundamental para utilizar el plugin sin mayores problemas. Para ello es necesario seleccionar la versión adecuada de PyTorch, a continuación se describe la instalación de PyTorch que he realizado en Windows10 y 11, para diferentes versiones de QGIS.<br>
<strong>Un error común</strong> instalar la última versión de PyTorch desde la pagina oficial, si bien esta versión puede ejecutar el modelo SAM correctamente, las librerias pre-instaladas en QGIS no necesariamente cubriran los requerimientos de esa versión de PyTorch, por ejemplo, la versión de Numpy pre-instalada<br>
### Forma de instalación
Realizaremos la instalación desde el shell de OSGEO utilizando pip. El shell de OSGEO es la ventana de comandos (CMD) instalada con QGIS mediante ella podemos realizar instalaciones de librerias y otras tareas<br>
<strong>¿Como acceder al shell de OSGEO? </strong><br>
Dirijase al icono de windows ubicado en la esquina inferior izquierda esto desplegara una lista de todos los programas, seleccione la carpeta que corresponde a su instalación de QGIS. Luego seleccione OSGeo4wShell como se muestra en la imagen<br>
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/shell.png" width=400></center><br>
Esto desplegara la ventana MS DOS donde introduciremos el codigo de instalación<br>

### Procedimiento de instalación de PyTorch con PIP
#### 1. Verifique el entorno de trabajo
Antes proceder a instalar cualquier libreria Python debemos verificar si se requiere configurar el entorno de trabajo. <br>
Las versiones antiguas de QGIS, incluyendo la 3.16 debemos introducir el siguiente codigo para que la instalación de la libreria se realice adecuadamente, sin embargo, para las nuevas versiones no es necesario. <br>

```
py3_env
```
Introduzca el siguiente codigo en el shell, independiente el resultado que devuelva el shell prosiga con los siguientes pasos

#### 2. Actualizar pip
```
python -m pip install -U pip
```
Si esta en una versión muy antigua de QGIS y el codigo anterior arroja error utilice este<br>
```
python -m pip install --upgrade pip
```
#### 3. Seleccione la versión adecuada de PyTorch para su equipo
Las especificaciones del modelo SAM señalan que se requiere como minimo python>=3.8, pytorch>=1.7 y torchvision>=0.8. <br>
En teoria la versión de Python limita la versión QGIS donde podriamos instalar y ejecutar el modelo, sin embargo, me ha funcionado bien en QGIS 3.10 cuya versión es Python 3.7. Por lo tanto, cualquier versión de QGIS igual o superior a la 3.10 es posible utilizar el plugin.<br>

La instalación de PyTorch dependera de las especificaciones de tu equipo:<br>

1.- Procesador Intel con tarjeta gráfica Nvidia</li>
    Para un uso adecuado de la GPU deberas verificar la versión de tu driver Nvidia:<br><br>
a.- Para utilizar CUDA 10.2, la versión del Driver Nvidia debe ser >= 441.22<br>
En ese caso introduce este código<br>
    
```                                   
pip3 install torch==1.8.1+cu102 torchvision==0.9.1+cu102 torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```

b.-  Para utilizar CUDA 11.1, la versión del Driver Nvidia debe ser >= 456.38<br>
En ese caso introduce este código<br>
        
``` 
pip3 install torch==1.8.1+cu111 torchvision==0.9.1+cu111 torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```

2.- Otros procesadores y tarjetas de video<br>
Utiliza el siguiente codigo, en este caso utilizaras el modelo SAM solo con la opción CPU (no te preocupes hasta ahora solo la he utilizado de esta forma)<br>
    
``` 
pip3 install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```
    
3.- Verifica la instalación de PyTorch
Introduce este codigo debe devolverte información de la liberia instalada<br>
    
    ``` 
    pip3 show torch
    ``` 
    
Otra opción, abre QGIS activa la consola de Python ejecuta import torch si no devuelve nada, esta instalada<br>

### Corrigiendo una instalación previa
Si realizaste una instalación de PyTorch que no te permite ejecutar el plugin deberas removerla y reemplazarla por las recomendadas aqui.<br> 
Puedes removerla utilizando pip, asegurate de incluir todo lo instalado previamente, entre ello   torchvision y torchaudio<br>
Para desinstalar las versiones aqui recomendadas repite desde el paso 1 e introduce el siguiente codigo<br>
``` 
pip3 uninstall torch torchvision torchaudio
``` 
Deberas aceptar cuando te pregunte si estas seguro de desinstalar<br>

## Procedimiento para descargar e instalar el plugin
### Descarga del plugin
El primer paso es descargar el complemento, el proceso es muy sencillo haces clic en el botón de color verde con el texto <strong>CODE</strong>, despliega un menú y seleccionas <strong>Download ZIP</strong> esto descargara un archivo zip el cual puedes utilizar directamente para instalar en QGIS. También puedes descargar el complemento desde la opción de Versión ubicado en la parte inferior derecha, descarga la última versión publicada.
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/instal1.png" width=500></center>

### Instalación del plugin
Luego de descargado el Zip que contiene el plugin, puede activar el programa QGIS y realizar los siguientes pasos:
<ol>
    <li>Seleccione el menú complementos, luego "Administrar e instalar complementos"</li>
    <li>En la ventana que se despliega seleccione la etiqueta "Instalar a partir de Zip" ubicada en el panel de la izquierda</li>
    <li>Seleccione el botón a la derecha con tres puntos, le permitira ubicar el archivo Zip en su coputador, luego clic sobre el botón "Instalar complemento"</li>
    <center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/instal2.png" width=500></center>
    <li>Luego de instalado es recomendable reiniciar el programa QGIS, active la caja de dialogo Complementos, seleccione la etiqueta Instalado, encontrara el plugin GeoAI, activelo</li>
</ol>

## Modelos pre entrenados (puntos de control o check points)
Para poder ejecutar SAM debemos descargar los puntos de control, los cuales son requeridos durante el proceso de pre-carga del modelo/imagen<br>
Puedes descargar los puntos de control disponibles en los siguientes enlaces:
<ul>
    <li>Generalmente el más utilizado ```vit_h```: [modelo ViT-H SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) </li>
    <li>vit_l: [Modelo ViT-L SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth) </li>
    <li>vit_b: [Modelo ViT-B SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth) </li>
</ul>


