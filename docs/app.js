// Pagina del lago de datos de Filadelfia
// Lee los archivos de la carpeta datos/ que genera construir_lago.py

const INDICADORES = {
  reportes_viales_x1000hab: {
    nombre: "Reportes viales al 311",
    unidad: "por 1.000 hab. al año",
    decimales: 1,
    proxy: true,
    fuentes: ["F02", "F05", "F06", "F01"],
    calculo: "Solicitudes viales al 311 de 2020 a 2024 en el distrito, divididas por 5 años y por la población, por 1.000."
  },
  siniestros_graves_x1000hab: {
    nombre: "Siniestros graves",
    unidad: "por 1.000 hab. al año",
    decimales: 2,
    proxy: true,
    fuentes: ["F03", "F05", "F06", "F01"],
    calculo: "Siniestros con al menos un muerto o herido grave de 2020 a 2024, divididos por 5 años y por la población, por 1.000."
  },
  paraderos_x_km2: {
    nombre: "Paraderos de SEPTA",
    unidad: "por km²",
    decimales: 1,
    proxy: false,
    fuentes: ["F04", "F01"],
    calculo: "Paraderos del feed descargado el 2026-11-02 dentro del distrito, divididos por su área en km². No representa la red histórica de 2020–2024."
  },
  mediana_dias_atencion: {
    nombre: "Días para atender una solicitud vial",
    unidad: "días (mediana)",
    decimales: 0,
    proxy: false,
    fuentes: ["F02", "F01"],
    calculo: "Mediana de los días entre el reporte y el cierre de las solicitudes viales cerradas, 2020-2024."
  },
  proxy_ingreso_mediano_hogar: {
    nombre: "Ingreso del hogar",
    unidad: "USD al año",
    decimales: 0,
    proxy: true,
    fuentes: ["F05", "F06"],
    calculo: "Promedio de los ingresos medianos de los census tracts del distrito, ponderado por población. No es la mediana real del distrito."
  },
  poblacion_total: {
    nombre: "Población",
    unidad: "habitantes",
    decimales: 0,
    proxy: true,
    fuentes: ["F05", "F06"],
    calculo: "Suma de la población de los census tracts asignados al distrito por su punto interno."
  }
};

const COLORES = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"];
const POBLACION_BAJA = 10000;

let distritos, fuentes, preguntas, mapa, capa;

