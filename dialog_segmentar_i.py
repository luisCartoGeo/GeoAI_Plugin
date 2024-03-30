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
from qgis.PyQt.QtWidgets import QFileDialog, QComboBox, QLineEdit,QProgressBar, QMessageBox
#librerias requeridas
import torch
import os, gc
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

#modulos de sam_f
from .segment_fast import *
from .segment_fast.predictor_f import SamPredictor_f
from .segment_fast.build_sam_f import sam_model_registry_f
from .segment_fast.automatic_mask_generator_f import SamAutomaticMaskGenerator_f

DialogUi, DialogType=uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'segmenti.ui'))
    
class dialog_segmentar_i(DialogUi, DialogType):
    """Construction and management of the panel creation wizard """
    def __init__(self,iface,listaRaster):
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
        
        #imagen portada
        iconportada= QPixmap(os.path.join(self.dir,'fondorojo.png'))
        self.icon_portada.setPixmap(iconportada)
        self.icon_portada_2.setPixmap(iconportada)
        #icono de la ventana
        rIdigi= os.path.join(self.dir,'icons//icoboton2.png')
        iconv=QIcon(rIdigi)
        self.setWindowIcon(iconv)
        
        #lista de capas
        self.listaRaster=listaRaster
        self.listV=self.verificar_vector_puntos()#captamos capas de puntos
        self.cargarListaV()
        
        #tiny checkpoint
        self.modeltiny= os.path.join(self.dir,'sam_hq_vit_tiny.pth')
        #inicializamos con tiny marcado y opciones por defecto
        self.inicializar()
        self.tinyhqop.stateChanged.connect(self.gestion_cambio)
        
        #cambio de estado opciones avanzadas
        self.defecto.stateChanged.connect(self.cambio_defecto)
        
        #listado de comboBox de Bandas
        self.lbandas=(self.bandR,self.bandG,self.bandB)
        
        #Configuracion inicial
        self.paginador.setCurrentIndex(1)
        
        #EVENTOS DEL PROYECTO
        self.pry.layersWillBeRemoved.connect(self.capaRemovida)
        self.pry.layersAdded.connect(self.capaAdicionada)
        
        #EVENTO AL CAMBIAR LA CAPA
        self.listImagen.currentTextChanged.connect(self.cambioCapa)
        #INICIALZAR LISTAS RASTER
        self.cargarLista(self.listaRaster)
        #EVENTO CAMBIAR PAGINA
        self.opAvanzadas.clicked.connect(self.cambiarPagina)
        iconavan=QIcon(os.path.join(self.dir,'icons','opAvanzadas.png'))
        self.opAvanzadas.setIcon(iconavan)
        self.opBasicas.clicked.connect(self.retornar)
        iconbasicas=QIcon(os.path.join(self.dir,'icons','opBasicas.png'))
        self.opBasicas.setIcon(iconbasicas)
        #----------------
        #EVENTO SELECCION MODELO
        self.brmodelo.clicked.connect(self.archivo_modelo)

        self.cancelar.clicked.connect(self.cerrar)
        self.ejecutar.clicked.connect(self.procesar)
        
    def verificar_vector_puntos(self):
        listacapas= self.pry.mapLayers().values()  #Lista de capas
        #------Filtramos y guardamos solo las capas Vector--------
        listV=[] #Lista de capas Vector
        for i in listacapas:
            if i.type()==QgsMapLayer.VectorLayer or isinstance(i,QgsVectorLayer):
                tipoGeom=i.geometryType()
                if tipoGeom==QgsWkbTypes.PointGeometry:
                    listV.append(i)
        return listV
        
    #INICIALZAR LISTAS VECTOR
    def cargarListaV(self):
        if len(self.listV)>0:
            for i in self.listV:
                self.listVector.addItem(i.name(),i)
    
    def liberarMemoria(self):
        torch.cuda.empty_cache()
        gc.collect()
            
    def cargar_imagen(self,capa):
    #metodo devulev la imagen como arreglo apto para el modelo
    #y un tuple con el geotrasnform, numero de filas, columnas y georeferencia
    #en formato wkt
        if isinstance(capa,QgsRasterLayer):
            nbandas=capa.bandCount() 
