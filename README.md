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
    - [Procedimiento para instalar PyTorch](Funcionalidad)
    - [Procedimiento para descargar e instalar el plugin](#Procedimiento-para-descargar-e-instalar-el-plugin)
      - [Descarga del plugin](#Descarga-del-plugin)
      - [Instalación del plugin](#Instalación-del-plugin)
    - [Modelos pre-entrenados (check points)]()
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
