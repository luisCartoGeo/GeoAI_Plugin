import os, glob, random
try:
    import osr
except:
    from osgeo import osr
import processing
from osgeo import gdal
import numpy as np
import tempfile
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QVariant
from qgis.core import (Qgis,QgsField,QgsMapLayer,QgsFeature,QgsRasterLayer,
           QgsGeometry,QgsVectorLayer,QgsRasterBandStats, QgsFeatureRequest,
           QgsCoordinateReferenceSystem,QgsCoordinateTransform,
           QgsVectorLayerEditUtils,edit,QgsEditError)


def inversion_vector(entrada):
    #le asigna signo negativo a la coordenada Y de cada vertice
#    print(entrada)
    if type(entrada)==QgsVectorLayer:
        capa=entrada
    else:
        capa=QgsVectorLayer(ruta,"vtests","ogr")
    with edit(capa):
        for feat in capa.getFeatures():
            idf=feat.id()
            geom = feat.geometry()
            dic={}
            conteo=0
#            print('id de feature ',feat.id())
            for part in geom.parts(): # iterate through all parts of each feature
                for vertex in part.vertices():
#                    print(vertex.y())
                    if vertex.y()<0:
                        break
                    else:
                        QgsVectorLayerEditUtils(capa).\
                        moveVertex(vertex.x(),-vertex.y(),idf,conteo)
                        conteo=conteo+1
    del(capa)
    del(dic)
    
def crearCapaVector(listPuntos,listAreas,dicPuntos,\
                    dicAreas,dicpm,dicarm,proyecto):
    epsg=proyecto.crs().authid()
    uri = "point?crs="+epsg+"&field=id:integer"
    outPoint = QgsVectorLayer(uri, "Puntos_Muestreo",  "memory")
    lfeatures=[]
    provPunto=outPoint.dataProvider()
    if len(listPuntos)>0:
        for g in listPuntos:
            f=QgsFeature()
            f.setFields(outPoint.fields())
            geo=QgsGeometry.fromPointXY(g)
            f.setGeometry(geo)
            lfeatures.append(f)
        provPunto.addFeatures(lfeatures)
    if len(dicPuntos)>0:
        for i in dicPuntos:
            lista=dicPuntos[i]
            for p in lista:
                f=QgsFeature()
                f.setFields(outPoint.fields())
                geo=QgsGeometry.fromPointXY(p)
                f.setGeometry(geo)
                lfeatures.append(f)
        provPunto.addFeatures(lfeatures)
    if len(dicpm[0])>0 or len(dicpm[1])>0:
        lista=dicpm[0]+dicpm[1]
        for g in lista:
            f=QgsFeature()
            f.setFields(outPoint.fields())
            geo=QgsGeometry.fromPointXY(g)
            f.setGeometry(geo)
            lfeatures.append(f)
        provPunto.addFeatures(lfeatures)
    uri = "polygon?crs="+epsg+"&field=id:integer"
    outPolg = QgsVectorLayer(uri, "Areas_Muestreo",  "memory")
    lfeatures=[]
    provPolg=outPolg.dataProvider()
    if len(listAreas)>0:
        for g in listAreas:
            f=QgsFeature()
            f.setFields(outPolg.fields())
            geo=QgsGeometry.fromRect(g)
            f.setGeometry(geo)
            lfeatures.append(f)
        provPolg.addFeatures(lfeatures)
    if len(dicAreas)>0:
        for i in dicAreas:
            lista=dicAreas[i]
            for p in lista:
                f=QgsFeature()
                f.setFields(outPolg.fields())
                geo=QgsGeometry.fromRect(p)
                f.setGeometry(geo)
                lfeatures.append(f)
        provPolg.addFeatures(lfeatures)
    if len(dicarm[1])>0:
        lista=dicarm[1]
        for p in lista:
            f=QgsFeature()
            f.setFields(outPolg.fields())
            geo=QgsGeometry.fromRect(p)
            f.setGeometry(geo)
            lfeatures.append(f)
        provPolg.addFeatures(lfeatures)
    resultado=[]
    if outPoint.featureCount()>0:
        resultado.append(outPoint)
    if outPolg.featureCount()>0:
        resultado.append(outPolg)

    return resultado

def vectorizar(ruta):
#    print(' imagen a vectorizar',ruta)
    r=processing.run("gdal:polygonize", 
    {'INPUT':ruta,\
    'BAND':1,'FIELD':'DN',\
    'EIGHT_CONNECTEDNESS':True,\
    'OUTPUT':'TEMPORARY_OUTPUT'}
    )
    return r['OUTPUT']
    
def puntosArreglo(capa,srci,proyecto,transform):
    sc=capa.crs().authid()
    sci=srci.authid()
    #lista de puntos transformados
    lpixel=[]
    #Iteramos las geometrias
    request = QgsFeatureRequest()
    request.setSubsetOfAttributes([0])
    lfeat=capa.getFeatures()
    print('sistema de coordenadas',sc,sci)
    if not sc == sci:
        sc1=QgsCoordinateReferenceSystem(sc)
        sc2=QgsCoordinateReferenceSystem(sci)
        t=QgsCoordinateTransform(sc1,sc2,proyecto)
        for i in lfeat:
            geo=i.geometry()
            geot=geo.transform(t)
            #print(geot)
            coords=coord_pixel(transform,geot.x(),geot.y())
            lpixel.append([coords[0], coords[1]])
    else:
        for i in lfeat:
            geo=i.geometry()
            coords=coord_pixel(transform,geo.asPoint().x(),geo.asPoint().y())
            lpixel.append([coords[0], coords[1]])
    return np.array(lpixel)
            
