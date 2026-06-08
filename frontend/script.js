// Se ajustaron los índices de columnas por la reubicación de Reloj Absoluto
const COLUMNAS_TIEMPO = [2, 3, 7, 8, 13, 17, 21];

document.getElementById('probAp').addEventListener('input', recalcProb);
document.getElementById('probVa').addEventListener('input', recalcProb);

function recalcProb() {
    const ap = Number(document.getElementById('probAp').value) || 0;
    const va = Number(document.getElementById('probVa').value) || 0;
    const vb = 100 - ap - va;

    if (vb < 0) {
        // Revertir el último campo editado al máximo posible
        const apInput = document.getElementById('probAp');
        const vaInput = document.getElementById('probVa');
        if (document.activeElement === apInput) {
            apInput.value = 100 - va;
        } else {
            vaInput.value = 100 - ap;
        }
        document.getElementById('probVb').value = 0;
    } else {
        document.getElementById('probVb').value = vb;
    }
}

function formatTime(val) {
    if (val === '-' || val === null || val === undefined || val === '') return '-';
    const num = Number(val);
    if (isNaN(num) || num < 0) return val;
    
    let totalSeconds = Math.round(num * 60);
    let h = Math.floor(totalSeconds / 3600);
    let m = Math.floor((totalSeconds % 3600) / 60);
    let s = totalSeconds % 60;
    
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('tablaBody');
    tbody.addEventListener('click', function(e) {
        const tr = e.target.closest('tr');
        if (!tr) return;
        const currentSelected = tbody.querySelector('.selected-row');
        if (currentSelected && currentSelected !== tr) {
            currentSelected.classList.remove('selected-row');
        }
        tr.classList.toggle('selected-row');
    });
});

async function ejecutarSimulacion() {
    const X = document.getElementById('X').value;
    const i = document.getElementById('i').value;
    const j = document.getElementById('j').value;

    const params = {
        lleg_a: Number(document.getElementById('llegA').value),
        lleg_b: Number(document.getElementById('llegB').value),
        ap_a: Number(document.getElementById('apA').value),
        ap_b: Number(document.getElementById('apB').value),
        va_a: Number(document.getElementById('vaA').value),
        va_b: Number(document.getElementById('vaB').value),
        vb_a: Number(document.getElementById('vbA').value),
        vb_b: Number(document.getElementById('vbB').value),
        prob_ap: Number(document.getElementById('probAp').value),
        prob_va: Number(document.getElementById('probVa').value)
    };

    if (!X || !i || !j) {
        mostrarError('Completá X, i, j.');
        return;
    }

    const pares = [
    { a: params.lleg_a, b: params.lleg_b, nombre: 'Llegada Clientes' },
    { a: params.ap_a,   b: params.ap_b,   nombre: 'Atención Aprendiz' },
    { a: params.va_a,   b: params.va_b,   nombre: 'Atención Veterano A' },
    { a: params.vb_a,   b: params.vb_b,   nombre: 'Atención Veterano B' },
    ];

    for (const par of pares) {
        if (par.a >= par.b) {
            mostrarError(`"${par.nombre}": el valor A (${par.a}) debe ser menor que B (${par.b}).`);
            return;
        }
    }

    const camposNumericos = ['X', 'i', 'j', 'llegA', 'llegB', 'apA', 'apB', 'vaA', 'vaB', 'vbA', 'vbB', 'probAp', 'probVa'];
    for (const id of camposNumericos) {
        if (Number(document.getElementById(id).value) < 0) {
            mostrarError(`Ningun campo puede ser negativo.`);
            return;
        }
    }

    document.getElementById('errorBox').style.display = 'none';
    document.getElementById('resultsPanel').style.display = 'none';
    document.getElementById('finalPanel').style.display = 'none';
    document.getElementById('spinnerWrap').style.display = 'flex';

    try {
        const response = await fetch('/simular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ X: Number(X), i: Number(i), j: Number(j), params: params })
        });
        const data = await response.json();

        if (!response.ok) {
            mostrarError(data.error || 'Error en simulación.');
            return;
        }

        renderizarTabla(data.columnas, data.filas);
        
        document.getElementById('ansLibre').textContent = `${data.metricas.pct_libre_aprendiz}%`;
        document.getElementById('ansSillas').textContent = `${data.metricas.max_sillas}`;
        document.getElementById('ansProb').textContent = `${data.metricas.prob_cola_tres.toFixed(2)}`;
        document.getElementById('spinnerWrap').style.display = 'none';
        document.getElementById('resultsMeta').innerHTML = `Mostrando tramo solicitado del vector de estados (<b>${data.filas.length}</b> filas generadas).`;
        document.getElementById('resultsPanel').style.display = 'block';
        document.getElementById('finalPanel').style.display = 'block';

    } catch (err) {
        mostrarError('Sin conexión con el backend.');
    }
}

function renderizarTabla(columnas, filas) {
    const thead = document.getElementById('tablaHead');
    const tbody = document.getElementById('tablaBody');
    thead.innerHTML = ''; tbody.innerHTML = '';

    thead.innerHTML = `
        <tr class="group-row">
            <th colspan="6" class="col-group-1">General</th>
            <th colspan="5" class="col-group-2">Llegada y Asignación</th>
            <th colspan="4" class="col-group-3">Peluquero: Aprendiz</th>
            <th colspan="4" class="col-group-4">Peluquero: Veterano A</th>
            <th colspan="4" class="col-group-5">Peluquero: Veterano B</th>
            <th colspan="3" class="col-group-7">Métricas Acumuladas</th>
        </tr>
    `;

    const trHead = document.createElement('tr');
    trHead.className = "col-row";
    columnas.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    const fragment = document.createDocumentFragment();
    filas.forEach(fila => {
        const tr = document.createElement('tr');
        
        fila.forEach((celda, idx) => {
            const td = document.createElement('td');
            let valorAMostrar = celda === null || celda === undefined ? '-' : String(celda);
            
            if (COLUMNAS_TIEMPO.includes(idx)) {
                valorAMostrar = formatTime(celda);
            }

            td.textContent = valorAMostrar;
            // Índice del evento ahora es el 4 (por la inserción del Reloj Absoluto en el 3)
            if (idx === 4) td.className = claseEvento(String(celda)); 
            tr.appendChild(td);
        });
        fragment.appendChild(tr);
    });
    tbody.appendChild(fragment);
}

function claseEvento(ev) {
    if (ev.includes('Llegada')) return 'ev-llegada';
    if (ev.includes('Fin Atencion')) return 'ev-fin';
    if (ev.includes('Cierre Recepcion')) return 'ev-cierre';
    if (ev.includes('Abandono')) return 'ev-abandono';
    if (ev.includes('Fin Simulación')) return 'ev-abandono';
    return 'ev-dia';
}

function mostrarError(msg) {
    document.getElementById('spinnerWrap').style.display = 'none';
    const box = document.getElementById('errorBox');
    document.getElementById('errorMsg').textContent = msg;
    box.style.display = 'flex';
}