#            print(nbandas)
            capag=gdal.Open(capa.source())
        elif type(capa)==str:
            capag=gdal.Open(capa.source())
            nbandas=capag.RasterCount
        #captamos los parametros de la imagen
        geotransform=capag.GetGeoTransform()
        bimag = capag.GetRasterBand(1)
        arr=bimag.ReadAsArray()
        filas=arr.shape[0]
        columnas=arr.shape[1]
        wkt = capag.GetProjection()
        #valor minimo y maximo bandas seleccionadas
        l=[int(i.currentText()) for i in self.lbandas] #lista de bandas (enteros)
        #print('l', l)
        minmax=minimo_maximo_bs(capa,l)
        del(arr)
        del(bimag)
        #creamos el arreglo de salida
        lbands= []
#        print(' numero de bandas',nbandas)
        #if nbandas>1:
        if nbandas>1:
            for n in l:
                #print('banda ',n)
                b=capag.GetRasterBand(n)
                ba=b.ReadAsArray()
                #print(' tipo de imagen',ba.dtype)
                if ba.dtype!='uint8':
#                    print('entro agtransformacion de la imagen')
                    if minmax[1]<2:
                        bac=ba*10000
                        min=minmax[0]*10000
                        max=minmax[1]*10000
                        ran=max-min
                    else:
                        bac=ba
                        min=minmax[0]
                        max=minmax[1]
                        ran=max-min
                    #escalamos de 0 a 255
                    av = 255 / ran
                    b = 255 - av * max
                    lf=lambda x: av*x+b
                    result = lf(bac).astype(np.uint8)
