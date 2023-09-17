import os, glob, random
try:
    import osr
except:
    from osgeo import osr
import processing
from osgeo import gdal
import numpy as np
import tempfile
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsField,QgsMapLayer,QgsFeature,QgsRasterLayer,
           QgsGeometry,QgsVectorLayer,QgsRasterBandStats)

def vectorizar(ruta):
    #print(' imagen a vectorizar',ruta)
    r=processing.run("gdal:polygonize", 
    {'INPUT':ruta,\
    'BAND':1,'FIELD':'DN',\
    'EIGHT_CONNECTEDNESS':True,\
    'OUTPUT':'TEMPORARY_OUTPUT'}
    )
    return r['OUTPUT']
    
def mask_to_imagen(mascara,ruta,nombre,columnas,filas,wkt,geotransform):
    lnombres=[]
    for e,mi in enumerate(mascara):
        arrf=np.where(mi==True,1.0,np.nan)
        nombrei=nombre+'.tif'
        #verificacion de nombre archivo
        for a in glob.glob(os.path.join(ruta,"*.tif")):
            nfile=os.path.basename(a)
            #nfile=nfile[:nfile.find('.')]
            if nfile==nombrei:
                rand=random.randint(0,1000)
                nombrei=nombre+str(rand)+'.tif'
        rnombrei=os.path.join(ruta,nombrei)
        driver = gdal.GetDriverByName("GTiff")
        output_file = rnombrei
        dst_ds = driver.Create(output_file, columnas,filas, 1, gdal.GDT_Float32,options=['COMPRESS=LZW'])
        dst_ds.GetRasterBand(1).WriteArray(arrf)
        dst_ds.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromWkt(wkt)
        dst_ds.SetProjection( srs.ExportToWkt() )
        lnombres.append(rnombrei)
        dst_ds=None
        srs=None
    return lnombres
    
def minimo_maximo(imagen):
    extension=imagen.extent()
    nbandas=imagen.bandCount()
    provider= imagen.dataProvider()
    #determinar minimo y maximo
    for i in range(nbandas):
        stats = provider.bandStatistics(i+1, QgsRasterBandStats.All, extension)
        min = stats.minimumValue
        max = stats.maximumValue
        #print('banda',i+1,min,max)
        if i==0:
            minimo=min
            maximo=max
        else:
            if min<minimo:
                minimo=min
            if max>maximo:
                maximo=max
    return (minimo,maximo)

def crear_capa_salida(lista,epsg,multi=False):
    if len(lista)>0:
        #extraer geometrias
        list_geo=[]
        if multi:
            for l in lista:
                for v in l:
                    #print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    f=next(f1)
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
        else:
            for v in lista:
                #print(v)
                vc=QgsVectorLayer(v,'vector','ogr')
                f1=vc.getFeatures('"DN"=1')
                f=next(f1)
                #print(f)
                g=f.geometry()
                #print(g)
                list_geo.append(g)
        #print(' lista geometrias ' ,list_geo)
        #print(epsg)
        #creamos la capa de salida
        uri = "polygon?crs="+epsg+"&field=id:integer"
        salida = QgsVectorLayer(uri, "ResultadoSAM",  "memory")
        lfeatures=[]
        provider=salida.dataProvider()
        for i in list_geo:
            f=QgsFeature()
            f.setFields(salida.fields())
            f.setGeometry(i)
            lfeatures.append(f)
        provider.addFeatures(lfeatures)
        return salida
    else:
        return None
        
def crear_capa_atrib(dic,epsg):
    if len(dic)>0:
        #creamos la capa de salida
        uri = "polygon?crs="+epsg+"&field=id:integer"
        salida = QgsVectorLayer(uri, "ResultadoSAM",  "memory")
        #obtenemos el provedor para editar
        provider=salida.dataProvider()
        for i in dic:
            tipo=i[0]
            ncampo=i[1]
            valor=i[2]
            lista=dic[i]
            #extraer geometrias
            list_geo=[]
            for l in lista:
                for v in l:
                    #print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    f=next(f1)
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
            camp = QgsField(ncampo, QVariant.String)
            provider.addAttributes([camp])
            salida.updateFields()
            lfeatures=[]
            for i in list_geo:
                f=QgsFeature()
                f.setFields(salida.fields())
                f.setGeometry(i)
                f.setAttribute(ncampo, valor)
                lfeatures.append(f)
            provider.addFeatures(lfeatures)
        return salida
    else:
        return None

