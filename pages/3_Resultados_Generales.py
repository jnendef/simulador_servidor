### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64
# import logging

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

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

st.markdown("# Análisis de Comunidad")


meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
st.write("Zaragoza, "+str(dt.datetime.today().day)+" de "+meses[dt.datetime.today().month-1]+" de "+str(dt.datetime.today().year))

st.markdown("## Comunidad "+str(st.session_state.nComunidad))

st.markdown("Las comunidades energéticas son entidades jurídicas basadas en la participación abierta y voluntaria, autónomas y efectivamente controladas por socios o miembros que están situados en las proximidades de los proyectos de energías renovables que sean propiedad de dichas entidades jurídicas y que estas hayan desarrollado, cuyos socios o miembros sean personas físicas, pymes o autoridades locales, incluidos los municipios y cuya finalidad primordial sea proporcionar beneficios medioambientales, económicos o sociales a sus socios o miembros o a las zonas locales donde operan, en lugar de ganancias financieras.")

st.markdown("## Simulación para el año "+str(st.session_state.anyo))
st.markdown("Los resultados de este informe son previsiones que se realizan en base a consumos tipo que no tienen por qué coincidir con el consumo real de los usuarios. Es una aproximación que sirve de orientación para poder tomar una decisión respecto a la comunidad.")
st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