#                    print(' arreglo f' ,result)
#                    print(' minimo y maximo' ,result.min(),result.max())
                    lbands.append(result)
                else:
                    #print(' la imagen es uint8 carga directa')
                    lbands.append(ba)
        else:
            b=capag.GetRasterBand(1)
            ba=b.ReadAsArray()
            if ba.dtype!='uint8':
                if minmax[1]<2:
                    bac=ba*10000
                    min=minmax[0]*10000
                    max=minmax[1]*10000
                    ran=max-min
                else:
                    bac=ba
                    min=minmax[0]
                    max=minmax[1]
                    ran=max-min
                #escalamos de 0 a 255
                av = 255 / ran
                b = 255 - av * max
                lf=lambda x: av*x+b
                result = lf(bac).astype(np.uint8)
                #convertimos a int
                lbands.append(result)
                lbands.append(result.copy())
                lbands.append(result.copy())
            else:
                lbands.append(ba)
                lbands.append(ba.copy())
                lbands.append(ba.copy())
        #else:
        capag=None
        return (np.dstack(lbands),(geotransform,filas,columnas,wkt))
    
    def archivo_modelo(self):
        d=QFileDialog.getOpenFileName(None,"Ruta al modelo, generalmente sam_vit_h_4b8939.pth",filter='*.pth')
        if os.path.exists(d[0]):
            self.ruta_modelo=d[0] #CONSIDERAR COLOCAR UNA VERIFICACION DE NOMBRE Y TAMAÑO DE ARCHIVO
            self.ruta_file.setText(self.ruta_modelo)
        else:
            self.ruta_file.setText('Directorio incorrecto o sin acceso, seleccione otra')
            self.iface.messageBar().pushMessage('ERROR',\
            '<b>Directorio incorrecto o sin acceso, seleccione otra</b>', level=0, duration=7)
    
    #INICIALZAR LISTAS RASTER
    def cargarLista(self,lista):
        for i in lista:
            if  i.type()==QgsMapLayer.RasterLayer or isinstance(i,QgsRasterLayer):
                if i.dataProvider().description()=='GDAL data provider':
                    self.listImagen.addItem(i.name(),i)
       
    #La capa fue removida del mapa
    def capaRemovida(self,ids):
        items=[]
        for i in range(self.listImagen.count()):
            capa=self.listImagen.itemData(i)
            if type(capa)==QgsRasterLayer:
                if capa.dataProvider().description()=='GDAL data provider':
                    items.append(capa)
        for i in ids:
            for j in items:
                if i==j.id():
                    indice=self.listImagen.findText(j.name())
                    if indice>-1:
                        cap=self.listImagen.itemData(indice)
                        #print(type(cap))
                        if type(cap)==QgsRasterLayer:    
                            self.listImagen.removeItem(indice)
        if self.listImagen.count()==0:
            self.cerrar()
        for i in ids:
            for j in self.listV:#lista de capas interna
                id=j.id()
                if i==id:
                    self.listV.remove(j)
                    ubi=self.listVector.findData(j)
                    if ubi!=-1:
                        self.listVector.removeItem(ubi)
                        
    #Se adiciono una nueva capa    
    def capaAdicionada(self,lista):
        for i in lista:
            if i.type()==QgsMapLayer.RasterLayer or isinstance(i,QgsRasterLayer):
                if i.dataProvider().description()=='GDAL data provider':
                    self.listImagen.addItem(i.name(),i)
        for i in lista:
            if i.type()==QgsMapLayer.VectorLayer or isinstance(i,QgsVectorLayer):
                if i.geometryType()== QgsWkbTypes.PointGeometry:
                    self.listVector.addItem(i.name(),i)
                    self.listV.append(i)
    
    def cambioCapa(self):
        imagen=self.listImagen.currentData()
        if type(imagen)==QgsRasterLayer:
            nbandas=imagen.bandCount()
            if nbandas==1:
                for i in self.lbandas:
                    i.setEnabled(False)
            else:
                for i in self.lbandas:
                    i.clear()
                    i.setEnabled(True)
                    i.addItems([str(i) for i in range(1,nbandas+1)])
     
    def cerrar(self):
        self.pry.layersWillBeRemoved.disconnect(self.capaRemovida)
        self.pry.layersAdded.disconnect(self.capaAdicionada)
        self.close()
        
    def cambiarPagina(self,e):
        self.paginador.setCurrentIndex(0)
    
    def retornar(self,e):
        self.paginador.setCurrentIndex(1)
        
    def procesar(self):
        self.liberarMemoria()
        progressMessageBar = self.iface.messageBar().createMessage("El proceso de carga tomara varios minutos...")
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        time.sleep(1)
        self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
        progress.setValue(10)
        #CARGA DE IMAGEN
        ruta_modelo=self.ruta_file.text()
        if not os.path.exists(ruta_modelo):
            d= QFileDialog.getOpenFileName(None,"Ruta al modelo, generalmente sam_vit_h_4b8939.pth")
            if os.path.exists(d):
                ruta_modelo=d
            else:
                self.cerrar()
                self.iface.messageBar().pushMessage('ERROR',\
                '<b>Error en la ruta del modelo</b>', level=0, duration=7)
                return None
        #verificando correcta asignacion del nombre del modelo
        if self.tinyhqop.isChecked()==False:
            nf=os.path.basename(ruta_modelo)
            if nf=='sam_vit_h_4b8939.pth':
                nombre_modelo='vit_h'
            elif nf=='sam_vit_l_0b3195.pth':
                nombre_modelo='vit_l'
            elif nf=='sam_vit_b_01ec64.pth':
                nombre_modelo='vit_b'
            else:
                nombre_modelo=self.nmodelo.currentText()
            nombre_modelo=self.nmodelo.currentText()
        #--------------------------------------------------
        imagen=self.listImagen.currentData()
        #sistema de coordenadas de la imagen
        src=imagen.crs()
        extension=imagen.extent()
        
        device=self.device.currentText()
        
        #captar primeras bandas con gdal y convertir en array
        resultado=self.cargar_imagen(imagen)
        arreglo=resultado[0]
        
        self.cerrar()    #cerramos el dialogo para evitar que el usuario ejecute de nuevo por equivocacion
        #Configurar device
        device=self.device.currentText()
        if device=='CPU':
            device='cpu'
        else:
            if torch.cuda.is_available():
                device='cuda'
            else:
                device='cpu'
                
        if self.tinyhqop.isChecked():
            sam = sam_model_registry_f['vit_tiny'](checkpoint=self.modeltiny)
            sam.to(device=device)