def crear_capa_mayor_atrib(dic,epsg):
    if len(dic)>0:
        #creamos la capa de salida
        uri = "polygon?crs="+epsg+"&field=id:integer"
        salida = QgsVectorLayer(uri, "ResultadoSAM",  "memory")
        #obtenemos el provedor para editar
        provider=salida.dataProvider()
        for i in dic:
            tipo=i[0]
            ncampo=i[1]
            valor=i[2]
            lista=dic[i]
            #extraer geometrias
            list_geo=[]
            for l in lista:
                lgeo=[]
                for v in l:
                    #print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    f=next(f1)
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    lgeo.append(g)
                if len(lgeo)>1:
                #print('mas de una geometria' ,lgeo)
                    for e,x in enumerate(lgeo):
                        if e==0:
                            #print('area ',str(e),x.area())
                            xs=x
                        else:
                            #print('area ',str(e),x.area())
                            if x.area() >xs.area():
                                xs=x
                    list_geo.append(xs)
                else:
                    #print('solo una geometria',lgeo)
                    list_geo.append(lgeo[0])
            camp = QgsField(ncampo, QVariant.String)
            provider.addAttributes([camp])
            salida.triggerRepaint()
            salida.updateFields()
            lfeatures=[]
            for i in list_geo:
                f=QgsFeature()
                f.setFields(salida.fields())
                f.setGeometry(i)
                f.setAttribute(ncampo, valor)
                lfeatures.append(f)
            provider.addFeatures(lfeatures)
        return salida
    else:
        return None
        
def crear_capa_mayor_salida(lista,epsg):
    if len(lista)>0:
        #print(' capa mayor salida')
        #extraer geometrias
        list_geo=[]
        for l in lista:
#            print(l)
            lgeo=[]
            for v in l:
                #print(v)
                vc=QgsVectorLayer(v,'vector','ogr')
                f1=vc.getFeatures('"DN"=1')
                f=next(f1)
                #print(f)
                g=f.geometry()
                #print(g)
                lgeo.append(g)
            #procesar listas de geometrias
            if len(lgeo)>1:
                #print('mas de una geometria' ,lgeo)
                for e,x in enumerate(lgeo):
                    if e==0:
                        #print('area ',str(e),x.area())
                        xs=x
                    else:
                        #print('area ',str(e),x.area())
                        if x.area() >xs.area():
                            xs=x
                list_geo.append(xs)
            else:
                #print('solo una geometria',lgeo)
                list_geo.append(lgeo[0])
        #creamos la capa de salida
        uri = "polygon?crs="+epsg+"&field=id:integer"
        salida = QgsVectorLayer(uri, "ResultadoSAM",  "memory")
        lfeatures=[]
        provider=salida.dataProvider()
        for i in list_geo:
            f=QgsFeature()
            f.setFields(salida.fields())
            f.setGeometry(i)
            lfeatures.append(f)
        provider.addFeatures(lfeatures)
        return salida
    else:
        return None

def cargar_capa_exist(capa,lista,epsg,multi=False):
    if capa.crs().authid()==epsg:
        #extraer geometrias
        list_geo=[]
        if multi:
            for l in lista:
                for v in l:
                    #print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    f=next(f1)
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
        else:
            for v in lista:
                #print(v)
                vc=QgsVectorLayer(v,'vector','ogr')
                f1=vc.getFeatures('"DN"=1')
                f=next(f1)
                #print(f)
                g=f.geometry()
                #print(g)
                list_geo.append(g)
        lfeatures=[]
        provider=capa.dataProvider()
        for i in list_geo:
            f=QgsFeature()
            f.setFields(capa.fields())
            f.setGeometry(i)
            lfeatures.append(f)
        provider.addFeatures(lfeatures)
    else:
        print('sistema de coordenadas de la capa difernte al de la imagen')

def cargar_capa_exist_mayor(capa,lista,epsg):  
    #extraer geometrias
    #print(lista)
    list_geo=[]
    for l in lista:
        lgeo=[]
        for v in l:
            #print(v)
            vc=QgsVectorLayer(v,'vector','ogr')
            f1=vc.getFeatures('"DN"=1')
            f=next(f1)
            #print(f)
            g=f.geometry()
            #print(g)
            lgeo.append(g)
        #procesar listas de geometrias
        if len(lgeo)>1:
            #print('mas de una geometria' ,lgeo)
            for e,x in enumerate(lgeo):
                if e==0:
                    #print('area ',str(e),x.area())
                    xs=x
                else:
                    #print('area ',str(e),x.area())
                    if x.area() >xs.area():
                        xs=x
            list_geo.append(xs)
        else:
            #print('solo una geometria',lgeo)
            list_geo.append(lgeo[0])
        #print(' lista geometrias ' ,list_geo)
    #print(epsg)
    lfeatures=[]
    provider=capa.dataProvider()
    for i in list_geo:
        f=QgsFeature()
        f.setFields(capa.fields())
        f.setGeometry(i)
        lfeatures.append(f)
    provider.addFeatures(lfeatures)
    capa.updateFields()

