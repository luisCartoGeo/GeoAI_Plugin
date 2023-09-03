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

from PyQt5.QtWidgets import QAction, QMessageBox

def classFactory(iface):
    """Load ini_geosam class from file ini_geosam.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ini_geoai import ini_geoai
    return ini_geoai(iface)
