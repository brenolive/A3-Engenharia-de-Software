// ============================================================
// manutencoes.js — Madeira Verde
// ✅ Listar | ✅ Criar | ✅ Visualizar | ✅ Excluir | ✅ Filtrar
// PADRÃO: API.get/post/delete | UI.mostrarAlerta(id, msg, tipo)
// NUNCA redeclarar const API — já existe em api.js
// ============================================================

const formManutencao = document.getElementById('form-manutencao');

// ============================================================
// INICIALIZAÇÃO — carrega selects de máquinas e empresas
// ============================================================
async function inicializarSelects() {
  try {
    const [maquinas, empresas] = await Promise.all([
      API.get('/componentes?tipo=MAQUINA'),
      API.get('/manutencoes/empresas'),
    ]);

    const selMaq    = document.getElementById('id_maquina');
    const selEmp    = document.getElementById('id_empresa');
    const selFiltro = document.getElementById('filtro-maquina');

    maquinas.forEach(m => {
      const opt = `<option value="${m.id_componente}">${m.nome}</option>`;
      if (selMaq)    selMaq.insertAdjacentHTML('beforeend', opt);
      if (selFiltro) selFiltro.insertAdjacentHTML('beforeend', opt);
    });

    empresas.forEach(e => {
      if (selEmp) selEmp.insertAdjacentHTML('beforeend',
        `<option value="${e.id_empresa_manut}">${e.nome_fantasia || e.razao_social}</option>`);
    });

  } catch (err) {
    // ✅ UI.mostrarAlerta — nunca console.error
    UI.mostrarAlerta('alerta-manut', 'Erro ao carregar selects: ' + err.message, 'error');
  }
}

// ============================================================
// CARREGAR HISTÓRICO
// ============================================================
async function carregarHistorico() {
  const filtro = document.getElementById('filtro-maquina')?.value || '';
  try {
    const data = filtro
      ? await API.get(`/manutencoes/maquina/${filtro}`)
      : await API.get('/manutencoes');
    renderizarTabela(data);
  } catch (err) {
    UI.tabelaVazia('tbody-manutencoes', 9);
  }
}

function renderizarTabela(manutencoes) {
  if (!manutencoes.length) {
    UI.tabelaVazia('tbody-manutencoes', 9);
    return;
  }
  const tbody = document.getElementById('tbody-manutencoes');
  tbody.innerHTML = '';
  manutencoes.forEach((m, i) => {
    const inicio    = m.data_inicio ? UI.formatarData(m.data_inicio) : '—';
    const conclusao = m.data_fim    ? UI.formatarData(m.data_fim)    : '🔄 Em andamento';
    const custo     = m.custo != null ? UI.formatarMoeda(m.custo)   : '—';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${m.componente_nome   || m.id_componente}</td>
      <td>${m.empresa_nome      || m.id_empresa_manut}</td>
      <td><span class="badge">${m.tipo_manutencao}</span></td>
      <td>${inicio}</td>
      <td>${conclusao}</td>
      <td>${custo}</td>
      <td>${m.responsavel_interno || '—'}</td>
      <td style="text-align:center;">
        <button class="btn-icon btn-ver"
                title="Ver detalhes"
                onclick="verManutencao(${m.id_manutencao})">👁️</button>
        <button class="btn-icon btn-excluir"
                title="Excluir"
                onclick="excluirManutencao(${m.id_manutencao})">🗑️</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

// ============================================================
// VISUALIZAR DETALHES
// ============================================================
async function verManutencao(id) {
  try {
    const m = await API.get(`/manutencoes/${id}`);

    const inicio    = m.data_inicio ? UI.formatarData(m.data_inicio) : '—';
    const conclusao = m.data_fim    ? UI.formatarData(m.data_fim)    : '🔄 Em andamento';
    const custo     = m.custo != null ? UI.formatarMoeda(m.custo)   : '—';

    const campos = [
      ['Máquina',             m.componente_nome      || m.id_componente],
      ['Empresa',             m.empresa_nome         || m.id_empresa_manut],
      ['Tipo',                m.tipo_manutencao],
      ['Data de Início',      inicio],
      ['Data de Conclusão',   conclusao],
      ['Custo',               custo],
      ['Responsável Interno', m.responsavel_interno  || '—'],
      ['Descrição',           m.descricao            || '—'],
      ['Peças Substituídas',  m.pecas_substituidas   || '—'],
    ];

    const linhas = campos.map(([k, v]) => `
      <tr>
        <td style="font-weight:600;width:45%;padding:6px 8px;color:#555;">${k}</td>
        <td style="padding:6px 8px;">${v}</td>
      </tr>`).join('');

    abrirModal(
      '🔧 Detalhes da Manutenção',
      `<table style="width:100%;border-collapse:collapse;font-size:0.95rem;">
         ${linhas}
       </table>`
    );
  } catch (err) {
    // ✅ UI.mostrarAlerta — nunca alert()
    UI.mostrarAlerta('alerta-manut', 'Erro ao buscar manutenção: ' + err.message, 'error');
  }
}

// ============================================================
// CRIAR MANUTENÇÃO
// ============================================================
formManutencao?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    id_componente:       parseInt(document.getElementById('id_maquina')?.value),
    id_empresa_manut:    parseInt(document.getElementById('id_empresa')?.value),
    tipo_manutencao:     document.getElementById('tipo_manut')?.value,
    data_inicio:         document.getElementById('data_inicio')?.value,
    data_fim:            document.getElementById('data_fim')?.value          || null,
    custo:               parseFloat(document.getElementById('custo')?.value) || null,
    descricao:           document.getElementById('descricao_manut')?.value   || null,
    pecas_substituidas:  document.getElementById('pecas')?.value             || null,
    responsavel_interno: document.getElementById('resp_interno')?.value      || null,
  };

  try {
    await API.post('/manutencoes', payload);
    UI.mostrarAlerta('alerta-manut', '✅ Manutenção registrada com sucesso!', 'success');
    formManutencao.reset();
    await carregarHistorico();
  } catch (err) {
    UI.mostrarAlerta('alerta-manut', '❌ ' + err.message, 'error');
  }
});

// ============================================================
// EXCLUIR
// ============================================================
async function excluirManutencao(id) {
  if (!confirm('Excluir este registro de manutenção?\nEsta ação não pode ser desfeita.')) return;
  try {
    await API.delete(`/manutencoes/${id}`);
    UI.mostrarAlerta('alerta-manut', '✅ Manutenção excluída.', 'success');
    await carregarHistorico();
  } catch (err) {
    UI.mostrarAlerta('alerta-manut', '❌ ' + err.message, 'error');
  }
}

// ============================================================
// INIT
// ============================================================
inicializarSelects();
carregarHistorico();
