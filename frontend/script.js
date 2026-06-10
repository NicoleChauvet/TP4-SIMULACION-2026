// Índices de columnas que contienen tiempos (se muestran como HH:MM:SS)
// 2=Reloj Día, 3=Reloj Abs, 7=T.Llegada, 8=Próx.Llegada
// 14=PróxFin Ap, 19=PróxFin VetA, 24=PróxFin VetB, 26=Acum.T.Libre Ap
const COLUMNAS_TIEMPO = [2, 3, 7, 8, 14, 19, 24, 26];

// Validacion de probabilidad de los peluqueros
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

// Funcion que le da formato a la hora de las columnas de tiempo
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

// Funcion que maneja la seleccion de una fila en la tabla
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

        renderizarTabla(data.columnas, data.filas, data.clientes_por_fila);
        
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

function renderizarTabla(columnas, filas, clientesPorFila) {
    const thead = document.getElementById('tablaHead');
    const tbody = document.getElementById('tablaBody');
    thead.innerHTML = ''; tbody.innerHTML = '';

    // Recolectar todos los IDs de clientes presentes en el rango mostrado
    const todosIds = new Set();
    clientesPorFila.forEach(snap => Object.keys(snap.clientes).forEach(id => todosIds.add(Number(id))));
    const idsOrdenados = [...todosIds].sort((a, b) => a - b);
    const numClientes = idsOrdenados.length;

    // Fila de grupos superiores (cada cliente ocupa 2 columnas: Hora Ab. + Estado)
    thead.innerHTML = `
        <tr class="group-row">
            <th colspan="6"  class="col-group-1">General</th>
            <th colspan="5"  class="col-group-2">Llegada y Asignación</th>
            <th colspan="5"  class="col-group-3">Peluquero: Aprendiz</th>
            <th colspan="5"  class="col-group-4">Peluquero: Veterano A</th>
            <th colspan="5"  class="col-group-5">Peluquero: Veterano B</th>
            <th colspan="7"  class="col-group-7">Métricas Acumuladas</th>
            ${numClientes > 0 ? `<th colspan="${numClientes * 2}" class="col-group-clientes">Estado de Clientes</th>` : ''}
        </tr>
    `;

    // Fila de encabezados de columnas
    const trHead = document.createElement('tr');
    trHead.className = 'col-row';
    columnas.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        trHead.appendChild(th);
    });
    idsOrdenados.forEach(id => {
        const thAb = document.createElement('th');
        thAb.textContent = `Hora Ab. C${id}`;
        thAb.className = 'th-cliente th-abandono';
        trHead.appendChild(thAb);

        const thEst = document.createElement('th');
        thEst.textContent = `C${id}`;
        thEst.className = 'th-cliente';
        trHead.appendChild(thEst);
    });
    thead.appendChild(trHead);

    // Filas del cuerpo
    const fragment = document.createDocumentFragment();
    filas.forEach((fila, rowIdx) => {
        const tr = document.createElement('tr');
        const snap = clientesPorFila[rowIdx] || { clientes: {}, abandono: {} };

        fila.forEach((celda, idx) => {
            const td = document.createElement('td');
            let valorAMostrar = celda === null || celda === undefined ? '-' : String(celda);
            if (COLUMNAS_TIEMPO.includes(idx)) {
                valorAMostrar = formatTime(celda);
            }
            td.textContent = valorAMostrar;
            if (idx === 4) td.className = claseEvento(String(celda));
            tr.appendChild(td);
        });

        // Par de celdas por cliente: Hora Abandono + Estado
        idsOrdenados.forEach(id => {
            const horaAbandono = snap.abandono[String(id)];
            const sigla = snap.clientes[String(id)] || '-';

            const tdAb = document.createElement('td');
            tdAb.textContent = horaAbandono !== undefined ? formatTime(horaAbandono) : '-';
            tdAb.className = horaAbandono !== undefined ? 'cli-hora-abandono' : '';
            tr.appendChild(tdAb);

            const tdEst = document.createElement('td');
            tdEst.textContent = sigla;
            tdEst.className = claseCliente(sigla);
            tr.appendChild(tdEst);
        });

        fragment.appendChild(tr);
    });
    tbody.appendChild(fragment);
}

// Agregar la clase corrrespondiente segun el evento
function claseEvento(ev) {
    if (ev.includes('Llegada')) return 'ev-llegada';
    if (ev.includes('Fin Atencion')) return 'ev-fin';
    if (ev.includes('Cierre Recepcion')) return 'ev-cierre';
    if (ev.includes('Abandono')) return 'ev-abandono';
    if (ev.includes('Fin Simulación')) return 'ev-abandono';
    return 'ev-dia';
}

// Colorear celdas de estado de cliente según sigla
function claseCliente(sigla) {
    if (sigla.startsWith('SA')) return 'cli-siendo-atendido';
    if (sigla.startsWith('EC')) return 'cli-en-cola';
    if (sigla === 'AT') return 'cli-atendido';
    if (sigla === 'AB') return 'cli-abandono';
    return '';
}

function mostrarError(msg) {
    document.getElementById('spinnerWrap').style.display = 'none';
    const box = document.getElementById('errorBox');
    document.getElementById('errorMsg').textContent = msg;
    box.style.display = 'flex';
}