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
from qgis.PyQt.QtGui import QIcon, QPixmap, QColor
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QFileDialog, QComboBox, QLineEdit, QMessageBox
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolPan, QgsVertexMarker,QgsMapToolEmitPoint
from qgis.core import (Qgis,QgsMapLayer, QgsRasterLayer, QgsProject, QgsMapLayerType, QgsRectangle,
                      QgsGeometry, QgsWkbTypes, QgsVectorLayer,QgsCoordinateReferenceSystem,
                      QgsCoordinateTransform,QgsPointXY)
#gestion de widgets
from .control_digitaliz import *
#modulos de sam
from .segment_anything.predictor import SamPredictor
from .segment_anything.build_sam import sam_model_registry
from .segment_anything.automatic_mask_generator import SamAutomaticMaskGenerator
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

#herramienta para marcar los puntos en pantalla
class ptool(QgsMapToolEmitPoint):
    def __init__(self, iface,dlg):
        self.ifac=iface
        self.dlg=dlg #Referencia al dialogo digitalizacion
        self.can=self.ifac.mapCanvas()
        QgsMapToolEmitPoint.__init__(self, self.can)
        self.inirubber()
        self.transform = self.can.getCoordinateTransform()
        self.deactivated.connect(self.reset)
        self.reseteado=False
        
    def inirubber(self):
        self.rubberBand = None
        self.rubberBand = QgsRubberBand(self.can, QgsWkbTypes.PointGeometry)
        if self.dlg.opPrompt.currentText()=='Adicionar a la selección':
            self.rubberBand.setColor(QColor(0,0,255))
        else:
            self.rubberBand.setColor(QColor(255,0,0))
        self.rubberBand.setIcon(QgsRubberBand.ICON_CROSS)
        self.rubberBand.setIconSize(10)
        self.rubberBand.setWidth(2)
    
    def canvasPressEvent(self, event):
        #print(' self.reseteado' ,self.reseteado)
        if self.reseteado==True:
            self.reseteado=False
            self.inirubber()
        self.pi=self.transform.toMapCoordinates(event.pos().x(),
                             event.pos().y())
#        print(event.pos().x(),event.pos().y())
#        print(self.pi.x(),self.pi.y())
        geo=QgsGeometry.fromPointXY(self.pi)
        self.rubberBand.setToGeometry(geo, None)
        self.dlg.captar_punto([self.pi.x(),self.pi.y()])
    
    def reset(self):
        self.reseteado=True
        try:
            self.can.scene().removeItem(self.rubberBand)
        except:
            pass
        
    def setColor(self,color):
        self.rubberBand.setColor(color)
        
        
#herramienta para dibujar el rectangulo en patalla
class rectangT(QgsMapTool):
    def __init__(self, iiface,dlg):
        QgsMapTool.__init__(self, iiface.mapCanvas())
        self.dlg=dlg #Referencia al dialogo digitalizacion
        self.iface = iiface
        self.can= self.iface.mapCanvas()
        self.transform = self.can.getCoordinateTransform()
        
        self.captar=False
        self.deactivated.connect(self.reset)
        #Lista que contendra los vertices
        self.vertexMarkers = []

    def canvasPressEvent(self, event):
        self.rubberBand = QgsRubberBand(self.can, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QColor(0,0,255,40))
        self.rubberBand.setWidth(1)
        self.pi=self.transform.toMapCoordinates(event.pos().x(),
                             event.pos().y())
#        self.pf= self.pi
        self.captar=True
        self.addVertex(self.pi)
    
    def canvasMoveEvent(self, event):
        if not self.captar:
          return
        self.pf= self.transform.toMapCoordinates(event.pos().x(),event.pos().y())
        self.dibujar()

    def canvasReleaseEvent(self, event):
        self.captar=False
        self.pf= self.transform.toMapCoordinates(event.pos().x(),
                    event.pos().y())
        self.addVertex(self.pf)
        self.dibujar()
        #Enviamos el rectangulo al dialogo, la region trazada por el usuario
        r=QgsRectangle(self.pi,self.pf)
        #obtenido el rectangulo actualizo histoSelec
        #print('rec enviado ',r)
        self.dlg.addArea(r)
        self.reset()
        #self.dlg.desactivarTool()
        
    def dibujar(self):
        if self.pi.x() == self.pf.x() or self.pi.y() == self.pf.y():
            self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
            return
        r=QgsRectangle(self.pi,self.pf)
        polig=r.asWktPolygon()
        geo=QgsGeometry().fromWkt(polig)
        self.rubberBand.setToGeometry(geo, None)

    def addVertex(self, pt):
        """
        Add a new vertex to the current polygon.
        @param {QgsPoint} pt Position of the mouse click in map coordinates
        """
        # And add also a small marker to highlight the vertices
        m = QgsVertexMarker(self.can)
        self.vertexMarkers.append(m)
        m.setCenter(pt)
       
    def reset(self):
        self.starP=None
        self.endP=None
        try:
            self.can.scene().removeItem(self.rubberBand)
        except:
            pass
        # Removemos los vertices
        for marker in self.vertexMarkers:
            self.can.scene().removeItem(marker)
            del(marker)
        self.can.refresh()