#            sam.eval()
        else:
            #inicializar modelo
            sam = sam_model_registry[nombre_modelo](checkpoint=ruta_modelo)
            sam.to(device=device)
        #Parametros
        geotransform=resultado[1][0]
        filas=resultado[1][1]
        columnas=resultado[1][2]
        wkt=resultado[1][3]
        epsg=src.authid()
        image=arreglo
       
        #INICIO PROCESAMIENTO
        if self.defecto.isChecked():
            time.sleep(1)
            progressMessageBar.setText('Procesando segmentacion')
            progress.setValue(20)
            #---------------------------
            if self.tinyhqop.isChecked():
                mask_generator = SamAutomaticMaskGenerator_f(sam)
                masks =  mask_generator.generate(image)
            else:
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
                time.sleep(1)
                progress.setValue(100)
                self.iface.messageBar().clearWidgets()
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
                '<b>No se genraron segmentos</b>', level=0, duration=7)
                ms = QMessageBox()
                ms.setText("Error en el proceso. No se generaron segmentos")
                ms.setIcon(QMessageBox.Warning)
                ms.exec()
                time.sleep(1)
                progress.setValue(100)
                self.iface.messageBar().clearWidgets()
                return None
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
            return None
        else:
            #print('segmentar con opciones configuradas')
            time.sleep(1)
            progressMessageBar.setText('Procesando segmentacion')
            progress.setValue(20)
            #nuevos parametros
            Points_per_batch=self.Points_per_batch.value() #GPU
            PointsPerSide=self.Points_per_side.value()
            PredIouThresh=self.Pred_iou_thresh.value()
            StabilityScoreThresh=self.Stability_score_thresh.value()
            CropNLayers=self.Crop_n_layers.value()
            CropNPointsDownscaleFactor=self.Crop_n_points_downscale_factor.value()
            #print('Points_per_batch',Points_per_batch)
            #print('opcion vector' ,self.opVector.isChecked())
            #print('capas en combobox' ,self.listVector.count())
            if self.opVector.isChecked() and self.listVector.count()>0:
                capav=self.listVector.currentData()
                extensionv=capav.extent()
                #print('area exte imagen',extension.area(),', exte capa ',extensionv.area())
                #print(' comparacion de extents' ,extension.contains(extensionv))
                if extension.contains(extensionv):
                    grid=[puntosArreglo(capav,src,self.pry,geotransform)]
                    #print(len(grid),grid[0].shape,grid[0].ndim)
                    #print(grid)
                    if self.tinyhqop.isChecked():
                        mask_generator_2 = SamAutomaticMaskGenerator_f(
                            model=sam,
                            points_per_batch=Points_per_batch,
                            points_per_side=None,
                            pred_iou_thresh=PredIouThresh,
                            stability_score_thresh=StabilityScoreThresh,
                            crop_n_layers=CropNLayers,
                            crop_n_points_downscale_factor=CropNPointsDownscaleFactor,
                            point_grids=grid
                        )
                    else:
                        mask_generator_2 = SamAutomaticMaskGenerator(
                            model=sam,
                            points_per_batch=Points_per_batch,
                            points_per_side=None,
                            pred_iou_thresh=PredIouThresh,
                            stability_score_thresh=StabilityScoreThresh,
                            crop_n_layers=CropNLayers,
                            crop_n_points_downscale_factor=CropNPointsDownscaleFactor,
                            point_grids=grid
                        )
            else:
                #segmentacion
                if self.tinyhqop.isChecked():
                    mask_generator_2 = SamAutomaticMaskGenerator_f(
                        model=sam,
                        points_per_batch=Points_per_batch,
                        points_per_side=PointsPerSide,
                        pred_iou_thresh=PredIouThresh,
                        stability_score_thresh=StabilityScoreThresh,
                        crop_n_layers=CropNLayers,
                        crop_n_points_downscale_factor=CropNPointsDownscaleFactor,
                    )
                else:
                    mask_generator_2 = SamAutomaticMaskGenerator(
                        model=sam,
                        points_per_batch=Points_per_batch,
                        points_per_side=PointsPerSide,
                        pred_iou_thresh=PredIouThresh,
                        stability_score_thresh=StabilityScoreThresh,
                        crop_n_layers=CropNLayers,
                        crop_n_points_downscale_factor=CropNPointsDownscaleFactor,
                    )
                    mask_generator_2 = SamAutomaticMaskGenerator(
                        model=sam,
                        points_per_batch=Points_per_batch,
                        points_per_side=PointsPerSide,
                        pred_iou_thresh=PredIouThresh,
                        stability_score_thresh=StabilityScoreThresh,
                        crop_n_layers=CropNLayers,
                        crop_n_points_downscale_factor=CropNPointsDownscaleFactor,
                    )
            masks2 = mask_generator_2.generate(image)
            #print('mascaras generadas',len(masks2))
