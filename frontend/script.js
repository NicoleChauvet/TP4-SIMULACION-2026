// ── Estado global ────────────────────────────────────
let datosSimulacion = null;   // { columnas: [], filas: [[]] }
let filaSeleccionada = null;  // referencia a <tr> actualmente seleccionado

// ── Ejecutar simulación ──────────────────────────────
async function ejecutarSimulacion() {
    const N = document.getElementById('N').value.trim();
    const X = document.getElementById('X').value.trim();
    const i = document.getElementById('i').value.trim();
    const j = document.getElementById('j').value.trim();

    // Validación básica en frontend
    if (!N || !X || !i || !j === '') {
        mostrarError('Completá todos los campos antes de simular.');
        return;
    }
    if (Number(N) <= 0 || Number(X) <= 0 || Number(i) <= 0 || Number(j) < 0) {
        mostrarError('N, X e i deben ser mayores a 0. j debe ser mayor o igual a 0.');
        return;
    }

    ocultarError();
    ocultarResultados();
    mostrarSpinner(true);
    deshabilitarBoton(true);

    try {
        const response = await fetch('/simular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ N: Number(N), X: Number(X), i: Number(i), j: Number(j) })
        });

        const data = await response.json();

        if (!response.ok) {
            mostrarError(data.error || 'Error desconocido en el servidor.');
            return;
        }

        datosSimulacion = data;
        renderizarTabla(data.columnas, data.filas);
        mostrarResultados(data.filas.length);

    } catch (err) {
        mostrarError('No se pudo conectar con el servidor. ¿Está corriendo app.py?');
    } finally {
        mostrarSpinner(false);
        deshabilitarBoton(false);
    }
}

// ── Renderizar tabla ─────────────────────────────────
function renderizarTabla(columnas, filas) {
    const thead = document.getElementById('tablaHead');
    const tbody = document.getElementById('tablaBody');
    filaSeleccionada = null;

    // Cabecera
    thead.innerHTML = '';
    const trHead = document.createElement('tr');
    columnas.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col.replace(/_/g, ' ');
        th.title = col;
        trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    // Cuerpo — usamos fragment para rendimiento
    tbody.innerHTML = '';
    const fragment = document.createDocumentFragment();

    // Índice de la columna "Evento" para colorear
    const idxEvento = columnas.indexOf('Evento');

    filas.forEach((fila, idx) => {
        const tr = document.createElement('tr');
        tr.dataset.idx = idx;

        fila.forEach((celda, colIdx) => {
            const td = document.createElement('td');
            const valor = celda === null || celda === undefined ? '-' : String(celda);
            td.textContent = valor;

            // Color semántico en columna Evento
            if (colIdx === idxEvento) {
                td.className = claseEvento(valor);
            }

            tr.appendChild(td);
        });

        // Selección de fila con clic
        tr.addEventListener('click', () => seleccionarFila(tr));

        fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);
}

// ── Selección de fila ────────────────────────────────
function seleccionarFila(tr) {
    // Deseleccionar la anterior
    if (filaSeleccionada) {
        filaSeleccionada.classList.remove('selected');
    }
    // Si se hace clic en la misma, deseleccionar
    if (filaSeleccionada === tr) {
        filaSeleccionada = null;
        return;
    }
    tr.classList.add('selected');
    filaSeleccionada = tr;
}

// ── Color semántico por evento ───────────────────────
function claseEvento(evento) {
    if (!evento) return '';
    const e = evento.toLowerCase();
    if (e.includes('llegada'))   return 'ev-llegada';
    if (e.includes('fin atenc')) return 'ev-fin';
    if (e.includes('abandono'))  return 'ev-abandono';
    if (e.includes('cierre'))    return 'ev-cierre';
    if (e.includes('fin de dia') || e.includes('fin de día')) return 'ev-dia';
    if (e.includes('inicializ')) return 'ev-init';
    return '';
}

// ── Descargar CSV ────────────────────────────────────
function descargarCSV() {
    if (!datosSimulacion) return;

    const { columnas, filas } = datosSimulacion;
    const BOM = '\uFEFF'; // para compatibilidad con Excel

    const lineas = [
        columnas.join(';'),
        ...filas.map(fila =>
            fila.map(celda => {
                const v = celda === null || celda === undefined ? '' : String(celda);
                // Si contiene ; o salto de línea, entrecomillar
                return v.includes(';') || v.includes('\n') ? `"${v}"` : v;
            }).join(';')
        )
    ];

    const csv = BOM + lineas.join('\r\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'Vector_Estados_Peluqueria.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ── Utilidades de UI ─────────────────────────────────
function mostrarSpinner(visible) {
    document.getElementById('spinnerWrap').style.display = visible ? 'flex' : 'none';
}

function deshabilitarBoton(disabled) {
    const btn = document.getElementById('btnSimular');
    btn.disabled = disabled;
    btn.textContent = disabled ? '⏳ Simulando...' : '▶  Ejecutar simulación';
}

function mostrarError(msg) {
    const box = document.getElementById('errorBox');
    document.getElementById('errorMsg').textContent = msg;
    box.style.display = 'flex';
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function ocultarError() {
    document.getElementById('errorBox').style.display = 'none';
}

function mostrarResultados(cantFilas) {
    const panel = document.getElementById('resultsPanel');
    const meta = document.getElementById('resultsMeta');
    meta.innerHTML = `<strong>${cantFilas.toLocaleString('es-AR')}</strong> filas generadas`;
    panel.style.display = 'block';
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function ocultarResultados() {
    document.getElementById('resultsPanel').style.display = 'none';
}

// ── Atajo de teclado: Enter para simular ─────────────
document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && document.activeElement.tagName === 'INPUT') {
        ejecutarSimulacion();
    }
});
