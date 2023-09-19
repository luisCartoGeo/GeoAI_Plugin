# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoAI, un complemento para QGIS

Complemento de QGIS cuyo fin es implementar el modelo de segmentación
de imagenes SAM desarrollado por META en datos geoespaciales, en la 
interfaz de QGIS.

                             -------------------
        Inicio               : 02 de Septiembre del 2023
        Autores              : Luis Eduardo Perez 
        email                :         
        Desarrollador        : Luis Eduardo Perez https://www.linkedin.com/in/luisedpg/
 ***************************************************************************/
 Este script ejecuta el modelo de segmentaciond de toda la imagen
"""
import time
from qgis.PyQt import uic
from qgis import PyQt
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt import QtGui
from qgis.PyQt.QtGui import QIcon, QPixmap, QColor
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QFileDialog, QComboBox, QLineEdit
#librerias requeridas
import torch
import os
import numpy as np
#archivos temprales 
import tempfile
from shutil import rmtree
#utilidades y procesos
from .utils import *
try:
    import gdal
except:
    from osgeo import gdal
#importacion API de QGIS
from qgis.core import (Qgis,QgsMapLayer, QgsRasterLayer, QgsProject, QgsMapLayerType, QgsRectangle,
                      QgsGeometry, QgsWkbTypes, QgsVectorLayer,QgsCoordinateReferenceSystem,
                      QgsCoordinateTransform,QgsPointXY)
#modulos de sam
from .segment_anything.predictor import SamPredictor
from .segment_anything.build_sam import sam_model_registry
from .segment_anything.automatic_mask_generator import SamAutomaticMaskGenerator
    
DialogUi, DialogType=uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'segmenti.ui'))
    
class dialog_segmentar_i(DialogUi, DialogType):
    """Construction and management of the panel creation wizard """
    def __init__(self,iface,parametros):
        """Constructor.
        :param iface: viene de la clase de inicialización, permite interactura con la interfaz
        :tipo iface: QgisInterface,
        :param listaRaster: lista de capas raster ya cargadas en el mapa, viene de la inicializacion
        :tipo listRaster: list
        :param parametros: encapsula los parametros de configuracion del modelo/imagen, vienen vacios,
        seran calculados e inicializados por este dialogo
        :tipo parametros: clase sencilla con con cuatro atributos 
        """
        super().__init__()
        self.setupUi(self)
        self.iface=iface
        self.pry=QgsProject.instance()
        self.dir = os.path.dirname(__file__)
        #Instancia de clase que almacena los parametros del modelo e imagen
        self.param=parametros
        
        #imagen portada
        iconportada= QPixmap(os.path.join(self.dir,'icons','fondoSegmt2.png'))
        self.icon_portada.setPixmap(iconportada)

        #icono de la ventana
        rIdigi= os.path.join(self.dir,'icons//icoboton2.png')
        iconv=QIcon(rIdigi)
        self.setWindowIcon(iconv)
        self.cancelar.clicked.connect(self.cerrar)
        self.ejecutar.clicked.connect(self.procesar)
     
    def cerrar(self):
        self.close()
        
    def procesar(self):
        progressMessageBar = self.iface.messageBar().createMessage("El proceso de carga tomara varios minutos...")
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        time.sleep(1)
        self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
        progress.setValue(10)
        
        if self.defecto.isChecked():
            time.sleep(1)
            progressMessageBar.setText('Procesando segmentacion')
            #parametros
            predictor=self.param.predictor
            sam=self.param.sam
            wkt=self.param.wkt
            columnas=self.param.columnas
            filas=self.param.filas
            geotransform=self.param.geotransform
            epsg=self.param.src.authid()
            image=self.param.arreglo
            #print(' arreglo pasado en param',image)
            
            mask_generator = SamAutomaticMaskGenerator(sam)
            masks = mask_generator.generate(image)
            lmask=[i['segmentation'] for i in masks]
            #print(' lista de mascaras',lmask)
            #carpeta temporal
            if len(lmask)==0:
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>No se generaron segmentos</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("Error en el proceso. No se generaron segmentos")
                ms.setIcon(QMessageBox.Warning)
                ms.exec()
                return None
            tempdir=tempfile.TemporaryDirectory()
            ruta_out=tempdir.name
            listap=mask_to_imagen(lmask,ruta_out,'seg_i',columnas,filas,wkt,geotransform)
            time.sleep(1)
            progressMessageBar.setText('Procesando segmentos')
            progress.setValue(50)
            #vectorizando
            listcapas=[]
            if len(listap)>0:
                for i in listap:
                    if os.path.exists(i):
                        vector=vectorizar(i)
                        #print(' ruta capa vector',vector)
                        listcapas.append(vector)
            else:
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>Error al vectorizar segmentos</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("Error al vectorizar segmentos. No se genero la capa de salida")
                ms.setIcon(QMessageBox.Warning)
                ms.exec()
                return None
            resultado=crear_capa_salida(listcapas,epsg,multi=False)
            self.pry.addMapLayer(resultado)
            #proceso finalizado
            time.sleep(1)
            progress.setValue(100)
            self.iface.messageBar().clearWidgets()
            for i in listap:
                try:
                    rmtree(i)
                except:
                    pass
        else:
            time.sleep(1)
            progressMessageBar.setText('Procesando segmentacion')
            progress.setValue(20)
            #parametros
            predictor=self.param.predictor
            sam=self.param.sam
            wkt=self.param.wkt
            columnas=self.param.columnas
            filas=self.param.filas
            geotransform=self.param.geotransform
            epsg=self.param.src.authid()
            image=self.param.arreglo
            #nuevos parametros
            PointsPerSide=self.Points_per_side.value()
            PredIouThresh=self.Pred_iou_thresh.value()
            StabilityScoreThresh=self.Stability_score_thresh.value()
            CropNLayers=self.Crop_n_layers.value()
            CropNPointsDownscaleFactor=self.Crop_n_points_downscale_factor.value()
            #segmentacion
            mask_generator_2 = SamAutomaticMaskGenerator(
                model=sam,
                points_per_side=PointsPerSide,
                pred_iou_thresh=PredIouThresh,
                stability_score_thresh=StabilityScoreThresh,
                crop_n_layers=CropNLayers,
                crop_n_points_downscale_factor=CropNPointsDownscaleFactor,
            )
            masks2 = mask_generator_2.generate(image)
            lmask=[i['segmentation'] for i in masks2]
            #print(' lista de mascaras',lmask)
            #carpeta temporal
            if len(lmask)==0:
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>No se genraron segmentos</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("Error en el proceso. No se generaron segmentos")
                ms.setIcon(QMessageBox.Warning)
                ms.exec()
                return None
            tempdir=tempfile.TemporaryDirectory()
            ruta_out=tempdir.name
            listap=mask_to_imagen(lmask,ruta_out,'seg_i',columnas,filas,wkt,geotransform)
            time.sleep(1)
            progressMessageBar.setText('Procesando segmentos')
            progress.setValue(50)
            #vectorizando
            listcapas=[]
            if len(listap)>0:
                for i in listap:
                    if os.path.exists(i):
                        vector=vectorizar(i)
                        #print(' ruta capa vector',vector)
                        listcapas.append(vector)
            else:
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>Error al vectorizar segmentos</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("Error al vectorizar segmentos. No se genero la capa de salida")
                ms.setIcon(QMessageBox.Warning)
                ms.exec()
                return None
            resultado=crear_capa_salida(listcapas,epsg,multi=False)
            self.pry.addMapLayer(resultado)
            #proceso finalizado
            time.sleep(1)
            progress.setValue(100)
            self.iface.messageBar().clearWidgets()
            for i in listap:
                try:
                    rmtree(i)
                except:
                    pass
        