if st.session_state.idComunidad>0:
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
    
    indicesUsr = [str(i)+"-"+str(int(j.split("-")[1]))+" "+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]
    st.sidebar.write("")
    try:
        st.markdown("### Consumos Totales Anuales Por Usuario")
        texto = "La comunidad de "+str(st.session_state.nComunidad)
        if st.session_state.informe["cantidadFV"] > 0.0:
            texto = texto + " cuenta con una potencia fotovoltaica instalada de "+str(st.session_state.informe["cantidadFV"])+"kW"
        if st.session_state.informe["cantidadEO"] > 0.0:
            texto = texto + ", la potencia eólica instalada es "+str(st.session_state.informe["cantidadEO"])+"kW"
        if st.session_state.informe["cantidadBat"] > 0.0:
            texto = texto + " y "+str(st.session_state.informe["cantidadBat"])+"kWh de almacenamiento"
        texto += "."

        st.markdown(texto)
        st.markdown(" En el siguiente gráfico de barras se pueden apreciar los valores de los consumos, reparto y excedentes, en valores promedio, para cada usuario de la comunidad, en kWh, para el año especificado en la simulación("+str(st.session_state.anyo)+").")
        dfCon = pd.DataFrame(mConsumos,index=indicesUsr,columns=["Consumos [kWh]"])
        dfRep = pd.DataFrame(mReparto,index=indicesUsr,columns=["Reparto [kWh]"])
        dfExc = pd.DataFrame(mExcedentes,index=indicesUsr,columns=["Excedentes [kWh]"])
        dfF = dfExc.join(dfRep)
        dfF = dfF.join(dfCon)
        dfF2 = dfF.copy()
        dfF2.index = [i for i in range(len(mConsumos))]

        st.markdown("")
        st.markdown("*Gráfico 1. Valores promedios de consumo, reparto y excedentes*")
        st.bar_chart(dfF2, horizontal = False, height = 500, width = 500, stack=False,color= ["#00C42D", "#2645CB", "#FFC400"], x_label="Usuarios", y_label="kWh")

        st.markdown("De forma tabulada, los valores promedios anuales serían los indicados a continuación:")
        st.data_editor(
                        dfF,
                        column_config={
                            "_index": st.column_config.Column(
                                "Usuarios",
                                width="medium",
                                required=True,
                            )
                        },
                        hide_index=False,
                        height = 43 * len(mConsumos),
                    )
        st.markdown("*Tabla 1. Valores promedios de consumo, reparto y excedentes*")

        st.markdown("### Coeficientes de reparto")
        st.markdown("Los coeficientes de reparto son los factores por los que se multiplica la producción para obtener el reparto de la energía producida. La elección del valor de estos coeficientes es decisión de la comunidad energética y se debe aceptar por parte de los miembros de ésta.")
        st.markdown("En esta simulación se proponen los posibles coeficientes de reparto basando los cálculos en los consumos de los usuarios de la comunidad y distribuyendo la energía producida proporcionalmente a estos consumos. Con este cálculo se busca que haya el mínimo de excedente vertido a red porque permite sacar el mayor rendimiento a la producción.")
        st.markdown("El coeficiente máximo seleccionado para la simulación es **"+str(st.session_state.datoscomunidad["max_participation"])+"%** que consiste en el valor máximo que puede tomar en la simulación el coeficiente de reparto para un único usuario. Se puede poner esta restricción para el caso de que un usuario tenga un consumo muy superior y evitar que acapare toda la producción.")
        st.markdown("El coeficiente mínimo seleccionado para la simulación es **"+str(st.session_state.datoscomunidad["min_participation"])+"%** que consiste en el valor mínimo que puede tomar en la simulación el coeficiente de reparto para un único usuario. Se puede poner esta restricción para evitar que un usuario tenga muy poca participación debido a tener poco consumo.")
        st.markdown("El porcentaje dedicado a pobreza energética es **"+str(st.session_state.datoscomunidad["energy_poverty"])+"%** que es el porcentaje de energía que se dedicará para los casos seleccionados.")

        dfCoef = pd.DataFrame(mCoef,index=indicesUsr,columns=["%"])
        
        dfCoef2 = dfCoef.copy()
        dfCoef2.index = [i for i in range(len(mConsumos))]
        st.markdown("*Gráfico 2. Valores promedios anuales de coeficientes de reparto por usuario*")
        st.bar_chart(dfCoef2, horizontal = False, height = 500, width = 500, x_label="Usuario", y_label="%",)

        st.markdown("De forma tabulada, los valores promedios anuales serían los indicados a continuación:")

        st.data_editor(
                        dfCoef,
                        column_config={
                            "_index": st.column_config.Column(
                                "Usuarios",
                                width="large",
                                required=True,
                            ),
                            "%": st.column_config.Column(
                                "Porcentaje",
                                width="medium",
                                required=True,
                            )
                        },
                        hide_index=False,
                        height = 43 * len(mConsumos),
                    )
        st.markdown("*Tabla 2. Valores promedios anuales de coeficientes de reparto por usuario*")

        st.write("\n")
        st.write("\n")
        st.markdown("###### Responsabilidades")
        st.markdown("###### Esta información es facilitada por endef mediante el uso de software libre desarrollado para el apoyo a las comunidades energéticas. Esta app es una herramienta informática diseñada para realizar simulaciones con fines informativos y educativos. Si bien se han implementado metodologías rigurosas para mejorar la precisión de los resultados, Endef no garantiza la exactitud ni idoneidad de los datos generados.")

        st.markdown("###### El usuario reconoce y acepta que:")

        st.markdown("###### - Uso Bajo Responsabilidad Propia: El usuario es el único responsable de la aplicación de los resultados.")

        st.markdown("###### - Limitación de Responsabilidad: En ningún caso Endef será responsable de daños directos, indirectos, incidentales, especiales o consecuentes, incluyendo, pero sin limitarse a, pérdidas económicas, interrupciones del negocio, daños a equipos o cualquier otro perjuicio derivado del uso o incapacidad de uso del software.")
        st.markdown("###### Al utilizar esta app, el usuario acepta esta exención de responsabilidad en su totalidad.")
        
        col1,col2,col3 = st.columns(3)

        with col1:
            st.write("Zaragoza, "+str(dt.datetime.today().day)+" de "+meses[dt.datetime.today().month-1]+" de "+str(dt.datetime.today().year))

        with col3:
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
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
    