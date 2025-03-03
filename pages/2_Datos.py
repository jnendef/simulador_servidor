### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt
from geopy.geocoders import Nominatim 
from string import punctuation

import base64
# import logging

import numpy as np
import pandas as pd

from pages.scripts.envios import envioDatos
from pages.scripts.calculos import calcula2

# definicion de las funciones
def borrar(campo,valores):
    # st.session_state[campo].remove(valores)
    if len(st.session_state[campo])>0:
        st.session_state[campo].pop(-1)
    else:
        pass
    return 

def resetear(campo):
    st.session_state[campo] = []
    return

def actualizarValores(AddElem,listaElem,infoElem):
    if AddElem:
        infoElem.append(listaElem)

    return infoElem

def comprobarStrings(mensaje):
    return any(caracter in punctuation for caracter in mensaje)

def camposDataframe(concepto, datos, columnas, add = True):
    
    st.session_state[concepto] = actualizarValores(add,datos,st.session_state[concepto])
    
    info = st.session_state[concepto]
    df = pd.DataFrame(info, columns=columnas)
    return df

#Creacion de un localizador de coordenadas
geolocator = Nominatim(user_agent="aplication")
if 'localizador' not in st.session_state:
    st.session_state.localizador = geolocator.geocode("Zaragoza")
    
# Comienza la pagina
st.title("DATOS")

st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))
st.info("Se deben rellenar todos los campos requeridos antes de la subida de datos y la simulación. Prestar atención a los avisos en cada pestaña")

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8= st.tabs(["Comunidad", "Fotovoltaicos","Eólicos", "Baterías", "Usuarios","Coeficientes", "Confirmación", "Simular"])

ce = False
fv = False
eo = False
gen = False
bt = False
usr = False
sub = False

location = None

with tab1:
    st.info("Nota aclaratoria: Obligatorio cumplimentar Nombre de la comunidad y Ubicación. No emplear signos de puntuación")
    st.header("Comunidad")
    st.markdown("### Datos Generales")
    nombreCE = st.text_input("Nombre de la comunidad *",help="Poner el nombre que tiene la comunidad.")
    ubicacion = st.text_input("Ubicación *",help="Poner el nombre de la ciudad o pueblo. Por ejemplo: Zaragoza.")
    coste = 100000.00
    amortizacion = 1000.00

    deshabilitadoCE = True
    gralComu = None
    if nombreCE=="":
        st.write("Falta el nombre")
    elif comprobarStrings(nombreCE):
        st.warning("Nombre no válido. Quitar signos de puntuación.")
    elif comprobarStrings(ubicacion):
        st.warning("Ubicación no válida. Quitar signos de puntuación.")
    elif ubicacion == "":
        st.write("Falta la ubicación")
    else:
        deshabilitadoCE = False
        gralComu = (nombreCE,ubicacion,coste,amortizacion)

    comunidadEnerg = {}
    colums = ("Nombre","Ubicacion","Coste","Amortizacion")
    addce = st.button("Crea comunidad",type="primary", disabled = deshabilitadoCE)
    dfComu = pd.DataFrame([])
    if addce:
        st.info("Datos cumplimentados")
        st.session_state.nComunidad = nombreCE
        st.session_state.saltoSimu = False
        st.success('Ya puedes pasar a la siguiente pestaña: Fotovoltaicos.', icon="✅")
        try:
            st.session_state.localizador = geolocator.geocode(ubicacion)
        except:
            pass
    if gralComu != None:
        dfComu = camposDataframe("comunidades",gralComu,colums,addce)
        conceptos = ["name", "location", "inst_cost", "inst_monthly_fee"]
        for i,j in zip(conceptos,gralComu):
            comunidadEnerg[i] = j
        comunidadEnerg["id_administrator"] = 1
        ce = True

    

