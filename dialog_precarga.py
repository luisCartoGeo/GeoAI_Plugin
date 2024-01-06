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
import time
from qgis.PyQt import uic
from qgis import PyQt
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt import QtGui
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QFileDialog, QComboBox, QProgressBar, QMessageBox
from qgis.core import (Qgis, QgsMapLayer, QgsRasterLayer, QgsProject, QgsMapLayerType)
#modulos de sam
from .segment_anything import *
from .segment_anything.predictor import SamPredictor
from .segment_anything.build_sam import sam_model_registry
from .segment_anything.automatic_mask_generator import SamAutomaticMaskGenerator

#modulos de sam_f
from .segment_fast import *
from .segment_fast.predictor_f import SamPredictor_f
from .segment_fast.build_sam_f import sam_model_registry_f
#librerias requeridas
import torch
import os
import numpy as np
#utilidades y procesos
from .utils import *
try:
    import gdal
except:
    from osgeo import gdal

DialogUi, DialogType=uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'precarga.ui'))

class dialog_precarga(DialogUi, DialogType):
    """Construction and management of the panel creation wizard """
    def __init__(self,iface,listaRaster,parametros):
        """Constructor.
        :param iface: viene de la clase de inicialización, permite interactura con la interfaz
        :tipo iface: QgisInterface,
        :param listaRaster: lista de capas raster ya cargadas en el mapa, viene de la inicializacion
        :tipo litRaster: list
        :param parametros: encapsula los parametros de configuracion del modelo/imagen, vienen vacios,
        seran calculados e inicializados por este dialogo
        :tipo parametros: clase sencilla con con cuatro atributos 
        """
        super().__init__()
        self.setupUi(self)
        self.iface=iface
        self.pry=QgsProject.instance()
        self.dir = os.path.dirname(__file__)
        self.ruta_modelo=None
        #Instancia de clase que almacena los parametros del modelo e imagen
        self.param=parametros
        
        #lista de capas
        self.listaRaster=listaRaster
        #icono de la ventana
        rutaiconv= os.path.join(self.dir,'icon.png')
        iconv=QIcon(rutaiconv)
        self.setWindowIcon(iconv)

        #tiny checkpoint
        self.modeltiny= os.path.join(self.dir,'sam_hq_vit_tiny.pth')
        #inicializamos con tiny marcado
        self.nmodelo.setEnabled(False)
        self.brmodelo.setEnabled(False)
        self.device.setEnabled(False)
        self.label_3.setEnabled(False)
        self.label_4.setEnabled(False)
        self.ruta_file.setEnabled(False)
        self.label_6.setEnabled(False)
        self.tinyhqop.stateChanged.connect(self.gestion_cambio)

        #imagen portada
        iconportada= QPixmap(os.path.join(self.dir,'fondonegro.png'))
        self.icon_portada.setPixmap(iconportada)
        
        #----------------
        #self.opAvanzadas.clicked.connect(self.cambiarPagina)
        #iconavan=QIcon(os.path.join(self.dir,'icons','opAvanzadas.png'))
        #self.opAvanzadas.setIcon(iconavan)
        #self.opBasicas.clicked.connect(self.retornar)
        #iconbasicas=QIcon(os.path.join(self.dir,'icons','opBasicas.png'))
        #self.opBasicas.setIcon(iconbasicas)
        
        #listado de comboBox de Bandas
        self.lbandas=(self.bandR,self.bandG,self.bandB)
        
        #Configuracion inicial
        self.paginador.setCurrentIndex(0)
        
        #EVENTOS
        self.bejecutar.clicked.connect(self.ejecutar)
        self.bcancelar.clicked.connect(self.cerrar)
        self.brmodelo.clicked.connect(self.archivo_modelo)

        #EVENTOS DEL PROYECTO
        self.pry.layersWillBeRemoved.connect(self.capaRemovida)
        self.pry.layersAdded.connect(self.capaAdicionada)
        #EVENTO AL CAMBIAR LA CAPA
        self.listImagen.currentTextChanged.connect(self.cambioCapa)
        
        #INICIALZAR LISTAS RASTER
        self.cargarLista(self.listaRaster)

    def gestion_cambio(self,e):
        if e==2:
            self.nmodelo.setEnabled(False)
            self.brmodelo.setEnabled(False)
            self.device.setEnabled(False)
            self.label_3.setEnabled(False)
            self.label_4.setEnabled(False)
            self.ruta_file.setEnabled(False)
            self.label_6.setEnabled(False)
        elif e==0:
            self.nmodelo.setEnabled(True)
            self.brmodelo.setEnabled(True)
            self.device.setEnabled(True)
            self.label_4.setEnabled(True)
            self.ruta_file.setEnabled(True)
            self.label_6.setEnabled(True)

    def ejecutar(self):
        if self.tinyhqop.isChecked()==False:
            #si no se utiliza el hq tiny verificamos que se cargo el modelo, desplegamos la busqueda del archivo         
            ruta=self.ruta_file.text()
            if not os.path.exists(ruta):
                d= QFileDialog.getOpenFileName(None,"Ruta al modelo, generalmente sam_vit_h_4b8939.pth")
                if os.path.exists(d):
                    ruta=d
                else:
                    self.cerrar()
                    self.iface.messageBar().pushMessage('ERROR',\
                    '<b>Error en la ruta del modelo</b>', level=0, duration=7)
                    return None
            #verificando correcta asignacion del nombre del modelo
            nf=os.path.basename(ruta)
            if nf=='sam_vit_h_4b8939.pth':
                nombre_modelo='vit_h'
            elif nf=='sam_vit_l_0b3195.pth':
                nombre_modelo='vit_l'
            elif nf=='sam_vit_b_01ec64.pth':
                nombre_modelo='vit_b'
            else:
                nombre_modelo=self.nmodelo.currentText()
            nombre_modelo=self.nmodelo.currentText()
            
        #INFORMAR EL ESTATUS DEL PROCESO
        progressMessageBar = self.iface.messageBar().createMessage("El proceso de carga tomara varios minutos...")
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        time.sleep(1)
        self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
        time.sleep(1)
        progress.setValue(10)
        #-----------------------------
        #cerramos la caja de dialogo evitar que se ejecute dos veces
        self.cerrar()
        #--------------------------------------------------
        imagen=self.listImagen.currentData()
        #sistema de coordenadas de la imagen
        src=imagen.crs()
        extension=imagen.extent()
        if self.tinyhqop.isChecked()==False:
            ruta_modelo=ruta
            device=self.device.currentText()
            if device=='CPU':
                device='cpu'
            else:
                if torch.cuda.is_available():
                    device='cuda'
                else:
                    device='cpu'
                    #print('GPU no disponible se utiliza el cpu')
            
        #captar primeras bandas con gdal y convertir en array
        #generar sam y predictor, guardarlos en la clase parametros
        resultado=self.cargar_imagen(imagen)
        arreglo=resultado[0]
        time.sleep(1)
        progress.setValue(50)
        #Configuracion del modelo
        if self.tinyhqop.isChecked():
            device = torch.device("cpu")
            sam = sam_model_registry_f['vit_tiny'](checkpoint=self.modeltiny)
            sam.to(device=device)
            sam.eval()
            predictor = SamPredictor_f(sam)
            predictor.set_image(arreglo)
        else:
            #try:
            sam = sam_model_registry[nombre_modelo](checkpoint=ruta_modelo)
            sam.to(device=device)
            predictor = SamPredictor(sam)
            predictor.set_image(arreglo)
            """
            except Exception as e:
                self.iface.messageBar().pushMessage('ERROR',\
                str(e), level=0, duration=7)
                ms = QMessageBox()
                ms.setText("No se pudo configurar modelo"+str(e))
                ms.setIcon(QMessageBox.Warning)
                ms.exec()
                return None"""
            #guardamos los parametros en la instancia de parametros
        self.param.activo=True
        self.param.sam=sam
        #sistema de coordenadas segun QGIS
        if self.tinyhqop.isChecked():
            self.param.nombre="tinyhq"
        else:
            self.param.nombre="sam"
        self.param.src=src
        self.param.extenti=extension
        self.param.predictor=predictor
        self.param.geotransform=resultado[1][0]
        self.param.filas=resultado[1][1]
        self.param.columnas=resultado[1][2]
        self.param.wkt=resultado[1][3]
        self.param.arreglo=arreglo
        del(sam)
        del(predictor)
        del(resultado)
        del(arreglo)
        #proceso finalizado
        time.sleep(1)
        progress.setValue(100)
        self.iface.messageBar().clearWidgets()

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
        #valor minimo y maximo considerando todas las capas
        #debe ajustarse para solo las capas que se utilizaran
        minmax=minimo_maximo(capa)
        del(arr)
        del(bimag)
        #creamos el arreglo de salida
        lbands= []
#        print(' numero de bandas',nbandas)
        #if nbandas>1:
        if nbandas>1:
            l=[int(i.currentText()) for i in self.lbandas]
            for n in l:
                #print('banda ',n)
                b=capag.GetRasterBand(n)
                ba=b.ReadAsArray()
#                print(ba.dtype)
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
#        imagen=self.listImagen.currentData()
#        nbandas=imagen.bandCount()
#        for i in self.lbandas:
#            i.addItems([str(i) for i in range(1,nbandas+1)])
            
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
    #Se adiciono una nueva capa    
    def capaAdicionada(self,lista):
        for i in lista:
            if i.type()==QgsMapLayer.RasterLayer or isinstance(i,QgsRasterLayer):
                if i.dataProvider().description()=='GDAL data provider':
                    self.listImagen.addItem(i.name(),i)
                    
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
        self.paginador.setCurrentIndex(1)
    
    def retornar(self,e):
        self.paginador.setCurrentIndex(0)