DialogUi, DialogType=uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'digitalizacion.ui'))

class dialog_digitalizacion(DialogUi, DialogType):
    """Construction and management of the panel creation wizard """
    def __init__(self,iface,listaVector,parametros):
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
        self.listaVector=listaVector
        
        #imagen portada
        iconportada= QPixmap(os.path.join(self.dir,'fondoimagen.png'))
        self.icon_portada.setPixmap(iconportada)

        #icono de la ventana
        rIdigi= os.path.join(self.dir,'icons//segnenti.png')
        iconv=QIcon(rIdigi)
        self.setWindowIcon(iconv)
        #iconos botones
        iconborrar=QIcon(os.path.join(self.dir,'icons','borrar.png'))
        self.borrarAreas.setIcon(iconborrar)
        self.borrarPuntos.setIcon(iconborrar)
        iconarea=QIcon(os.path.join(self.dir,'icons','area.png'))
        self.barea.setIcon(iconarea)
        iconpunto=QIcon(os.path.join(self.dir,'icons','punto.png'))
        self.bpunto.setIcon(iconpunto)
        
    #----PARAMETROS DE CAPTACION DE TRAZADOS EN PANTALLA
        #determina si se captaran multiplos rectangulos o uno solo
        self.multiple=False
        #Lista de puntos poligono dibujado tool barea
        self.rectangulo=None
        #lista de poligonos
        self.listAreas=[]
        #lista de puntos
        self.listPuntos=[]
        #dic poligonos
        self.dicAreas={}
        #dic puntos
        self.dicPuntos={}
        #variable booleana cuando se activan los tool
        self.dibuArea=False
        self.dibuPunto=False
        
        #ESTRUCTURAS PARA MAYOR FUNCIONALIDAD
        self.dicpm={0:[],1:[],'data':[]}
        self.dicarm={1:[],'data':[]}
        self.capMulti=False #identifica que se esta haciendo captura multiple
        self.dataMultiple={'geo':[]}
        self.reiniMultiple='Adicionar' #identifica si se adicionaran datos a una captura multiple o se trabajara una nueva
        
        #tool para dibujar puntos
        can = iface.mapCanvas()
        self.tool_punto = ptool(iface,self)
