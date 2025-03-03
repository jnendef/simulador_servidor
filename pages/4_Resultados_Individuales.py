### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64
# import logging

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

from datetime import datetime

diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                "Apartamento_1adulto_calef_gas" : 7,
                "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                "Piso_2adultos_calef_gas_aire_ac" : 12,
                "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
            }

listaDiccioTipo = list(diccioTipo)

tipologiaSB0 = [
            "Apartamento un adulto calefacción eléctrica",
            "Apartamento un adulto calefacción gas",
            "Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
            "Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
            "Piso dos adultos, calefacción gas y AC",
            "Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
        ]

tipologiaSB = {
    6:"Apartamento un adulto calefacción eléctrica",
    7:"Apartamento un adulto calefacción gas",
    9:"Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
    8:"Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
    12:"Piso dos adultos, calefacción gas y AC",
    10:"Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
}

st.markdown("# Resultados")

st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))

st.markdown("## Comunidad: "+str(st.session_state.nComunidad))
st.markdown("## Simulación para el Año: "+str(st.session_state.anyo))
st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)
try:
    agente = Agente_MySql()
    sentenciaSQLusr = "SELECT * FROM leading_db.user WHERE id_energy_community = "+str(st.session_state.idComunidad)+";"
    usuarios = agente.ejecutar(sentenciaSQLusr)

    datosUsr = []

    for i in usuarios:
        sentenciaSQLdatos = "SELECT * FROM leading_db.user_data WHERE id_user = "+str(i[0])+";"
        datos = agente.ejecutar(sentenciaSQLdatos)
        datosUsr.append((i[10],datos))

    listaUsr = []
    diccioUsr = {}
    redListaU = []

    mDatos = np.zeros((len(datosUsr),len(datosUsr[0][1]),4))
    for i in range(len(datosUsr)):
        claveUsr = datosUsr[i][0]
        listaUsr.append(claveUsr)
        if claveUsr not in redListaU:
            redListaU.append(claveUsr)
        diccioUsr[claveUsr] = i
        for j in range(len(datosUsr[i][1])):
            for k,l in enumerate(datosUsr[i][1][j]):
                if k>2:
                    mDatos[i,j,k-3] = l

    mConsumos = [mDatos[i,:,0].sum(0) for i in range(len(datosUsr))]
    mCoef = [mDatos[i,:,1].mean(0) for i in range(len(datosUsr))]
    mReparto = [mDatos[i,:,2].sum(0) for i in range(len(datosUsr))]
    mExcedentes = [mDatos[i,:,3].sum(0) for i in range(len(datosUsr))]

    # Obtenemos los distintos usuarios de la informacion
    redLista = sorted(redListaU)
    redLista2 = []
    posiRedLista = []

    # Se obtienen los valores no repetidos de tipologias
    for j,i in enumerate(redLista):
        if int(i.split("-")[0]) not in redLista2:
            redLista2.append(int(i.split("-")[0]))
            posiRedLista.append(j)
    
    indicesUsr = [str(i)+" "+str(int(j.split("-")[1]))+" "+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]

    st.markdown("### Datos por usuario")
    eleccion0 = st.selectbox("Tipo de Usuario",[tipologiaSB[i] for i in redLista2])
    agente = Agente_MySql()
    sentenciaSQLusr = "SELECT * FROM leading_db.user WHERE id_energy_community = "+str(st.session_state.idComunidad)+";"
    usuarios = agente.ejecutar(sentenciaSQLusr)

    datosUsr = []

    for i in usuarios:
        sentenciaSQLdatos = "SELECT * FROM leading_db.user_data WHERE id_user = "+str(i[0])+";"
        datos = agente.ejecutar(sentenciaSQLdatos)
        datosUsr.append((i[10],datos))

    listaUsr = []
    diccioUsr = {}
    redListaU = []

    mDatos = np.zeros((len(datosUsr),len(datosUsr[0][1]),4))
    for i in range(len(datosUsr)):
        claveUsr = datosUsr[i][0]
        listaUsr.append(claveUsr)
        if claveUsr not in redListaU:
            redListaU.append(claveUsr)
        diccioUsr[claveUsr] = i
        for j in range(len(datosUsr[i][1])):
            for k,l in enumerate(datosUsr[i][1][j]):
                if k>2:
                    mDatos[i,j,k-3] = l

    mConsumos = [mDatos[i,:,0].sum(0) for i in range(len(datosUsr))]
    mCoef = [mDatos[i,:,1].mean(0) for i in range(len(datosUsr))]
    mReparto = [mDatos[i,:,2].sum(0) for i in range(len(datosUsr))]
    mExcedentes = [mDatos[i,:,3].sum(0) for i in range(len(datosUsr))]

    # Obtenemos los distintos usuarios de la informacion
    redLista = sorted(redListaU)
    redLista2 = []
    posiRedLista = []

    # Se obtienen los valores no repetidos de tipologias
    for j,i in enumerate(redLista):
        if int(i.split("-")[0]) not in redLista2:
            redLista2.append(int(i.split("-")[0]))
            posiRedLista.append(j)
    
    indicesUsr = [str(i)+" "+str(int(j.split("-")[1]))+" "+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]
    st.sidebar.write("")
    eleccion = redLista[posiRedLista[redLista2.index(diccioTipo[listaDiccioTipo[tipologiaSB0.index(eleccion0)]])]]

    start_time = st.date_input("fecha inicio",value=datetime(st.session_state.anyo, 1, 1, 0, 0))

    end_time = st.date_input("fecha fin", value=datetime(st.session_state.anyo, 12, 31, 23, 0))

    horasInicio = 24*(start_time-datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    # df = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,2:4],columns=["Reparto","Excedentes"])
    df0 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,0],columns=["Consumo"])
    df1 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,1],columns=["Coeficiente"])
    df2 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,2],columns=["Reparto"])
    df3 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,3],columns=["Excedentes"])
    df4 = df2.join(-1*df3)
    df4 = df4.join((-1*df0))
    st.markdown("### Gráfica de Consumo, Reparto y Excedentes")
    st.bar_chart(df4,x_label="Horas", y_label= "kWh")

    st.write("Consumo Total en el intervalo kWh: {}".format(str(df0.sum()["Consumo"])[:6]))
    st.write("Reparto Total en el intervalo kWh: {}".format(str(df2.sum()["Reparto"])[:6]))
    st.write("Excedente Total en el intervalo kWh: {}".format(str(df3.sum()["Excedentes"])[:6]))
    # st.write(df0.mean())

    st.markdown("### Coeficientes de reparto")
    st.line_chart(df1,x_label="Horas", y_label="%")
    st.write("Coeficiente Promedio en el intervalo en Porcentaje: {}".format(str(df1.mean()["Coeficiente"])[:6]))
    # st.write(df1.mean())

    st.dataframe(df1)

    col1,col2,col3 = st.columns(3)

    with col3:
        st.markdown(
            """<a href="https://endef.com/">
            <img src="data:;base64,{}" width="200">
            </a>""".format(
                base64.b64encode(open("path1.png", "rb").read()).decode()
            ),
            unsafe_allow_html=True,
        )
except:
    pass