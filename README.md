# GeoAI_QGIS Plugin
<table align="center">
    <p align = "center">
      <a href="https://www.linkedin.com/in/luisedpg/"><img alt="LuisGeo" src="https://img.shields.io/badge/AUTOR-Luis%20Eduardo%20Perez%20Graterol-brightgreen"></a>
      <a href="https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FluisCartoGeo%2FQGIS_Dashboard%2F"><img alt="Twitter" src="https://img.shields.io/twitter/url?label=TWITTER&style=social&url=https%3A%2F%2Ftwitter.com%2FLuiseperezg"></a>
      </P>
</table>

<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/fondoimagen.png" style="max-width:80%;"></center>
<h2><b>Repositorio del complemento GeoAI</b></h2><br>
<STRONG>GeoAI</STRONG> es un complemento en desarrollo para QGIS cuyo objetivo es permitir explotar con versatilidad las capacidades de modelos de Inteligencia Artifical (IA)
en el procesamiento de datos Geo-espaciales, comenzando con el modelo de segmentación de imagenes <strong>Segment Anything (SAM)</strong> desarrollado por <strong>MET</strong>A.<br><br>

<strong>Segment Anything</strong> es un modelo de inteligencia artificial pre-entrenado que permite generar mascaras sobre objetos reconocidos en imágenes para su resalte o extracción 
(Fuente [pagina del proyecto SAM] (https://segment-anything.com/), [repositorio github del proyecto SAM](https://github.com/facebookresearch/segment-anything)).<br>
<strong>Segment Anything</strong> produce máscaras de objetos de alta calidad a partir de entradas como puntos o recuadros, y puede utilizarse para generar máscaras para todos los objetos de una 
imagen. Se ha entrenado con un conjunto de datos de 11 millones de imágenes y 1.100 millones de máscaras, 
y ofrece un gran rendimiento en una gran variedad de tareas de segmentación Fuente [pagina del proyecto SAM](https://segment-anything.com/), 
[repositorio github del proyecto SAM](https://github.com/facebookresearch/segment-anything)).
<hr></hr>


### ¿Qué ventajas tiene GeoAI para aplicar el modelo SAM?
En esta primera versión del complemento he apostado por cuatro (04) aspectos fundamentales:
<center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/graf_caracte.png" width=350></center>
<br>
<ul>
    <li><strong>Funcionalidad</strong></li>
    <strong>GeoAI</strong> puede trabajar sobre imagenes georeferenciadas RGB de 8 bites (formato aceptado por el modelo) y tambien sobre imagenes unibanda y multibanda como las 
    imagenes de satelite y de drones, las cuales pueden poseer diversos formatos. Para ello el plugin realiza un proceso de transformación.<br>
    Luego de configuradas las imagenes el usuario puede segmentar las imagenes utilizando dos modulos:<br>
    1.- Segmentación de la imagen<br>
    Permite segementar toda la imagen, el usuario puede realizarlo utilizando la configuración por defecto o alterando los parametros avanzados. <strong>PRECAUCION</strong> la modificación de los parametros puede alterar los resultados y los tiempos de ejecución.<br>
    2.- Segmentación interactiva<br>
    Despliega un asistente mediante el cual es posible segmentar objetos de la imagen seleccionandolos en pantalla mediante puntos y/o areas (dibujando un rectangulo). Ademas cuenta con la opción de obtener un solo segmento por selección, múltiples segmentos o el de mayor superficie. Por otro lado, el usuario puede almacenar los segmentos en una nueva capa o una existente, incluso crear campos y guardar un atributo.<br>
    <li><strong>Versatilidad</strong></li>
    Las interfaces de usuario han sido diseñadas para facilitar su uso al mismo tiempo que se explotan las capacidades del modelo, brindando diversas configuraciones las cuales se disponibilizan cuando es oportuno.<br>
    <li><strong>Compatibilidad</strong></li>
    <center><img style="text-align:center" src="https://github.com/luisCartoGeo/GeoAI_Plugin/blob/main/logos.png" width=350></center>
    <strong>GeoAI</strong> ha sido probado en los sistemas operativos Windows10 y 11, en las versiones de QGIS 3.10, 3.16, 3.22 y la última LTR 3.28.<br>
    <li><strong>Facil instalación y portabilidad</strong></li>
    El archivo del complemento es ligero pesa menos de 2 megabytes, sus requisitos de instalación son los minimos requeridos para utilizar el modelo SAM, como son: instalar PyTorch, descargar los archivos de los modelos pre-entrenados (checkpoints).<br>
    Puede descargar el archivo zip del plugin de este repositorio y luego instalarlo en QGIS con la opción Instalar emdiante Zip.<br>
</ul>