#        self.tool_punto.canvasClicked.connect(self.captar_punto)
        
        #damos formato a combox con tipos de prompts
        model = self.opPrompt.model()
        model.setData(model.index(0, 0), QtGui.QColor(0,0,255), QtCore.Qt.BackgroundRole)
        model.setData(model.index(1, 0), QtGui.QColor(255,0,0), QtCore.Qt.BackgroundRole)
        
        #EVENTOS
        self.bpunto.clicked.connect(self.dibujarPunto)
        self.barea.clicked.connect(self.dibujarArea)
        #eventos de borrado de geometrias
        self.borrarAreas.clicked.connect(self.borrar_areas)
        self.borrarPuntos.clicked.connect(self.borrar_puntos)
        #EVENTOS CHECKBOX
        self.op_capa.setChecked(False)
        self.op_atrib.setChecked(False)
        self.op_unsegment.setChecked(True)
        self.op_mayor.setChecked(False)
        self.op_mayor.setEnabled(False)

        #INICIALZAR LISTAS CAPAS VECTORIALES
        if len(self.listaVector)>0:
            self.cargarLista(self.listaVector)
        #INICIALIZAR CONTROLES
        #set pagina
        self.paginador.setCurrentIndex(0)
        self.op_capa.setChecked(False)
        if len(self.listaVector)==0:
            self.op_capa.setEnabled(False)
            self.op_crear_campo.setChecked(True)
            self.op_crear_campo.setEnabled(False)
        else:
            self.op_capa.setEnabled(True)
        self.listCVector.setEnabled(False)
        self.op_atrib.setChecked(False)
        self.lcampos.setEnabled(False)
        self.valor.setEnabled(False)
        #eventos controles checkbox y radio box
        self.op_capa.stateChanged.connect(self.gestion_cambio)
        self.op_atrib.stateChanged.connect(self.gestion_cambio)
        self.op_crear_campo.stateChanged.connect(self.gestion_cambio)
        self.op_unsegment.toggled.connect(lambda:self.btnstate(self.op_unsegment))
        self.op_multisegment.toggled.connect(lambda:self.btnstate(self.op_multisegment))
        #controles adicionales
        self.ncampo=QLineEdit()
        self.ncampo.setText('Categoria')
        self.ncampo.setMinimumWidth(120)
        self.ncampo.setMinimumHeight(23)
        #EVENTOS DEL PROYECTO
        self.pry.layersWillBeRemoved.connect(self.capaRemovida)
        self.pry.layersAdded.connect(self.capaAdicionada)
        #evento del combobox lista de capas vector
        self.listCVector.currentTextChanged.connect(self.cambio_capa)
        #evento del combobox tipo de seleccion o prompt
        self.opPrompt.currentTextChanged.connect(self.cambio_prompt)
        
        #EVENTO CAMBIAR PAGINA
        self.opAvanzadas.clicked.connect(self.cambiarPagina)
        iconavan=QIcon(os.path.join(self.dir,'icons','opAvanzadas.png'))
        self.opAvanzadas.setIcon(iconavan)
        self.opBasicas.clicked.connect(self.retornar)
        iconbasicas=QIcon(os.path.join(self.dir,'icons','opBasicas.png'))
        self.opBasicas.setIcon(iconbasicas)
        
        #Evento crear capa de datos de muestreo
        self.crearVector.clicked.connect(self.crear_vector)
        
        #control externo de widgets
        self.control=control_ui_digitaliz(self)
        self.control.inicializar()
        #estilo de los botones
        stylesheet = \
            "QPushButton {\n" \
            + "background-color: rgb(200, 200, 200);\n" \
            + "}" \
            + "QPushButton::flat{\n" \
            + "background-color: rgb(60, 60, 60);\n" \
            + "border: none;;\n" \
            + "}"
        self.barea.setStyleSheet(stylesheet)
        self.bpunto.setStyleSheet(stylesheet)
        self.ejecutar.clicked.connect(self.procesar)
        self.pushButton_2.clicked.connect(self.cerrar)
        self.reiniCapturaMultiple.clicked.connect(self.reini_cap_multi)

 
    def crear_vector(self):
        lcapas=crearCapaVector(self.listPuntos,self.listAreas,self.dicPuntos,\
                    self.dicAreas,self.dicpm,self.dicarm,self.pry)
        if len(lcapas)>0:
            for i in lcapas:
                self.pry.addMapLayer(i)
        
    def cambiarPagina(self,e):
        self.paginador.setCurrentIndex(1)
    
    def retornar(self,e):
        self.paginador.setCurrentIndex(0)
    
    def cambio_prompt(self):
        if self.opCaptura.isChecked()==True:#captura sencilla
            if self.opPrompt.currentText()=='Excluir de la selección':
                self.tool_punto.setColor(QColor(255,0,0))
            else:
                self.tool_punto.setColor(QColor(0,0,255))
        else:
            self.tool_punto.setColor(QColor(0,0,255))
        
    def btnstate(self,b):
        if self.sender().objectName()=='op_unsegment':
            self.op_mayor.setEnabled(False)
        if self.sender().objectName() == "op_multisegment":
            self.op_mayor.setEnabled(True)
        
    def gestion_cambio(self,e):
        self.control.gestion_check(self.sender().objectName(),e)
        
    def cambio_capa(self):
        #borramos lista de campos
        self.lcampos.clear()
        #cargamos los campos si tiene
        capa=self.listCVector.currentData()
        self.cargarCampos(capa)
        
    def addArea(self,r):
#        if self.nareas.value()<=10:
        #verificamos los sistemas de coordenadas de ser necesario se realiza 
        #la transformacion al sc de la imagen 
        sc=self.pry.crs().authid()
        sci=self.param.src.authid()
        #sci='EPSG:2202'
        if sc == sci:
            geo=r
        else:
            sc1=QgsCoordinateReferenceSystem(sc)
            sc2=QgsCoordinateReferenceSystem(sci)
            t=QgsCoordinateTransform(sc1,sc2,self.pry)
            rt=t.transform(r)
            geo=rt
        if self.opCaptura.isChecked()==False:#captura sencilla
            self.cierreCapturaMultiple()#cerramos la captura multiple si hay eventos
            if self.op_atrib.isChecked():
                if self.listCVector.count()==0 or self.op_crear_campo.isChecked():
                    #print(' crar area con atributos')
                    valor=self.valor.text()
                    ncampo=self.ncampo.text()
                    if ('crear',ncampo,valor) in self.dicAreas:
                        self.dicAreas[('crear',ncampo,valor)].append(geo)
                    else:
                        self.dicAreas[('crear',ncampo,valor)]=[geo]
                elif not self.op_crear_campo.isEnabled() or not self.op_crear_campo.isChecked():
                    if self.lcampos.isEnabled():
                        valor=self.valor.text()
                        ncampo=self.lcampos.currentText()
                        if ('campo',ncampo,valor) in self.dicAreas:
                            self.dicAreas[('campo',ncampo,valor)].append(geo)
                        else:
                            self.dicAreas[('campo',ncampo,valor)]=[geo]
                #print('diccionario de areas atributos',self.dicAreas)
            elif not self.op_atrib.isChecked():
                self.listAreas.append(geo)
                #print('lista',self.listAreas)
        else:#multiples puntos por captura
            #solo se lleva conteo en puntos
            self.reiniMultiple='Adicionar'
            self.capturaMultiple('positivo',punto=None,area=geo,data=None)
        #actualizamos el conteo d eventos disponibles
        nlista=len(self.listAreas)
        c=0
        for i in self.dicAreas:
            c=c+len(self.dicAreas[i])
        total=nlista+c
        self.nareas.setValue(total)
        #print('areas ',len(self.listAreas))

    def borrar_areas(self):
        self.nareas.setValue(0)
        self.listAreas=[]
        self.dicAreas={}
        self.dataMultiple={'geo':[]}

    def borrar_puntos(self):
        self.npuntos.setValue(0)
        self.listPuntos=[]
        self.dicPuntos={}
        self.dataMultiple={'geo':[]}

    #INICIALZAR LISTAS VECTOR
    def cargarLista(self,lista):
        for i in lista:
            self.listCVector.addItem(i.name(),i)
        #cargamos los campos si tiene
        capa=self.listCVector.currentData()
        self.cargarCampos(capa)
        
    def cargarCampos(self,capa):
        if type(capa)==QgsVectorLayer:
            campos=capa.fields()
            if not campos.isEmpty():
                for f in campos:
                    if f.typeName()=='Text' or f.typeName()=='String' or f.typeName()=='string':
                        self.lcampos.addItem(f.name(),f)
        
    def dibujarPunto(self):
        if self.dibuPunto==False:
            self.dibuArea=False
            self.bpunto.setFlat(True)
            #desactivar dibujar area
            self.barea.setFlat(False)
            self.iface.mapCanvas().setMapTool(self.tool_punto)
            self.dibuPunto=True
        else:
            self.bpunto.setFlat(False)
            self.dibuPunto=False