with tab2:
    st.info("Nota aclaratoria: Si hay eólica y no hay FV, puedes pasar al definir la generación eólica.")
    tipologiasFV = {
        "Monocristalino":1,
        "Policristalino":2
    }
    location = st.session_state.localizador
    st.header("Generadores FV")
    st.markdown("### Formulario de incorporación generador FV")
    descFV = st.text_input("Descripción de los generadores FV", value = "FV1",help="Poner una breve descripción para diferenciarlo de otros generadores, ya que puedes hacer la simulación con más de una planta fotovoltaica. No usar signos de puntuación.", disabled= not ce)
 
    latiFV = st.number_input("Latitud instalación", help = "Puede obtener las coordenadas de google maps haciendo clic con el botón derecho en la ubicación de los paneles", disabled= not ce, value = location.latitude, max_value=90.0, min_value=-90.0,format="%2.6f")
    longFV = st.number_input("Longitud instalación", help = "Puede obtener las coordenadas de google maps haciendo clic con el botón derecho en la ubicación de los paneles", disabled= not ce, value = location.longitude, max_value=180.0, min_value=-180.0, format="%2.6f")
    
    df = pd.DataFrame(
        {
            "col1": np.array([latiFV]),
            "col2": np.array([longFV]),
        }
    )

    st.map(df, latitude="col1", longitude="col2")
    nModulos = 10
    pPicoFV = st.number_input("Potencia pico total FV [kW]",help="Poner la potencia pico de toda la planta fotovoltaica situada en las coordenadas que se han indicado.",min_value=0.0, disabled= not ce)
    tipoMod = "Monocristalino"
    azimuth = st.number_input("Azimuth en grados[-90 E, 0 S, 90 O, 180 N]", disabled= not ce,min_value=-90,max_value=180,value=0,step=1)
    inclinacion = st.number_input("Inclinación en grados [0 horizontal, 90 vertical]", disabled= not ce,min_value=0,max_value=90,value=30,step=1)

    deshabilitadoFV = True

    if descFV=="":
        st.warning("Falta la descripción")
    elif pPicoFV == 0.0:
        st.warning("Falta la potencia pico")
    elif comprobarStrings(descFV):
        st.warning("Descripción no válida. Quitar signos de puntuación.")
    else:
        deshabilitadoFV = False
        st.info("Ya puedes añadir la planta fotovoltaica. Asegúrate de que los datos son correctos antes de pasar al siguiente campo.")

    AddGenFv = st.button("Añade Fotovoltaica",type="primary", disabled= (not ce or deshabilitadoFV))

    aux = (descFV,latiFV,longFV,nModulos,pPicoFV,tipologiasFV[tipoMod],int(azimuth),int(inclinacion))
    colums = ("Descripcion","latitud","longitud","cantidad","Wp Total","Tipo","azimuth","inclinacion")

    dfFV = camposDataframe("fotovolt",aux,colums,AddGenFv)

    if len(st.session_state["fotovolt"]) == 0:
        st.write("No hay planta generadora FV")
    else:
        fv = True
        st.success("Hay al menos una planta generadora FV en la comunidad. Asegúrate de que los datos son correctos antes de pasar al siguiente campo. Una vez revisado, puedes pasar a la siguiente pestaña: Eólicos.")

    numeroFV = 0.0
    infoFV = st.session_state["fotovolt"]
    for i in infoFV:
        numeroFV += i[4]
    st.write("Total potencia FV instalada: ",numeroFV)
    st.dataframe(dfFV)

    if st.button("Borrar planta FV"):
        borrar("fotovolt",aux)
        st.rerun()


with tab3:
    location = st.session_state.localizador
    st.info("Nota aclaratoria: Si hay FV y no hay eólica, puedes pasar a la siguiente pestaña")
    st.header("Generadores eólicos")
    st.markdown("### Formulario de incorporación generador Eólico")
    descEo = st.text_input("Descripción de los generadores eólicos", value = "EO1",help="Poner una breve descripción para diferenciarlo de otros generadores, ya que puedes hacer la simulación con más de un generador eólico. No usar signos de puntuación.", disabled= not ce)
    latiEo = st.number_input("Latitud eólico", help = "Puede obtener las coordenadas de google maps haciendo clic con el botón derecho en la ubicación de los aerogeneradores", disabled= not ce,value = location.latitude,max_value=90.0,min_value=-90.0,format="%2.6f")
    longEo = st.number_input("Longitud eólico", help = "Puede obtener las coordenadas de google maps haciendo clic con el botón derecho en la ubicación de los aerogeneradores", disabled= not ce,value = location.longitude,max_value=180.0,min_value=-180.0,format="%2.6f")
    df = pd.DataFrame(
        {
            "col1": np.array([latiEo]),
            "col2": np.array([longEo]),
        }
    )

    st.map(df, latitude="col1", longitude="col2")
    pPicoEo = st.number_input("Potencia pico eólico [kW]",help="Potencia pico del aerogenerador.", disabled= not ce, min_value= 0.0)

    deshabilitadoEO = True

    if descEo=="":
        st.warning("Falta la descripción")
    elif comprobarStrings(descEo):
        st.warning("Descripción no válida. Quitar signos de puntuación.")
    elif pPicoEo == 0.0:
        st.warning("Falta la potencia pico")
    else:
        deshabilitadoEO = False
        st.info("Ya puedes añadir el aerogenerador. Asegúrate de que los datos son correctos antes de pasar al siguiente campo")

    AddGenEo = st.button("Añade Eólica",type="primary", disabled= (not ce or deshabilitadoEO))

    aux = (descEo,latiEo,longEo,pPicoEo)
    colums = ("Descripcion","latitud","longitud","Wp")

    dfEO = camposDataframe("eolicos",aux,colums,AddGenEo)

    if len(st.session_state["eolicos"]) == 0:
        st.write("No hay planta generadora eólica")
    else:
        eo = True
        st.success("Hay al menos un aerogenerador en la comunidad. Asegúrate de que los datos son correctos antes de pasar al siguiente campo. Una vez revisado puedes pasar a la siguiente pestaña: Baterías.")

    numeroEO = 0.0
    infoEo = st.session_state["eolicos"]
    for i in infoEo:
        numeroEO += i[3]
    st.write("Total potencia eólica instalada: ",numeroEO)
    st.dataframe(dfEO)

    if st.button("Borrar eólicos"):
        borrar("eolicos",aux)
        st.rerun()

