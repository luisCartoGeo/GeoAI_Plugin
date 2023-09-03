# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoSam, un complemento para QGIS

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
from qgis.PyQt.QtWidgets import QGridLayout
from qgis.PyQt import QtCore

class control_ui_digitaliz:
    def __init__(self,dlg):
        self.dlg=dlg

    def inicializar(self):
        self.grid_atrib=QGridLayout()
        self.grid_atrib.addWidget(self.dlg.lcampos,0,0)
        self.grid_atrib.addWidget(self.dlg.valor,0,1)
        self.dlg.patrib.setLayout(self.grid_atrib)
        self.grid_atrib.setAlignment(QtCore.Qt.AlignTop)
    
    def gestion_check(self,checkbox,e):
        #opcion capa existente
        op_capa=self.dlg.op_capa.objectName() 
        #opcion para definir atributos de segmentos
        op_atrib=self.dlg.op_atrib.objectName() 
        #gestion de cambios
        if self.dlg.listCVector.count()>0:
            print(self.dlg.listCVector.count())
            print(checkbox,e)
            if checkbox=='op_capa' and e==0: 
                self.dlg.listCVector.setEnabled(False)
                if self.dlg.op_atrib.isChecked():
                    self.nuevo_campo()
                    self.dlg.op_crear_campo.setEnabled(False)
                elif self.dlg.op_atrib.isChecked()==False:
                    self.sin_atributos()
            elif checkbox=='op_capa' and e==2: 
                self.dlg.listCVector.setEnabled(True)
                if self.dlg.op_atrib.isChecked() and self.dlg.op_crear_campo.isChecked():
                    self.dlg.op_crear_campo.setEnabled(True)
                    self.nuevo_campo()
                elif self.dlg.op_atrib.isChecked() and self.dlg.op_crear_campo.isChecked()==False:
                    self.campo_existente()
                elif self.dlg.op_atrib.isChecked()==False:
                    self.sin_atributos()    
            elif checkbox=='op_atrib' and e==0:
                self.sin_atributos()
            elif checkbox=='op_atrib' and e==2 and not self.dlg.op_capa.isChecked():
                self.dlg.op_crear_campo.setEnabled(True)
                self.dlg.op_crear_campo.setChecked(True)
                self.dlg.op_crear_campo.setChecked(True)
                self.dlg.op_crear_campo.setEnabled(False)
                self.nuevo_campo()
            elif checkbox=='op_atrib' and e==2 and self.dlg.op_capa.isChecked():
                self.dlg.op_crear_campo.setEnabled(True)
                if self.dlg.op_crear_campo.isChecked():
                    self.nuevo_campo()
                elif self.dlg.op_crear_campo.isChecked()==False:
                    self.campo_existente()
            elif checkbox=='op_crear_campo' and e==0 and self.dlg.op_capa.isChecked():
                self.campo_existente()
            elif checkbox=='op_crear_campo' and e==2:
                self.nuevo_campo()
        if self.dlg.listCVector.count()==0:
            if checkbox=='op_atrib' and e==0:
                self.sin_atributos()
            elif checkbox=='op_atrib' and e==2:
                self.nuevo_campo()
            
        #elif self.dlg.op_capa.isEnabled()==False:    
       
    def nuevo_campo(self):
        self.dlg.lcampos.setParent(None)   
        self.dlg.valor.setParent(None)
        self.grid_atrib.addWidget(self.dlg.ncampo,0,0)
        self.grid_atrib.addWidget(self.dlg.valor,0,1)
        self.dlg.ncampo.setEnabled(True)
        self.dlg.valor.setEnabled(True)
        self.dlg.patrib.setLayout(self.grid_atrib)
    
    def campo_existente(self):
        print('campo existente')
        #if self.dlg.listCVector.count()>0:
        self.dlg.listCVector.setEnabled(True)
        self.dlg.ncampo.setParent(None)   
        self.dlg.valor.setParent(None)
        self.dlg.lcampos.setEnabled(True)
        self.dlg.valor.setEnabled(True)
        self.grid_atrib.addWidget(self.dlg.lcampos,0,0)
        self.grid_atrib.addWidget(self.dlg.valor,0,1)
    
    def sin_atributos(self):
        self.dlg.lcampos.setEnabled(False)
        self.dlg.ncampo.setEnabled(False)
        self.dlg.valor.setEnabled(False)
        self.dlg.op_crear_campo.setEnabled(False)
            
            