#            self.tool_punto.reset()
            try:
                self.iface.mapCanvas().setMapTool(QgsMapToolPan(self.iface.mapCanvas()))
            except:
                pass
                
    #METODOS DE CAPTURA MULTIPLE
    #metodo captura multiple
    def capturaMultiple(self,tipo,punto=None,area=None,data=None):
        if not punto==None:
            if tipo=='positivo':
                self.dicpm[1].append(punto)
            else:
                self.dicpm[0].append(punto)
            #almacenamos los datos
            if not data==None and len(self.dicpm['data'])==0:
                self.dicpm['data'].append(data)
#        print('self.dicpm',self.dicpm)
        if not area==None:
            self.dicarm[1].append(area)
            
    #cerrar captura multiple
    def cierreCapturaMultiple(self):
#        self.capMulti=False
        labels=[]
        lista=[]
        input_box =[]
        procesado=False#identifica si se cargo algun dato de las opciones
        geotransform=self.param.geotransform
        if len(self.dicpm[1])>0 or len(self.dicpm[0])>0:
            procesado=True #control interno q verifca si se agregaron datos validos
            for i in self.dicpm[1]:
                coords=coord_pixel(geotransform,i.x(),i.y())
                lista.append([coords[0], coords[1]])
                labels.append(1)
            if len(self.dicpm[0])>0:
                for i in self.dicpm[0]:
                    coords=coord_pixel(geotransform,i.x(),i.y())
                    lista.append([coords[0], coords[1]])
                    labels.append(0)
        if len(self.dicarm[1])==1:
            procesado=True
            i=self.dicarm[1][0]
            minx=i.xMinimum()
            maxx=i.xMaximum()
            miny=i.yMinimum()
            maxy=i.yMaximum()
            p1=coord_pixel(geotransform,minx,maxy)
            p2=coord_pixel(geotransform,maxx,miny)
            input_box.append([p1[0], p1[1], p2[0], p2[1]])
            input_box= np.array(input_box)
        if len(self.dicarm[1])>1:
            procesado=True
            for i in self.dicarm[1]:
                minx=i.xMinimum()
                maxx=i.xMaximum()
                miny=i.yMinimum()
                maxy=i.yMaximum()
                p1=coord_pixel(geotransform,minx,maxy)
                p2=coord_pixel(geotransform,maxx,miny)
                input_box.append([p1[0], p1[1], p2[0], p2[1]])
            input_box= np.array(input_box)
            input_box=torch.tensor(input_box, device=self.param.predictor.device)
#           print('filas y columnas',self.param.filas,self.param.columnas)
            input_box=self.param.predictor.transform.apply_boxes_torch(input_box, (self.param.filas,self.param.columnas))
#           print(len(input_box),input_box.shape)
            #print(' tipo input box transf',type(input_box),input_box)
        if procesado==True:
            #deben adicionarse puntos o areas, dado caso seria solo restar puntos