function numero(valor, decimales) {
  if (valor === null || valor === undefined) return "sin dato";
  return Number(valor).toLocaleString("es-CO", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
}

function botonFuente(ids, calculo) {
  const datos = encodeURIComponent(JSON.stringify({ ids: ids, calculo: calculo || "" }));
  return `<button class="btn-fuente" data-fuente="${datos}">Fuente</button>`;
}

function etiquetaProxy(ind) {
  return ind.proxy ? '<span class="proxy">PROXY</span>' : "";
}

// ventana de fuentes
function abrirFuente(datos) {
  let html = "";
  if (datos.calculo) html += `<div class="bloque"><h4>Cómo se calcula</h4>${datos.calculo}</div>`;
  for (const id of datos.ids) {
    const f = fuentes[id] || {};
    html += `<div class="bloque"><h4>${id} - ${f.nombre || ""}</h4>
      Publica: ${f.publica || "-"}<br>
      ${f.url ? `<a href="${f.url}" target="_blank" rel="noopener noreferrer">Abrir fuente original</a><br>` : ""}
      Licencia: ${f.licencia || "-"}<br>
      Vigencia: ${f.periodo || "-"} (actualización ${(f.actualizacion || "-").toLowerCase()})<br>
      Fecha en que la probamos: ${f.fecha_prueba || "-"}</div>`;
  }
  document.getElementById("contenido-fuente").innerHTML = html;
  document.getElementById("dialogo-fuente").showModal();
}

document.addEventListener("click", function (e) {
  if (e.target.classList.contains("btn-fuente")) {
    abrirFuente(JSON.parse(decodeURIComponent(e.target.dataset.fuente)));
  }
});
document.getElementById("cerrar-fuente").addEventListener("click", function () {
  document.getElementById("dialogo-fuente").close();
});

// mapa
function cortes(valores) {
  // 5 grupos con la misma cantidad de distritos (quintiles)
  const orden = valores.filter(v => v !== null).sort((a, b) => a - b);
  const c = [];
  for (let i = 1; i < 5; i++) c.push(orden[Math.floor(i * orden.length / 5)]);
  return c;
}

function colorPara(valor, c) {
  if (valor === null || valor === undefined) return "#cccccc";
  let i = 0;
  while (i < c.length && valor >= c[i]) i++;
  return COLORES[i];
}

function pintarMapa() {
  const clave = document.getElementById("indicador").value;
  const ind = INDICADORES[clave];
  const valores = distritos.features.map(f => f.properties[clave]);
  const c = cortes(valores);

  document.getElementById("desc-indicador").innerHTML =
    `${ind.nombre}, ${ind.unidad} ${etiquetaProxy(ind)} ${botonFuente(ind.fuentes, ind.calculo)}`;

  capa.setStyle(function (f) {
    return { fillColor: colorPara(f.properties[clave], c), fillOpacity: 0.8, color: "#555", weight: 1 };
  });

  const minimo = Math.min(...valores.filter(v => v !== null));
  const limites = [minimo].concat(c);
  let html = "";
  for (let i = 0; i < COLORES.length; i++) {
    const desde = numero(limites[i], ind.decimales);
    html += `<span><span class="caja" style="background:${COLORES[i]}"></span>${i < 4 ? desde + " a " + numero(c[i], ind.decimales) : "más de " + numero(c[3], ind.decimales)}</span>`;
  }
  document.getElementById("leyenda").innerHTML = html;
}

function mostrarFicha(p) {
  let html = `<h3>${p.nombre_distrito} (${p.distrito_id})</h3>`;
  if (p.poblacion_total < POBLACION_BAJA) {
    html += `<p class="aviso">Este distrito tiene muy poca población (${numero(p.poblacion_total, 0)} habitantes):
      buena parte es puerto, industria, aeropuerto y estadios. Sus tasas por habitante salen muy altas y son poco estables.</p>`;
  }
  for (const clave in INDICADORES) {
    const ind = INDICADORES[clave];
    html += `<div class="dato"><span>${ind.nombre} ${etiquetaProxy(ind)}<br><small>${ind.unidad}</small></span>
      <span class="valor">${numero(p[clave], ind.decimales)} ${botonFuente(ind.fuentes, ind.calculo)}</span></div>`;
  }
  html += `<div class="dato"><span>Área<br><small>km²</small></span><span class="valor">${numero(p.area_km2, 1)} ${botonFuente(["F01"], "Área calculada con la proyección EPSG:2272.")}</span></div>`;
  document.getElementById("ficha").innerHTML = html;
}

function iniciarMapa() {
  mapa = L.map("mapa", { scrollWheelZoom: false });
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 18
  }).addTo(mapa);

  capa = L.geoJSON(distritos, {
    onEachFeature: function (f, layer) {
      layer.bindTooltip(f.properties.nombre_distrito);
      layer.on("click", function () { mostrarFicha(f.properties); });
    }
  }).addTo(mapa);
  mapa.fitBounds(capa.getBounds());

  const select = document.getElementById("indicador");
  for (const clave in INDICADORES) {
    const op = document.createElement("option");
    op.value = clave;
    op.textContent = INDICADORES[clave].nombre + (INDICADORES[clave].proxy ? " (PROXY)" : "");
    select.appendChild(op);
  }
  select.addEventListener("change", pintarMapa);
  pintarMapa();
}

