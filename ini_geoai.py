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
 Este script inicializa el complemento.
"""
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QMessageBox
from qgis.core import QgsProject, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsWkbTypes
from .dialog_precarga import dialog_precarga
from .dialog_digitalizacion import dialog_digitalizacion
from .dialog_segmentar_i import dialog_segmentar_i

#parametros del modelo
from .model_params import model_params
import os

class ini_geoai:
    def __init__(self, iface):
        self.iface = iface
        #parametros del modelo. Se inician y se pasan vacios
        self.params=model_params()

    def initGui(self):
        self.dir = os.path.dirname(__file__)
        rIcarga= os.path.join(self.dir,'icons//precarga.png')
        self.acprecarga = QAction(QIcon(rIcarga),'Precarga imagen y modelo', self.iface.mainWindow())
        self.acprecarga.setWhatsThis("---descripcion----")
        self.acprecarga.setStatusTip("---descripcion----")
        self.acprecarga.triggered.connect(self.precarga)
        #accion de digitalizacion
        rIdigi= os.path.join(self.dir,'icons//segnenti.png')
        self.acdigitalizacion = QAction(QIcon(rIdigi),'Segmentación interactiva', self.iface.mainWindow())
        self.acdigitalizacion.setWhatsThis("---descripcion----")
        self.acdigitalizacion.setStatusTip("---descripcion----")
        self.acdigitalizacion.triggered.connect(self.digitalizacion)
        #accion segmentar toda la imagen
        rIsegmi= os.path.join(self.dir,'icons//icoboton2.png')
        self.acsegment = QAction(QIcon(rIsegmi),'Segmentación total', self.iface.mainWindow())
        self.acsegment.setWhatsThis("---descripcion----")
        self.acsegment.setStatusTip("---descripcion----")
        self.acsegment.triggered.connect(self.segmenti)

        #añadir botones
        self.iface.addToolBarIcon(self.acprecarga)
        self.iface.addToolBarIcon(self.acdigitalizacion)
        self.iface.addToolBarIcon(self.acsegment)

        self.iface.addPluginToMenu('GeoAI',self.acprecarga)
        self.iface.addPluginToMenu('GeoAI',self.acdigitalizacion)
        self.iface.addPluginToMenu('GeoAI',self.acsegment)


    def unload(self):
        self.iface.removeToolBarIcon(self.acprecarga)
        self.iface.removeToolBarIcon(self.acdigitalizacion)
        self.iface.removeToolBarIcon(self.acsegment)

        self.iface.removePluginMenu(
                ('GeoAI'),
                self.acprecarga)
        self.iface.removePluginMenu(
                ('GeoAI'),
                self.acdigitalizacion)
        self.iface.removePluginMenu(
                ('GeoAI'),
                self.acsegment)

        del(self.acprecarga)
        del(self.acdigitalizacion)
        del(self.acsegment)

    def digitalizacion(self):
        listV=self.verificar_cargar_vector()
        if self.params.activo:
            self.dlg=dialog_digitalizacion(self.iface,listV,self.params)
            self.dlg.show()
        else:
            self.iface.messageBar().pushMessage('ERROR',\
            '<b>Primero debe Pre-Cargar el Modelo/Imagen</b>', level=0, duration=7)
            ms = QMessageBox()
            ms.setText("Primero debe Pre-Cargar el Modelo/Imagen. Ejecute Pre-Carga")
            ms.setIcon(QMessageBox.Information)
            ms.exec()

    def verificar_cargar_vector(self):
        pry=QgsProject.instance()
        listacapas= pry.mapLayers().values()  #Lista de capas
        #------Filtramos y guardamos solo las capas Vector--------
        listV=[] #Lista de capas Vector
        for i in listacapas:
            if i.type()==QgsMapLayer.VectorLayer or isinstance(i,QgsVectorLayer):
                tipoGeom=i.geometryType()
                if tipoGeom==QgsWkbTypes.PolygonGeometry:
                    listV.append(i)
        return listV

    def verificar_cargar_raster(self):
        pry=QgsProject.instance()
        listacapas= pry.mapLayers().values()  #Lista de capas
        #------Filtramos y guardamos solo las capas Raster--------
        self.listR=[] #Lista de capas Raster
        for i in listacapas:
            if  i.type()==QgsMapLayer.RasterLayer or isinstance(i,QgsRasterLayer):
                if i.dataProvider().description()=='GDAL data provider':
                    self.listR.append(i)
        return self.listR

    def precarga(self):
        self.verificar_cargar_raster()
        if len(self.listR)==0:
            self.iface.messageBar().pushMessage('ERROR',\
            '<b>No hay capas raster en el proyecto. Cargue las capas</b>', level=0, duration=7)
            ms = QMessageBox()
            ms.setText("No hay capas raster en el proyecto. Cargue las capas")
            ms.setIcon(QMessageBox.Information)
            ms.exec()
        else:
            self.dlg=dialog_precarga(self.iface,self.listR,self.params)
            self.dlg.show()
            
    def segmenti(self):
        if self.params.activo and self.params.nombre=="sam":
            self.dlg=dialog_segmentar_i(self.iface,self.params)
            self.dlg.show()
        else:
            if self.params.activo==False:
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>Primero debe Pre-Cargar el Modelo/Imagen</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("Primero debe Pre-Cargar el Modelo/Imagen. Ejecute Pre-Carga")
                ms.setIcon(QMessageBox.Information)
                ms.exec()
            elif self.params.nombre=="tinyhq":
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>El modelo HQ Ligero no se puede utilizar con esta opción</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("El modelo HQ Ligero no se puede utilizar con esta opción")
                ms.setIcon(QMessageBox.Information)
                ms.exec()