#            print('len(self.dicpm[1])',len(self.dicpm[1]))
#            print('len(self.dicarm[1])',len(self.dicarm[1]))
            if len(self.dicpm[1])>0 or len(self.dicarm[1])>0:
                data=None
                if len(self.dicpm['data'])>0:
                    data=self.dicpm['data'][0]
                #print('se envia la info',self.reiniMultiple)
                if self.reiniMultiple=='Nuevo' or len(self.dataMultiple['geo'])==0:
                    if not data==None:
                        self.dataMultiple['geo'].append([lista,labels,input_box,data])
                    else:
                        self.dataMultiple['geo'].append([lista,labels,input_box,[]])
                else:
                    #print('reinimultiple' ,self.reiniMultiple)
                    if self.reiniMultiple=='Adicionar' and len(self.dataMultiple['geo'])>0:
                        if len(self.dicpm[1])>0:
                            #print('adicionar despues de procesado')
                            #print(self.dataMultiple['geo'])
                            puntos=self.dataMultiple['geo'][0][0]
                            etiquetas=self.dataMultiple['geo'][0][1]
                            for i in zip(lista,labels):
                                puntos.append(i[0])
                                etiquetas.append(i[1])
                            self.dataMultiple['geo'][0][0]=puntos
                            self.dataMultiple['geo'][0][1]=etiquetas
                            #print('cambio',self.dataMultiple['geo'])
                self.dicpm={0:[],1:[],'data':[]}
                self.dicarm={1:[],'data':[]} 
                self.reiniMultiple='Adicionar'
        #elif len(self.dicarm[0])>0:
        #print('data multiple',self.dataMultiple)
        
    def reini_cap_multi(self):
        self.reiniMultiple='Nuevo'
        self.cierreCapturaMultiple()
        self.dicpm={0:[],1:[],'data':[]}
        self.dicarm={1:[],'data':[]}
    #-----------------------------------
    
    #metodo     ejecutado al hacer clic en el mapa
    def captar_punto(self,e):
        nlp=0
        ndp=0
        conteom=0
#        if self.npuntos.value()<=10:
        p= QgsPointXY(e[0],e[1])
        #verificamos los sistemas de coordenadas de ser necesario se realiza 
        #la transformacion al sc de la imagen 
        sc=self.pry.crs().authid()
        sci=self.param.src.authid()
#        sci='EPSG:2202'
        if sc == sci:
            geo=p
        else:
            sc1=QgsCoordinateReferenceSystem(sc)
            sc2=QgsCoordinateReferenceSystem(sci)
            t=QgsCoordinateTransform(sc1,sc2,self.pry)
            rt=t.transform(p)
            geo=rt
        if self.opCaptura.isChecked()==False:#captura sencilla
            self.cierreCapturaMultiple()#cerramos la captura multiple si hay eventos
            if self.op_atrib.isChecked():
                if self.listCVector.count()==0 or self.op_crear_campo.isChecked():
                    valor=self.valor.text()
                    ncampo=self.ncampo.text()
                    if ('crear',ncampo,valor) in self.dicPuntos:
                        self.dicPuntos[('crear',ncampo,valor)].append(geo)
                    else:
                        self.dicPuntos[('crear',ncampo,valor)]=[geo]
                elif not self.op_crear_campo.isEnabled() or not self.op_crear_campo.isChecked():
                    if self.lcampos.isEnabled():
                        valor=self.valor.text()
                        ncampo=self.lcampos.currentText()
                        if ('campo',ncampo,valor) in self.dicPuntos:
                            self.dicPuntos[('campo',ncampo,valor)].append(geo)
                        else:
                            self.dicPuntos[('campo',ncampo,valor)]=[geo]
                #print('diccionario',self.dicPuntos)
            elif not self.op_atrib.isChecked():
                self.listPuntos.append(geo)
        else:#multiples puntos por captura
            #sumamos al contador si comienza la captura
            #print(' self.capMulti',self.capMulti)
            datos=None
            if self.opPrompt.currentText()=='Adicionar a la selección':
                tipo='positivo'
            else:
                tipo='negativo'
             #almacenamos si no hay datos
            if len(self.dicpm['data'])==0:
                if self.op_atrib.isChecked():
                    #crear el campo
                    if self.listCVector.count()==0 or self.op_crear_campo.isChecked():
                        valor=self.valor.text()
                        ncampo=self.ncampo.text()
                        datos=('crear',ncampo,valor)
                    #guardar en campo existente
                    elif not self.op_crear_campo.isEnabled() or not self.op_crear_campo.isChecked():
                        if self.lcampos.isEnabled():
                            valor=self.valor.text()
                            ncampo=self.lcampos.currentText()
                            datos=('campo',ncampo,valor)
                    self.capturaMultiple(tipo,punto=geo,area=None,data=datos)
                else:
                    self.capturaMultiple(tipo,punto=geo,area=None,data=None)
            else:
                self.capturaMultiple(tipo,punto=geo,area=None,data=None)
#            print('lista',self.listPuntos)
        #ajustamos el contador
        nlp=len(self.listPuntos)
        ndp=len(self.dicPuntos)
        #print('lista y dic puntos normales',nlp,ndp)
        self.npuntos.setValue(0)
        if ndp>0:
            c=0
            for i in self.dicPuntos:
                v=len(self.dicPuntos[i])
                c=c+v
            self.npuntos.setValue(c)
        if nlp>0 and ndp>0:
            self.npuntos.setValue(nlp+self.npuntos.value())
        elif nlp>0 and ndp==0:
            self.npuntos.setValue(nlp)
        if len(self.dataMultiple['geo'])>0:
            self.npuntos.setValue(self.npuntos.value()+len(self.dataMultiple['geo']))
        #print('marcar captura ini conteom',conteom,self.capMulti,len(self.dicpm[1]))