#cargar geometrias con atributos
def cargar_capa_exist_atrib(capa,dic,epsg):
    if capa.crs().authid()==epsg:#pendiente que hacer si crs no coinciden?
        for i in dic:
            tipo=i[0]
            ncampo=i[1]
            valor=i[2]
            lista=dic[i]
            #campos
            campos=capa.fields()
            #extraer geometrias
            list_geo=[]
            for l in lista:
                for v in l:
                    #print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    f=next(f1)
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
            #obtenemos el provedor para editar
            provider=capa.dataProvider()
            enc=False
            for i in campos:
                if i.name()==ncampo:
                    enc=True
            #print(tipo,ncampo,enc)
            if tipo=='campo' and not enc:
                #print('creeando el campo')
                #si no existe el campo lo creamos
                camp = QgsField(ncampo, QVariant.String)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and enc:
                #si se pide crear y el campo ya existe
                ncampo=ncampo+'1'
                camp = QgsField(ncampo, QVariant.String)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and not enc:
                #si se pide crear y el campo ya existe
                camp = QgsField(ncampo, QVariant.String)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            capa.updateFields()
            lfeatures=[]
            for i in list_geo:
                f=QgsFeature()
                f.setFields(capa.fields())
                f.setGeometry(i)
                f.setAttribute(ncampo, valor)
                lfeatures.append(f)
            provider.addFeatures(lfeatures)
    else:
        print('sistema de coordenadas de la capa difernte al de la imagen')

#cargar solo geometria de mayor area con atributos
def cargar_capa_exist_atrib_mayor(capa,dic,epsg):
    if capa.crs().authid()==epsg:#pendiente que hacer si crs no coinciden?
        list_geo=[]
        #print(' dic vector ',dic)
        for i in dic:
            tipo=i[0]
            ncampo=i[1]
            valor=i[2]
            lista=dic[i]
            #print(' lista ' ,lista)
            #campos
            campos=capa.fields()
            #extraer geometrias
            for l in lista:
                lgeo=[]
                for v in l:
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    f=next(f1)
                    g=f.geometry()
                    #print(g)
                    lgeo.append(g)
                #procesar listas de geometrias
                if len(lgeo)>1:
                    #print('mas de una geometria' ,lgeo)
                    for e,x in enumerate(lgeo):
                        if e==0:
                            #print('area ',str(e),x.area())
                            xs=x
                        else:
                            #print('area ',str(e),x.area())
                            if x.area() >xs.area():
                                xs=x
                    list_geo.append(xs)
                else:
                    #print('solo una geometria',lgeo)
                    list_geo.append(lgeo[0])
            #obtenemos el provedor para editar
            provider=capa.dataProvider()
            enc=False
            for i in campos:
                if i.name()==ncampo:
                    enc=True
            #print(tipo,ncampo,enc)
            if tipo=='campo' and not enc:
                #print('creeando el campo')
                #si no existe el campo lo creamos
                camp = QgsField(ncampo, QVariant.String)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and enc:
                #si se pide crear y el campo ya existe
                ncampo=ncampo+'1'
                camp = QgsField(ncampo, QVariant.String)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and not enc:
                #si se pide crear y el campo ya existe
                camp = QgsField(ncampo, QVariant.String)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            capa.updateFields()
            lfeatures=[]
            for i in list_geo:
                f=QgsFeature()
                f.setFields(capa.fields())
                f.setGeometry(i)
                f.setAttribute(ncampo, valor)
                lfeatures.append(f)
            provider.addFeatures(lfeatures)
    else:
        print('sistema de coordenadas de la capa difernte al de la imagen')


#METODOS GDAL CONVERTIR COORDENADAS
#----------------------------------
#CONVERTIR FILA, COLUMNA DE LA IMAGEN A COORDENADAS REALES
def pixel_coord(geoMatrix, col, fil ):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    coorX = (ulX + (col * xDist))
    coorY = (ulY + (fil * yDist))
    return (coorX, coorY)
        
#CONVERTIR COORDENADAS X y Y A POSICION DE LA IMAGEN (FILA, COLUMNA)
def coord_pixel(geoMatrix,x,y):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((y - ulY) / yDist)
    return (pixel, line)
#------------------------------------    