with tab4:
    st.info("Si no hay baterías, puedes pasar al apartado de usuarios")
    if fv or eo:
        gen = True
    tipologiasBat = {
        "Litio":1,
        "Otras":2
    }
    st.header("Baterías")
    st.markdown("### Descripción de las Baterías")
    descBat = st.text_input("Descripción sobre las baterías", value = "BAT1", help="Poner una breve descripción para diferenciar las baterías que quiere poner entre sí, ya que puedes hacer la simulación con más de una batería. No usar signos de puntuación.",disabled= not gen)
    tipoBat = "Litio"
    st.markdown("### Características técnicas")

    voltajeBat =   220
    capacidadBat = st.number_input("Capacidad de las baterías [kWh]", help = "Capacidad nominal de las baterías en kWh" , value = 0.0, disabled= not gen, min_value=0.0)
    cargaMaxBat =  capacidadBat
    cargaMinBat =  0.1*capacidadBat
    arranquedBat = st.number_input("Potencia [kW]", help = "Potencia de las baterías que se obtiene de multiplicar la tensión nominal y la intensidad nominal. Si no tiene claros estos valores, poner la mitad del valor de la capacidad." ,disabled= not gen, value = capacidadBat/2.,min_value = 0.0)
    descMaxBat =  arranquedBat*1.0

    deshabilitadoBat = True

    if descBat=="":
        st.warning("Falta la descripción")
    elif comprobarStrings(descBat):
        st.warning("Descripción no válida. Quitar signos de puntuación.")
    elif tipoBat == "":
        st.warning("Falta el tipo de batería")
    elif capacidadBat == 0.0:
        st.warning("Falta la capacidad de la batería")
    elif arranquedBat == 0.0:
        st.write("Falta la potencia")
    else:
        deshabilitadoBat = False
        st.info("Ya puedes añadir el almacenamiento. Asegúrate de que los datos son correctos antes de pasar al siguiente campo.")

    AddAlmBat = st.button("Añade Almacenamiento",type="primary", disabled= (not gen or deshabilitadoBat))

    aux = (descBat,tipologiasBat[tipoBat],voltajeBat,capacidadBat,cargaMaxBat,cargaMinBat,arranquedBat,descMaxBat)
    colums = ("Descripcion","tipo","Voltaje","Capacidad","Carga Max","Carga min","Potencia","Descarga Max")

    dfBat = camposDataframe("baterias",aux,colums,AddAlmBat)

    if len(st.session_state["baterias"]) == 0:
        st.write("No hay almacenamiento")
    else:
        bt = True
        st.success("Hay almacenamiento en la comunidad. Asegúrate de que los datos son correctos. Una vez revisados, puedes pasar a la siguiente pestaña: Usuarios.")
    numeroBat = 0.0
    infBat = st.session_state["baterias"]
    for i in infBat:
        numeroBat += float(i[3])
    st.write("Total de almacenamiento instalado: ",numeroBat)
    st.dataframe(dfBat)

    if st.button("Borrar"):
        borrar("baterias",aux)
        st.rerun()