#        if self.reiniMultiple=='Adicionar':
        if len(self.dicpm[1])>0 or len(self.dicarm[1])>0:
            self.npuntos.setValue(self.npuntos.value()+1)
            
    
    def dibujarArea(self):
        if self.dibuArea==False:
            self.dibuPunto=False
            self.barea.setFlat(True)
            #Activamos el tool para seleccionar la region
            self.sr=rectangT(self.iface,self)
            self.iface.mapCanvas().setMapTool(self.sr)
            #desactivar dibujar punto
            self.bpunto.setFlat(False)
            self.dibuArea=True
        else:
            self.barea.setFlat(False)
            self.dibuArea=False
            try:
                self.iface.mapCanvas().setMapTool(QgsMapToolPan(self.iface.mapCanvas()))
            except:
                pass
                
    def proces_previo(self):
        if len(self.listPuntos)>0 or len(self.listAreas)>0\
        or len(self.dicAreas)>0 or len(self.dicPuntos)>0:
            #or len(self.dicPuntos)>0:
            self.procesar()
         
    def cerrar(self):
        self.pry.layersWillBeRemoved.disconnect(self.capaRemovida)
        self.pry.layersAdded.disconnect(self.capaAdicionada)
        try:
            self.tool_punto.reset()#borramos el punto marcado en el canvas
        except:
            pass
        self.close()
        
    def liberarMemoria(self):
        torch.cuda.empty_cache()
        gc.collect()
                
    def procesar(self):
#        self.tool_punto.reset()#borramos el punto marcado en el canvas
        self.liberarMemoria()
        progressMessageBar = self.iface.messageBar().createMessage("El proceso de carga tomara varios minutos...")
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        time.sleep(1)
        self.iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
        #carpeta temporal
        tempdir=tempfile.TemporaryDirectory()
        ruta_out=tempdir.name
        #print(' directorio temporal existe',os.path.exists(ruta_out))
        #lista de mascaras
        listImagenes=[]
        dicImagenes={}
        #parametros
        predictor=self.param.predictor
        sam=self.param.sam
        wkt=self.param.wkt
        columnas=self.param.columnas
        filas=self.param.filas
        geotransform=self.param.geotransform
        epsg=self.param.src.authid()
        #procesamiento de puntos
        input_label=np.array([1])
        #estatus del proceso
        #opciones de salida
        if self.op_multisegment.isChecked(): 
            multiple=True
        else:
            multiple=False
        #print('multiple: ',multiple)
        #barra de progreso
        if len(self.listPuntos)>0:
            time.sleep(1)
            progressMessageBar.setText('Procesando seleccion por puntos')
            progress.setValue(20)
            #print('lista puntos',self.listPuntos)
            for i in self.listPuntos:
                coords=coord_pixel(geotransform,i.x(),i.y())
                #print(' transformacion coordenadas imagen',coords) 
                input_point=np.array([[coords[0], coords[1]]])
                #print('puntos norma',input_point)
                if self.param.nombre=="tinyhq":
                    masks, scores, logits = predictor.predict(
                        point_coords=input_point,
                        point_labels=input_label,
                        multimask_output=multiple,
                        hq_token_only=False
                    )
                elif self.param.nombre=="sam":
                    masks, scores, logits = predictor.predict(
                        point_coords=input_point,
                        point_labels=input_label,
                        multimask_output=multiple,
                    )               
                listap=mask_to_imagen(masks,ruta_out,'puntos',columnas,filas,wkt,geotransform)
                listImagenes.append(listap)
        #diccionario de puntos
        if len(self.dicPuntos)>0:
            for i in self.dicPuntos:
                da=self.dicPuntos[i]
                dicImagenes[i]=[]
                for c in da:
                    coords=coord_pixel(geotransform,c.x(),c.y())
                    input_point=np.array([[coords[0], coords[1]]])
                    if self.param.nombre=="tinyhq":
                        masks, scores, logits = predictor.predict(
                            point_coords=input_point,
                            point_labels=input_label,
                            multimask_output=multiple,
                            hq_token_only=False
                        )
                    elif self.param.nombre=="sam":
                        masks, scores, logits = predictor.predict(
                            point_coords=input_point,
                            point_labels=input_label,
                            multimask_output=multiple,
                        )
                    listap=mask_to_imagen(masks,ruta_out,'dipuntos',columnas,filas,wkt,geotransform)  
                    dicImagenes[i].append(listap)
            #print(dicImagenes)
        if len(self.listAreas)>0:
            #print('lista areas',self.listAreas)
            time.sleep(1)
            progressMessageBar.setText('Procesando seleccion por areas')
            progress.setValue(30)
            for i in self.listAreas:
                minx=i.xMinimum()
                maxx=i.xMaximum()
                miny=i.yMinimum()
                maxy=i.yMaximum()
                p1=coord_pixel(geotransform,minx,maxy)
                p2=coord_pixel(geotransform,maxx,miny)
                input_box = np.array([p1[0], p1[1], p2[0], p2[1]])
                if self.param.nombre=="tinyhq":
                    masks, _, _ = predictor.predict(
                        point_coords=None,
                        point_labels=None,
                        box=input_box[None, :],
                        multimask_output=multiple,
                        hq_token_only=False
                    )
                elif self.param.nombre=="sam":
                    masks, _, _ = predictor.predict(
                        point_coords=None,
                        point_labels=None,
                        box=input_box[None, :],
                    multimask_output=multiple,
                    )
                listap=mask_to_imagen(masks,ruta_out,'areas_atrb',columnas,filas,wkt,geotransform)
                listImagenes.append(listap)
        #diccionario de puntos
        if len(self.dicAreas)>0:
            time.sleep(1)
            progressMessageBar.setText('Procesando seleccion por areas')
            progress.setValue(40)
            for i in self.dicAreas:
                da=self.dicAreas[i]
                if not i in dicImagenes:
                    dicImagenes[i]=[]
                for c in da:
                    minx=c.xMinimum()
                    maxx=c.xMaximum()
                    miny=c.yMinimum()
                    maxy=c.yMaximum()
                    p1=coord_pixel(geotransform,minx,maxy)
                    p2=coord_pixel(geotransform,maxx,miny)
                    input_box = np.array([p1[0], p1[1], p2[0], p2[1]])
                    if self.param.nombre=="tinyhq":
                        masks, _, _ = predictor.predict(
                            point_coords=None,
                            point_labels=None,
                            box=input_box[None, :],
                            multimask_output=multiple,
                            hq_token_only=False
                        )
                    elif self.param.nombre=="sam":
                        masks, _, _ = predictor.predict(
                            point_coords=None,
                            point_labels=None,
                            box=input_box[None, :],
                            multimask_output=multiple,
                        )
                    listap=mask_to_imagen(masks,ruta_out,'areas_atrb',columnas,filas,wkt,geotransform)
                    dicImagenes[i].append(listap)
                    #print('dic imagenes',dicImagenes)
        #PROCESAR CAPTURA MULTIPLE