#            print(masks2[0].keys())
#            print(masks2[0].values())
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
                time.sleep(1)
                progress.setValue(100)
                self.iface.messageBar().clearWidgets()
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
                time.sleep(1)
                progress.setValue(100)
                self.iface.messageBar().clearWidgets()
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
        lmask=None
        listap=None
        self.liberarMemoria()
        
    #eventos de checkbox cambios de estatus
    def cambio_defecto(self,e):
        if e==2:
            self.opVector.setEnabled(False)
            self.listVector.setEnabled(False)
            self.label_12.setEnabled(False)
            self.label_14.setEnabled(False)
            self.Points_per_batch.setEnabled(False)
            self.label_3.setEnabled(False)
            self.label_4.setEnabled(False)
            self.Points_per_side.setEnabled(False)
            self.label_6.setEnabled(False)
            self.label_5.setEnabled(False)
            self.Pred_iou_thresh.setEnabled(False)
            self.label_7.setEnabled(False)
            self.label_8.setEnabled(False)
            self.Stability_score_thresh.setEnabled(False)
            self.label_10.setEnabled(False)
            self.label_9.setEnabled(False)
            self.Crop_n_layers.setEnabled(False)
            self.label_13.setEnabled(False)
            self.label_11.setEnabled(False)
            self.Crop_n_points_downscale_factor.setEnabled(False)
        elif e==0:
            self.opVector.setEnabled(True)
            self.listVector.setEnabled(True)
            self.label_12.setEnabled(True)
            self.label_14.setEnabled(True)
            self.Points_per_batch.setEnabled(True)
            self.label_3.setEnabled(True)
            self.label_4.setEnabled(True)
            self.Points_per_side.setEnabled(True)
            self.label_6.setEnabled(True)
            self.label_5.setEnabled(True)
            self.Pred_iou_thresh.setEnabled(True)
            self.label_7.setEnabled(True)
            self.label_8.setEnabled(True)
            self.Stability_score_thresh.setEnabled(True)
            self.label_10.setEnabled(True)
            self.label_9.setEnabled(True)
            self.Crop_n_layers.setEnabled(True)
            self.label_13.setEnabled(True)
            self.label_11.setEnabled(True)
            self.Crop_n_points_downscale_factor.setEnabled(True)
        
    def gestion_cambio(self,e):
        if e==2:
            self.nmodelo.setEnabled(False)
            self.brmodelo.setEnabled(False)
            self.label_20.setEnabled(False)
            self.label_21.setEnabled(False)
            self.ruta_file.setEnabled(False)
        elif e==0:
            self.nmodelo.setEnabled(True)
            self.brmodelo.setEnabled(True)
            self.label_20.setEnabled(True)
            self.label_21.setEnabled(True)
            self.ruta_file.setEnabled(True)
            
    def inicializar(self):
        #opciones de carga de modelo
        self.nmodelo.setEnabled(False)
        self.brmodelo.setEnabled(False)
        self.device.setEnabled(True)
        self.label_20.setEnabled(False)
        self.label_21.setEnabled(False)
        self.ruta_file.setEnabled(False)
        self.label_16.setEnabled(True)
        #opciones de configuracion
        self.opVector.setEnabled(False)
        self.listVector.setEnabled(False)
        self.label_12.setEnabled(False)
        self.label_14.setEnabled(False)
        self.Points_per_batch.setEnabled(False)
        self.label_3.setEnabled(False)
        self.label_4.setEnabled(False)
        self.Points_per_side.setEnabled(False)
        self.label_6.setEnabled(False)
        self.label_5.setEnabled(False)
        self.Pred_iou_thresh.setEnabled(False)
        self.label_7.setEnabled(False)
        self.label_8.setEnabled(False)
        self.Stability_score_thresh.setEnabled(False)
        self.label_10.setEnabled(False)
        self.label_9.setEnabled(False)
        self.Crop_n_layers.setEnabled(False)
        self.label_13.setEnabled(False)
        self.label_11.setEnabled(False)
        self.Crop_n_points_downscale_factor.setEnabled(False)