with tab5:
    st.info("Nota aclaratoria: una vez estén todos los usuarios, puede pasar a la siguiente parte de subida de datos")
    diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                    "Apartamento_1adulto_calef_gas" : 7,
                    "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                    "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                    "Piso_2adultos_calef_gas_aire_ac" : 12,
                    "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
    }
    tipologias = [
        "Apartamento_1adulto_calef_electrica",
        "Apartamento_1adulto_calef_gas",
        "Piso_2adultos_1-2niños_calef_electrica_aire_ac",
        "Piso_2adultos_1-2niños_calef_gas_aire_ac",
        "Piso_2adultos_calef_gas_aire_ac",
        "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac"]
    
    tipologiaSB = [
        "Apartamento un adulto calefacción eléctrica",
        "Apartamento un adulto calefacción gas",
        "Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
        "Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
        "Piso dos adultos, calefacción gas y AC",
        "Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
    ]

    st.header("Usuarios")
    tipoUser = st.selectbox("Tipología de usuario",tipologiaSB, help="Seleccionar una tipología de vivienda para los tipos de miembros de la comunidad." , disabled= not gen)
    cantUser = st.number_input("Cantidad de usuarios con esta tipología", help="Indicar cuántos usuarios hay con la tipología seleccionada.",disabled= not gen, min_value=1,step=1)

    AddUser = st.button("Añade Usuarios",type="primary", disabled= not gen)

    aux = [tipologias[tipologiaSB.index(tipoUser)],cantUser]

    dfUs = camposDataframe("usuarios",aux,("Tipo de usuario","cantidad"),AddUser)

    if len(st.session_state["usuarios"]) == 0:
        st.warning("No hay usuarios")
    else:
        usr = True
        st.success("Hay usuarios en la comunidad. Asegúrate de que están incluidos todos los usuarios y de que los datos son correctos antes de pasar a la siguiente pestaña: Coeficientes.")

    numeroUsers = 0
    infoUsers = st.session_state["usuarios"]
    for i in infoUsers:
        numeroUsers += i[1]
    st.write("Total usuarios: ",numeroUsers)
    st.dataframe(dfUs)

    if st.button("Borrar usuarios"):
        borrar("usuarios",aux)
        st.rerun()

with tab6:
    st.info("Nota aclaratoria: Puede dejar los coeficientes de reparto como están o modificar los valores máximo, mínimo y de pobreza energética para calcular el reparto de la energía producida. Si todo está correcto, puede pasar a la siguiente pestaña: Confirmación.")
    st.header("Coeficientes de reparto")
    try:
        valorAux = 100.0/numeroUsers
    except ZeroDivisionError:
        valorAux = 50.0
    coefMax = st.number_input("Coeficiente máximo", min_value = valorAux, max_value = 100.0,value=100.0,step=1.0)
    coefmin = st.number_input("Coeficiente mínimo", min_value = 0.0, max_value = valorAux,value=0.0,step=1.0)
    pobrezaE = st.number_input("Porcentaje para pobreza energética",min_value=0.0, max_value=100.0,step=1.0)

    comunidadEnerg["max_participation"]=coefMax
    comunidadEnerg["min_participation"]=coefmin
    comunidadEnerg["energy_poverty"]=pobrezaE