def mask_to_imagen(mascara,ruta,nombre,columnas,filas,wkt,geotransform):
    #print(' en utils')
    lnombres=[]
    for e,mi in enumerate(mascara):
        #eliminamos la dimension adicional si viene de un tensor
        if mi.ndim==3:
            mi=mi[0]
        #print('mascara maximo ',np.nanmax(mi))
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

#valores minimo y maximos de todas las bandas
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
    
#minimo y maximo de bandas seleccionadas
def minimo_maximo_bs(imagen,bandas):
    extension=imagen.extent()
    provider= imagen.dataProvider()
    lista=[]
    #determinar minimo y maximo
    for i in bandas:
        stats = provider.bandStatistics(i, QgsRasterBandStats.All, extension)
        lista.append(stats.minimumValue)
        lista.append(stats.maximumValue)
        #print('banda',i+1,min,max)
    minimo=min(lista)
    maximo=max(lista)
    return (minimo,maximo)
    
def crear_capa_salida(lista,epsg,iiface,multi=False):
    iface=iiface
    if len(lista)>0:
        #extraer geometrias
        list_geo=[]
        if multi:
            for l in lista:
                for v in l:
#                    print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    try:
                        f=next(f1)
                    except:
                        iface.messageBar().pushMessage('No se genero segmentos',\
                        'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                        break
#                    print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
        else:
            for v in lista:
#                print('capa ',v)
                vc=QgsVectorLayer(v,'vector','ogr')
                f1=vc.getFeatures('"DN"=1')
#                print(f1)
                try:
                    f=next(f1)
                except:
                    iface.messageBar().pushMessage('No se genero segmentos',\
                    'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                    break
#                print(f)
                g=f.geometry()
                #print(g)
                list_geo.append(g)
#        print(' lista geometrias ' ,list_geo)
#        print(epsg)
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
        
def crear_capa_atrib(dic,epsg,iiface):
    iface=iiface
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
                    try:
                        f=next(f1)
                    except:
                        iface.messageBar().pushMessage('No se genero segmentos',\
                        'No se genero segmentos continua con las otras selecciones', level=Qgis.Warning, duration=7)
                        break
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
            camp = QgsField(ncampo, QVariant.String,'String',254,0)
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

def crear_capa_mayor_atrib(dic,epsg,iiface):
    iface=iiface
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
                    try:
                        f=next(f1)
                    except:
                        iface.messageBar().pushMessage('No se genero segmentos',\
                        'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                        break
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
            camp = QgsField(ncampo, QVariant.String,'String',254,0)
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
        
def crear_capa_mayor_salida(lista,epsg,iiface):
    iface=iiface
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
                try:
                    f=next(f1)
                except:
                    iface.messageBar().pushMessage('No se genero segmentos',\
                    'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                    break
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

def cargar_capa_exist(capa,lista,epsg,iiface,multi=False):
    iface=iiface
    if capa.crs().authid()==epsg:
        #extraer geometrias
        list_geo=[]
        if multi:
            for l in lista:
                for v in l:
                    #print(v)
                    vc=QgsVectorLayer(v,'vector','ogr')
                    f1=vc.getFeatures('"DN"=1')
                    try:
                        f=next(f1)
                    except:
                        iface.messageBar().pushMessage('No se genero segmentos',\
                        'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                        break
                    #print(f)
                    g=f.geometry()
                    #print(g)
                    list_geo.append(g)
        else:
            for v in lista:
                #print(v)
                vc=QgsVectorLayer(v,'vector','ogr')
                f1=vc.getFeatures('"DN"=1')
                try:
                    f=next(f1)
                except:
                    iface.messageBar().pushMessage('No se genero segmentos',\
                    'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                    break
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

def cargar_capa_exist_mayor(capa,lista,epsg,iiface):
    iface=iiface
    #extraer geometrias
    #print(lista)
    list_geo=[]
    for l in lista:
        lgeo=[]
        for v in l:
            #print(v)
            vc=QgsVectorLayer(v,'vector','ogr')
            f1=vc.getFeatures('"DN"=1')
            try:
                f=next(f1)
            except:
                iface.messageBar().pushMessage('No se genero segmentos',\
                'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                break
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
def cargar_capa_exist_atrib(capa,dic,epsg,iiface):
    iface=iiface
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
                    try:
                        f=next(f1)
                    except:
                        iface.messageBar().pushMessage('No se genero segmentos',\
                        'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                        break
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
                camp = QgsField(ncampo, QVariant.String,'String',254)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and enc:
                #si se pide crear y el campo ya existe
                ncampo=ncampo+'1'
                camp = QgsField(ncampo, QVariant.String,'String',254)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and not enc:
                #si se pide crear y el campo ya existe
                camp = QgsField(ncampo, QVariant.String,'String',254)
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
def cargar_capa_exist_atrib_mayor(capa,dic,epsg,iface):
    iface=iiface
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
                    try:
                        f=next(f1)
                    except:
                        iface.messageBar().pushMessage('No se genero segmentos',\
                        'No se genero segmentos intente con otra seleccion', level=Qgis.Warning, duration=7)
                        break
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
                camp = QgsField(ncampo, QVariant.String,'String',254,0)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and enc:
                #si se pide crear y el campo ya existe
                ncampo=ncampo+'1'
                camp = QgsField(ncampo, QVariant.String,'String',254,0)
                provider.addAttributes([camp])
                capa.triggerRepaint()
            elif tipo=='crear' and not enc:
                #si se pide crear y el campo ya existe
                camp = QgsField(ncampo, QVariant.String,'String',254,0)
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