// graficos de las preguntas
function dispersion(campoX, campoY, textoX, textoY) {
  const ancho = 420, alto = 300, m = { izq: 46, der: 40, arr: 15, aba: 42 };
  const puntos = distritos.features.map(f => f.properties).filter(p => p[campoX] !== null && p[campoY] !== null);
  const xs = puntos.map(p => p[campoX]), ys = puntos.map(p => p[campoY]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = 0, y1 = Math.max(...ys);
  const X = v => m.izq + (v - x0) / (x1 - x0) * (ancho - m.izq - m.der);
  const Y = v => alto - m.aba - (v - y0) / (y1 - y0) * (alto - m.arr - m.aba);

  let svg = `<svg class="grafico" viewBox="0 0 ${ancho} ${alto}" role="img">`;
  svg += `<line x1="${m.izq}" y1="${alto - m.aba}" x2="${ancho - m.der}" y2="${alto - m.aba}" stroke="#999"/>`;
  svg += `<line x1="${m.izq}" y1="${m.arr}" x2="${m.izq}" y2="${alto - m.aba}" stroke="#999"/>`;
  svg += `<text x="${(ancho + m.izq) / 2}" y="${alto - 8}" font-size="12" text-anchor="middle">${textoX}</text>`;
  svg += `<text x="14" y="${(alto - m.aba) / 2}" font-size="12" text-anchor="middle" transform="rotate(-90 14 ${(alto - m.aba) / 2})">${textoY}</text>`;
  svg += `<text x="${m.izq}" y="${alto - m.aba + 16}" font-size="10" text-anchor="middle">${numero(x0, 0)}</text>`;
  svg += `<text x="${ancho - m.der}" y="${alto - m.aba + 16}" font-size="10" text-anchor="end">${numero(x1, 0)}</text>`;
  svg += `<text x="${m.izq - 6}" y="${Y(y1) + 4}" font-size="10" text-anchor="end">${numero(y1, 1)}</text>`;
  svg += `<text x="${m.izq - 6}" y="${Y(0) + 4}" font-size="10" text-anchor="end">0</text>`;
  for (const p of puntos) {
    const color = p.poblacion_total < POBLACION_BAJA ? "#c0392b" : "#3f7cac";
    svg += `<circle cx="${X(p[campoX])}" cy="${Y(p[campoY])}" r="4.5" fill="${color}" opacity="0.85"><title>${p.nombre_distrito}</title></circle>`;
    svg += `<text x="${X(p[campoX]) + 7}" y="${Y(p[campoY]) + 4}" font-size="10" fill="#444">${p.distrito_id}</text>`;
  }
  return svg + "</svg>";
}

function textoRelacion(r) {
  return `Correlación de Spearman entre los 18 distritos: ${numero(r.rho_spearman, 2)} (p = ${numero(r.p_valor, 2)}), ${r.lectura}.`;
}

function pintarPreguntas() {
  const p1 = preguntas.P1;
  document.getElementById("p1").innerHTML = `
    <h3>P1. ${p1.pregunta}</h3>
    <p class="respuesta">No encontramos evidencia estadística suficiente de asociación entre las dos tasas.</p>
    <p>${textoRelacion(p1)} ${botonFuente(p1.fuentes, "Compara las dos tasas por 1.000 habitantes del mismo periodo, 2020-2024.")} <span class="proxy">PROXY</span></p>
    ${dispersion("reportes_viales_x1000hab", "siniestros_graves_x1000hab", "Reportes viales por 1.000 hab. al año", "Siniestros graves por 1.000 hab.")}
    <p class="nota">En rojo, Lower South (LS): tiene menos de 6.000 habitantes y por eso su tasa de siniestros sale muy alta.
      Sin ese distrito la relación sigue siendo débil.</p>`;

  const p2 = preguntas.P2;
  const filas = distritos.features.map(f => f.properties).sort((a, b) => b.paraderos_x_km2 - a.paraderos_x_km2);
  const max = filas[0].paraderos_x_km2;
  let barras = "";
  for (const p of filas) {
    barras += `<div class="barra"><span class="nombre">${p.nombre_distrito}</span>
      <span class="relleno" style="width:${p.paraderos_x_km2 / max * 55}%"></span><span>${numero(p.paraderos_x_km2, 1)}</span></div>`;
  }
  const masNombre = filas[0].nombre_distrito, menosNombre = filas[filas.length - 1].nombre_distrito;
  document.getElementById("p2").innerHTML = `
    <h3>P2. ${p2.pregunta}</h3>
    <p class="respuesta">${masNombre} tiene la mayor densidad (${numero(filas[0].paraderos_x_km2, 1)} paraderos por km²)
      y ${menosNombre} la menor (${numero(filas[filas.length - 1].paraderos_x_km2, 1)}).</p>
    <p>${botonFuente(p2.fuentes, INDICADORES.paraderos_x_km2.calculo)}</p>
    ${barras}`;

  const p3 = preguntas.P3;
  document.getElementById("p3").innerHTML = `
    <h3>P3. ${p3.pregunta}</h3>
    <p class="respuesta">No encontramos evidencia estadística suficiente para afirmar que los distritos de menor ingreso tardan más en ser atendidos.</p>
    <p>${textoRelacion(p3)} Una relación negativa habría indicado que a menor ingreso hay más días de espera;
      la que encontramos es débil y va en sentido contrario. ${botonFuente(p3.fuentes, "Compara el ingreso del hogar (PROXY) con la mediana de días de atención de las solicitudes viales cerradas, 2020-2024.")} <span class="proxy">PROXY</span></p>
    ${dispersion("proxy_ingreso_mediano_hogar", "mediana_dias_atencion", "Ingreso del hogar (USD al año, PROXY)", "Días de atención (mediana)")}`;
}

function pintarTablaFuentes() {
  let html = "";
  for (const id in fuentes) {
    const f = fuentes[id];
    html += `<tr><td>${id}</td><td><a href="${f.url}" target="_blank" rel="noopener noreferrer">${f.nombre}</a></td><td>${f.publica}</td><td>${f.licencia}</td><td>${f.periodo}</td><td>${f.fecha_prueba}</td></tr>`;
  }
  document.querySelector("#tabla-fuentes tbody").innerHTML = html;
}

// carga de datos
Promise.all([
  fetch("datos/distritos.geojson").then(r => r.json()),
  fetch("datos/fuentes.json").then(r => r.json()),
  fetch("datos/preguntas.json").then(r => r.json())
]).then(function (res) {
  distritos = res[0];
  fuentes = res[1];
  preguntas = res[2];
  iniciarMapa();
  pintarPreguntas();
  pintarTablaFuentes();
}).catch(function (err) {
  document.querySelector("main").insertAdjacentHTML("afterbegin",
    `<section class="aviso">No se pudieron cargar los datos (${err}). Si abrió el archivo directamente,
     use un servidor local: python -m http.server dentro de la carpeta docs.</section>`);
});