with tab7:
    st.info("Nota aclaratoria: La simulación sólo se ejecutará correctamente tras haber confirmado los datos que se encuentran resumidos en esta pestaña haciendo click en el botón Confirmar Datos del final de esta página")
    st.header("Datos finales")
    try:
        st.markdown("""### Nombre de la comunidad: {}""".format(str(st.session_state.comunidades[-1][0])))
    except:
        st.write()
    st.write("")
    try:
        st.markdown("""### Localización de la comunidad: {}""".format(str(st.session_state.comunidades[-1][1])))
    except:
        st.write()
    

    conceptos= ["description", "latitude", "longitude", "pv_num_modules", "pv_peak_power", "pv_module_type","pv_module_orientation","pv_module_tilt"]

    # Diccionarios de las instalaciones fotovoltaicas
    fotovoltaicos = []
    auxFV = st.session_state["fotovolt"].copy()
    try:
        if any(auxFV):
            for i in auxFV:
                diccioFVaux = {}
                for j,k in zip(conceptos,i):
                    diccioFVaux[j] = k
                fotovoltaicos.append(diccioFVaux)
    except:
        st.write("No hay generadores fotovoltaicos asignados")

    # Diccionarios de las instalaciones eolicas
    conceptos= ["description", "latitude", "longitude", "wind_peak_power"]
    eolicos = []
    try:
        auxEO = st.session_state["eolicos"].copy()
        if any(auxFV):
            for i in auxEO:
                diccioEOaux = {}
                for j,k in zip(conceptos,i):
                    diccioEOaux[j] = k
                eolicos.append(diccioEOaux)

    except:
        st.write("No hay generadores eólicos asignados")

    # Diccionarios de las baterias
    conceptos= ["ds_storage_system","id_battery_type", "voltage", "nominal_capacity", "max_limit", "min_limit", "init_capacity", "max_hour_discharge"]
    baterias = []
    try:
        auxBat = st.session_state["baterias"].copy()
        if any(auxBat):
            for i in auxBat:
                diccioBataux = {}
                for j,k in zip(conceptos,i):
                    diccioBataux[j] = k
                baterias.append(diccioBataux)
    except:
        st.write("No hay baterías asignadas")

    # Diccionarios de los usuarios
    conceptos = ["id_consumer_profile"]
    usuarios = []
    try:
        auxUser = st.session_state["usuarios"].copy()
        if any(auxUser):
            for us in auxUser:
                valor = diccioTipo[us[0]]
                for i in range(us[1]):
                    usuarios.append(valor)
    except:
        st.write("No hay usuarios asignados")


    st.header("Resumen de datos")

    st.write("Generadores FV:")
    st.dataframe(dfFV)
    
    dfaux = pd.DataFrame(
        {
            "col1": dfFV["latitud"],
            "col2": dfFV["longitud"],
        }
    )

    st.map(dfaux, latitude="col1", longitude="col2", color = [0.2, 0.2, 0.5, 0.5])

    st.write("Generadores eólicos:")
    st.dataframe(dfEO)

    
    dfaux2 = pd.DataFrame(
        {
            "col1": dfEO["latitud"],
            "col2": dfEO["longitud"],
        }
    )

    st.map(dfaux2, latitude="col1", longitude="col2", color = [0.2, 0.5, 0.2, 0.5])
    st.write("Almacenamiento:")
    st.dataframe(dfBat)

    st.write("Usuarios:")
    st.dataframe(dfUs)

    idComunidad = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        # Reset button
        if st.button("Resetear todo"):
            st.session_state.clear()  # Rerun the script
            st.session_state["authentication_status"] = None
            st.rerun(scope="app")
    with col3:
        if st.button("Confirmar Datos",type="primary", disabled= not usr):
            currentDateTime = dt.datetime.now()
            start = currentDateTime.strftime('%Y-%m-%d %H:%M:%S')
            st.session_state.procesosCurso = start

            if any(comunidadEnerg) and (any(fotovoltaicos) or any(eolicos)) and any(usuarios):
                try:
                    st.session_state.datoscomunidad["max_participation"]=comunidadEnerg["max_participation"]
                    st.session_state.datoscomunidad["min_participation"]=comunidadEnerg["min_participation"]
                    st.session_state.datoscomunidad["energy_poverty"]=comunidadEnerg["energy_poverty"]
                    idComunidad,start = envioDatos(comunidadEnerg,fotovoltaicos,eolicos,baterias,usuarios,start)
                    st.session_state.idComunidad = idComunidad
                    st.session_state.informe["cantidadFV"] = numeroFV
                    st.session_state.informe["cantidadEO"] = numeroEO
                    st.session_state.informe["cantidadBat"] = numeroBat
                    st.session_state.informe["cantidadUsers"] = numeroUsers

                    st.write("Exportación realizada, ID de la comunidad: ",idComunidad)
                except Exception as e:
                    st.write("Error en el envío")
                    st.write(e)
            sub = True
            st.session_state.envioInfo = True
    if sub:
        st.success("Puede pasar a la pestaña de simulación para realizar la simulación de producción, consumos y reparto energético para el año que seleccione.")
with tab8:

    st.info("Nota aclaratoria: La simulación sólo se debe ejecutar tras haber exportado los datos. Debe seleccionar el año del que quiere realizar la simulación y luego hacer click en el botón Simular.")
    try:
        st.markdown("""## Nombre de la comunidad: {}""".format(str(st.session_state.comunidades[-1][0])))
        simulable = True
    except:
        st.write()
        simulable = False

    date_year = st.number_input("Año de la simulación", disabled= not simulable and not st.session_state.envioInfo, value = int(dt.datetime.now().year), min_value=2020,step=1)
    

    if 'run_button' in st.session_state and st.session_state.run_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    if st.button('Simular', disabled=((not any(st.session_state.procesosCurso)) or st.session_state.saltoSimu or st.session_state.running), type="primary", key='run_button'):
        exitoSim = calcula2(st.session_state.procesosCurso,date_year)
        st.session_state.anyo = date_year
        st.session_state.saltoSimu = True
        if exitoSim:
            st.success("Puede ver los resultados yendo a los enlaces de Resultados Generales e Individuales de la barra lateral.")
            st.write("Momento de inicio del proceso: ", st.session_state.procesosCurso)