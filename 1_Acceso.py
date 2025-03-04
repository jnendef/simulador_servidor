### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

#import streamlit_authenticator as stauth
import streamlit as st
import datetime as dt

import os
import logging
from logging.handlers import RotatingFileHandler

import base64
# from streamlit import config

# config.set_option(key="theme.base",value="dark")
path = os.getcwd()
direc = os.path.join(path,"logs")
if not os.path.exists(direc):
    try:
        os.mkdir(direc)
    except Exception as e:
        direc = path

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[RotatingFileHandler(os.path.join(direc,"MENSAJES_PASOS_Output.log"), maxBytes=1000000, backupCount=4)],
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

st.set_page_config("Resultados",layout="centered")

if 'datoscomunidad' not in st.session_state:
    st.session_state.datoscomunidad = {
        "max_participation": 100.0,
        "min_participation": 0.0,
        "energy_poverty": 0.0
    }

if 'comunidades' not in st.session_state:
    st.session_state.comunidades = []
    
if 'procesosCurso' not in st.session_state:
    st.session_state.procesosCurso = ""

if 'usuarios' not in st.session_state:
    st.session_state.usuarios = []

if 'fotovolt' not in st.session_state:
    st.session_state.fotovolt = []

if 'eolicos' not in st.session_state:
    st.session_state.eolicos = []

if 'baterias' not in st.session_state:
    st.session_state.baterias = []

if 'envioInfo' not in st.session_state:
    st.session_state.envioInfo = False

if 'idComunidad' not in st.session_state:
    st.session_state.idComunidad = 0

if 'anyo' not in st.session_state:
    st.session_state.anyo = 2020
    
if 'nComunidad' not in st.session_state:
    st.session_state.nComunidad = ""

if 'saltoSimu' not in st.session_state:
    st.session_state.saltoSimu = False

if 'cupsUsuarios' not in st.session_state:
    st.session_state.cupsUsuarios = {}

if 'usuariosCE' not in st.session_state:
    st.session_state.usuariosCE = []

if 'informe' not in st.session_state:
    st.session_state.informe = {}

st.markdown("# SOFTWARE DE SIMULACIÓN DE COMUNIDADES ENERGÉTICAS")
st.markdown("### Versión 1.1.0 ("+dt.date(2025,3,3).__format__('%d %b %Y, %I:%M%p')+")")
st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))
st.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="300">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)
st.write("")
st.write("")
st.write("")