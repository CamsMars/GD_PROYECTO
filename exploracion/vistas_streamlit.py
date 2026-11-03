"""Prototipo comparativo que solo lee los mismos tres archivos agregados de la web."""
import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
INDICATORS = json.loads((ROOT / 'exploracion/indicadores.json').read_text())
DATA = json.loads((ROOT / 'docs/datos/distritos.geojson').read_text())
SOURCES = json.loads((ROOT / 'docs/datos/fuentes.json').read_text())
QUESTIONS = json.loads((ROOT / 'docs/datos/preguntas.json').read_text())
DISTRICTS = {f['properties']['distrito_id']: f['properties'] for f in DATA['features']}


def map_html(key):
    # Solo se insertan JSON escapado y código propio. Los rótulos usan textContent.
    template = '''<!doctype html><html lang="es"><head><meta charset="utf-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
    <style>html,body{margin:0;height:100%}#mapa{height:360px;width:100%}</style></head>
    <body><div id="mapa" aria-label="Distritos de Filadelfia"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script><script>
    const data=__DATA__, key=__KEY__;
    const values=data.features.map(f=>f.properties[key]).filter(v=>v!==null).sort((a,b)=>a-b);
    const cuts=[1,2,3,4].map(i=>values[Math.floor(i*values.length/5)]);
    const colors=['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c'];
    const map=L.map('mapa',{scrollWheelZoom:false});
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',maxZoom:19
    }).addTo(map);
    const layer=L.geoJSON(data,{style:f=>{
      const v=f.properties[key]; let i=0;while(i<cuts.length&&v>=cuts[i])i++;
      return {fillColor:v===null?'#ccc':colors[i],fillOpacity:.8,color:'#555',weight:1};
    },onEachFeature:(f,l)=>{
      const popup=document.createElement('div');
      popup.textContent=f.properties.nombre_distrito+' ('+f.properties.distrito_id+'): '+f.properties[key];
      l.bindPopup(popup); l.bindTooltip(document.createTextNode(f.properties.nombre_distrito));
    }}).addTo(map);map.fitBounds(layer.getBounds());
    </script></body></html>'''
    return template.replace('__DATA__', json.dumps(DATA, ensure_ascii=False).replace('<', '\\u003c')).replace('__KEY__', json.dumps(key))


st.set_page_config(page_title='Filadelfia · prueba Streamlit', layout='wide', initial_sidebar_state='collapsed')
st.title('Movilidad y vías en Filadelfia')
st.caption('Prototipo comparativo de Streamlit. Lee la misma instantánea agregada que la web: 18 distritos, sin registros individuales.')
selected = st.selectbox('Indicador', list(INDICATORS), format_func=lambda k: INDICATORS[k]['nombre'], key='indicador')
ind = INDICATORS[selected]
st.caption(ind['unidad'] + (' · PROXY' if ind['proxy'] else ''))
st.iframe(map_html(selected), height=365, alt='Mapa de los 18 distritos de Filadelfia')

did = st.selectbox('Distrito', sorted(DISTRICTS), format_func=lambda k: DISTRICTS[k]['nombre_distrito'] + ' (' + k + ')', key='distrito')
value = DISTRICTS[did][selected]
display = format(value, f",.{ind['decimales']}f") if value is not None else 'sin dato'
st.metric(ind['nombre'] + ' · ' + did, display)

with st.expander('Fuente y cálculo'):
    st.write(ind['calculo'])
    for fid in ind['fuentes']:
        source = SOURCES[fid]
        st.subheader(fid + ' · ' + source['nombre'])
        st.write('Publica: ' + source['publica'])
        st.write('Licencia: ' + source['licencia'])
        st.write('Vigencia: ' + source['periodo'])
        st.write('Fecha de prueba: ' + source['fecha_prueba'])
        st.link_button('Abrir fuente original · ' + fid, source.get('url_publica', source['url']))

st.subheader('Preguntas del sistema')
for pid in ('P1', 'P2', 'P3'):
    question = QUESTIONS[pid]
    st.write(pid + '. ' + question['pregunta'])
    if pid != 'P2':
        st.caption(f"Spearman ρ = {question['rho_spearman']}; p = {question['p_valor']}. No prueba causalidad.")
    else:
        st.caption('El mayor valor corresponde a CTR (48,1) y el menor a LS (2,5) paraderos/km², feed descargado el 2026-11-02.')
st.dataframe(pd.DataFrame(DISTRICTS.values()).sort_values('distrito_id'), hide_index=True)
st.caption('La selección en el mapa abre un rótulo; la ficha de Streamlit se cambia con el selector Distrito. No hay sincronización del clic del mapa con Python en este prototipo.')