#        print('len(self.dicpm[1])',len(self.dicpm[1]))
#        print('len(self.dicarm[1])',len(self.dicarm[1]))
        if len(self.dicpm[1])>0 or len(self.dicarm[1])>0:
            self.cierreCapturaMultiple()
        if len(self.dataMultiple['geo'])>0:
            #inicializamos las variables pq pudieron cambiar en la siteraciones anteriores
            input_box=None
            input_point=None
            labels=None
            time.sleep(1)
            progressMessageBar.setText('Procesando seleccion captura multiple')
            progress.setValue(70)
            for i in self.dataMultiple['geo']:
                #print(i)
                if len(i[2])>0:
                    input_box=i[2]
                else:
                    input_box=None
                if len(i[0])>0:
                    input_point=np.array(i[0])
                    labels=np.array(i[1])
                else:
                    input_point=None
                    labels=None
#                print('input_point',input_point)
#                print('labels',labels)
#                print('input_box',input_box,input_box.shape,input_box.ndim)
                if self.param.nombre=="tinyhq":
                    if not input_box is None:
                        if len(input_box)>1:
                            #print('multiples cajas tiny',input_box)
                            masks, scores, logits = predictor.predict_torch(
                                point_coords=None,
                                point_labels=None,
                                boxes=input_box,
                                multimask_output=multiple,
                                hq_token_only=False
                            )
                            self.iface.messageBar().pushMessage('ADVERTENCIA',\
                            '<b>Con multiples areas no se consideran puntos de seleccion</b>', level=Qgis.Info, duration=7)
                            masks=masks.cpu().numpy()
                            masksl=[]
                            for x in range(len(masks)):
                                masksl.append(masks[x])
                            masks=masksl
                    else:
                        masks, scores, logits = predictor.predict(
                            point_coords=input_point,
                            point_labels=labels,
                            box=input_box,
                            multimask_output=multiple,
                            hq_token_only=False
                        )
                elif self.param.nombre=="sam":
                    #print(' tipo tensor',type(input_box))
                    if not input_box is None:
                        if len(input_box)>1:
                            masks, scores, logits = predictor.predict_torch(
                                point_coords=None,
                                point_labels=None,
                                boxes=input_box,
                                multimask_output=multiple,
                            )
                            self.iface.messageBar().pushMessage('ADVERTENCIA',\
                            '<b>Con multiples areas no se consideran puntos de seleccion</b>', level=Qgis.Info, duration=7)
                            masks=masks.cpu().numpy()
                            masksl=[]
                            for x in range(len(masks)):
                                masksl.append(masks[x])
                            masks=masksl
                            #print('a numpy',masks,len(masks),masks[0],masks[0].shape,masks[1],masks[1].shape)
                    else:
                        masks, scores, logits = predictor.predict(
                            point_coords=input_point,
                            point_labels=labels,
                            box=input_box,
                            multimask_output=multiple,
                        )
                        #print(' mascara normal',masks,len(masks),masks.shape)
                #AQUI PROCESAMOS LOS ATRIBUTOS
                if len(i[3])==0:
                    listapm=mask_to_imagen(masks,ruta_out,'puntos',columnas,filas,wkt,geotransform)
                    listImagenes.append(listapm)
                elif len(i[3])>0:
                    dicImagenes[i[3]]=[]
                    listapm=mask_to_imagen(masks,ruta_out,'dipuntos',columnas,filas,wkt,geotransform)  
                    dicImagenes[i[3]].append(listapm)
            #inicializamos la captura multiple
            #self.dataMultiple={'geo':[]}
        #print('mascara',masks,len(masks))
        #print('lista de imagenes antes de procesar' ,listImagenes)
        time.sleep(1)
        progressMessageBar.setText('Procesando segmentos')
        progress.setValue(50)
        #vectorizar
        listcapas=[]
        diccapas={}
        #procesar listas y diccionarios, crear capas vectoriales
        #si multiple es true creamos listas dentro de lista, sino, bastara
        #una sola lista
        if multiple:
            if len(listImagenes)>0:
                for i in listImagenes:
                    #print(' list imagenes 0',i)
                    list=[]
                    for l in i:
                        #print('m ruta imagen entrada ' ,l)
                        if os.path.exists(l):
                            vector=vectorizar(l)
                            #print(' ruta capa vector',vector)
                            list.append(vector)
                    listcapas.append(list)
        else:
            if len(listImagenes)>0:
                for i in listImagenes:
                    #print(' list imagenes 0',i)
                    for l in i:
                        #print(' ruta imagen entrada ' ,l)
                        if os.path.exists(l):
                            vector=vectorizar(l)
                            #print('ruta capa vector',vector)
                            listcapas.append(vector)
