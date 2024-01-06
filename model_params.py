# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoAI, un complemento para QGIS

Complemento de QGIS cuyo fin es implementar el modelo de segmentación
de imagenes SAM desarrollado por META en datos geoespaciales, en la 
interfaz de QGIS.

                             -------------------
        Inicio               : 13 de Mayo del 2023
        Autores              : Luis Eduardo Perez 
        email                :         
        Desarrollador        : Luis Eduardo Perez https://www.linkedin.com/in/luisedpg/
 ***************************************************************************/
 Esta clase continene lo parametros obtenidos de la Precarga, es pasada a las otras herramientas
 Contiene las variables para generar la segmentacion por usuario y completa
 Tambien los parametros de la imagen necesarios para las transformaciones de coordenadas.
"""

class model_params:
    def __init__(self):
        self.activo = False
        self.sam= None
        self.predictor= None
        #parametros de la imagen
        self.geotransform=None
        self.filas=None
        self.columnas=None
        self.wkt=None
        self.src=None
        self.extenti=None
        self.arreglo=None
        self.nombre=None