#        print(' listcapas de salida de su creacion' ,listcapas)
        if len(dicImagenes)>0:
            #print('numero de imagenes generadas',len(dicImagenes))
            for i in dicImagenes:
                lista=dicImagenes[i]
                diccapas[i]=[]
                for l in lista:
                    list=[]
                    for c in l:
                        if os.path.exists(c):
                            list.append(vectorizar(c))
                    diccapas[i].append(list)
        #print('dic' ,diccapas)
        if self.op_multisegment.isChecked() and self.op_mayor.isChecked():
            #----------------------------------------------------------
            #dependiendo del control se crea o se anaden a capa existente
            if self.op_capa.isChecked():
                capa=self.listCVector.currentData()
                cargar_capa_exist_mayor(capa,listcapas,epsg)
                cargar_capa_exist_atrib_mayor(capa,diccapas,epsg)
                capa.triggerRepaint()
            else:
                resultado=crear_capa_mayor_salida(listcapas,epsg)
                if not resultado is None:
                    #print('resultado',type(resultado))
                    cargar_capa_exist_atrib_mayor(resultado,diccapas,epsg)
                else:
                    resultado=crear_capa_mayor_atrib(diccapas,epsg)
        else:
            #----------------------------------------------------------
            #dependiendo del control se crea o se anaden a capa existente
            if self.op_capa.isChecked():
                capa=self.listCVector.currentData()
                cargar_capa_exist(capa,listcapas,epsg,multi=multiple)
                cargar_capa_exist_atrib(capa,diccapas,epsg)
                capa.triggerRepaint()
            else:
                resultado=crear_capa_salida(listcapas,epsg,multi=multiple)
                if not resultado is None:
                    cargar_capa_exist_atrib(resultado,diccapas,epsg)
                else:
                    resultado=crear_capa_atrib(diccapas,epsg)
                    #print('resultado capa atrib',resultado)
        #si creamos una nueva capa la cargamos
        if not self.op_capa.isChecked():
            self.pry.addMapLayer(resultado)
        #proceso finalizado
        time.sleep(1)
        progress.setValue(100)
        self.iface.messageBar().clearWidgets()
        self.liberarMemoria()
        masks=None
        listap=None
        #borrar imagenes temporales
        for i in listImagenes:
            try:
                rmtree(i)
            except:
                pass
        for i in dicImagenes:
            lista=dicImagenes[i]
            for l in lista:
                for c in l:
                    if os.path.exists(c):
                        try:
                            rmtree(c)
                        except:
                            pass

    def capaRemovida(self,ids):
        for i in ids:
            for j in self.listaVector:
                id=j.id()
                if i==id:
                    self.listaVector.remove(j)
                    ubi=self.listCVector.findData(j)
                    if ubi!=-1:
                        self.listCVector.removeItem(ubi)
                        self.lcampos.clear()
        if self.listCVector.count()==0:
            self.op_capa.setChecked(False)
            self.listCVector.setEnabled(False)
        else:
            capa=self.listCVector.currentData()
            self.cargarCampos(capa)
        
    def capaAdicionada(self,lista):
        c=0
        for i in lista:
            if i.type()==QgsMapLayer.VectorLayer or isinstance(i,QgsVectorLayer):
                if i.geometryType()== QgsWkbTypes.PolygonGeometry:
                    c=c+1
                    self.listCVector.addItem(i.name(),i)
                    self.listaVector.append(i)
        if c>0:
            self.op_capa.setEnabled(True)
            capa=self.listCVector.currentData()
            self.cargarCampos(capa)
        

