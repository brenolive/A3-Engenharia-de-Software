// ============================================================
// componentes.js — Madeira Verde
// ✅ Listar | ✅ Criar | ✅ Editar (PUT) | ✅ Excluir | ✅ Visualizar
// PADRÃO: API.get/post/put/delete | UI.mostrarAlerta(id, msg, tipo)
// NUNCA redeclarar const API — já existe em api.js
// ============================================================

const formComponente = document.getElementById('form-componente');
const btnCancelar    = document.getElementById('btn-cancelar-edicao');

let editandoId = null;

// ============================================================
// CARREGAR
// ============================================================
async function carregarComponentes() {
  const filtroTipo = document.getElementById('filtro-tipo')?.value || '';
  const url = filtroTipo ? `/componentes?tipo=${filtroTipo}` : `/componentes`;

  try {
    const data = await API.get(url);
    renderizarTabela(data);
  } catch (err) {
    UI.tabelaVazia('tbody-componentes', 5);
  }
}

function renderizarTabela(componentes) {
  if (!componentes.length) {
    UI.tabelaVazia('tbody-componentes', 5);
    return;
  }
  const tbody = document.getElementById('tbody-componentes');
  tbody.innerHTML = '';
  componentes.forEach((c, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${c.nome}</td>
      <td>${UI.badgeTipoComp(c.tipo_componente)}</td>
      <td>${c.descricao || '—'}</td>
      <td style="text-align:center;">
        <button class="btn-icon btn-ver"
                title="Visualizar"
                onclick="verComponente(${c.id_componente})">👁️</button>
        <button class="btn-icon btn-editar"
                title="Editar"
                onclick="iniciarEdicaoComponente(${c.id_componente})">✏️</button>
        <button class="btn-icon btn-excluir"
                title="Excluir"
                onclick="excluirComponente(${c.id_componente}, '${c.nome}')">🗑️</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

// ============================================================
// VISUALIZAR
// ============================================================
async function verComponente(id) {
  try {
    const c = await API.get(`/componentes/${id}`);

    const base = [
      ['Nome',      c.nome],
      ['Tipo',      c.tipo_componente],
      ['Descrição', c.descricao || '—'],
    ];

    const extras =
      c.tipo_componente === 'MAQUINA' ? [
        ['Modelo',        c.modelo            || '—'],
        ['Fabricante',    c.fabricante         || '—'],
        ['Nº de Série',   c.numero_serie       || '—'],
        ['Vida (meses)',  c.tempo_medio_vida   ?? '—'],
        ['Data Compra',   UI.formatarData(c.data_compra)],
        ['Fim Garantia',  UI.formatarData(c.data_fim_garantia)],
        ['Em Manutenção', c.em_manutencao ? '⚠️ Sim' : '✅ Não'],
      ] : c.tipo_componente === 'MATERIA_PRIMA' ? [
        ['Origem',        c.origem      || '—'],
        ['Tipo Madeira',  c.tipo_madeira || '—'],
        ['Certificação',  c.certificacao || '—'],
      ] : c.tipo_componente === 'MATERIAL_DIVERSO' ? [
        ['Categoria',     c.categoria || '—'],
        ['Marca',         c.marca     || '—'],
      ] : c.tipo_componente === 'FERRAMENTA' ? [
        ['Tipo Ferramenta', c.tipo_ferramenta || '—'],
        ['Marca',           c.marca           || '—'],
        ['Nº de Série',     c.numero_serie    || '—'],
      ] : [];

    const linhas = [...base, ...extras].map(([k, v]) => `
      <tr>
        <td style="font-weight:600;width:45%;padding:6px 8px;color:#555;">${k}</td>
        <td style="padding:6px 8px;">${v}</td>
      </tr>`).join('');

    abrirModal(
      '🔩 Detalhes do Componente',
      `<table style="width:100%;border-collapse:collapse;font-size:0.95rem;">
         ${linhas}
       </table>`
    );
  } catch (err) {
    // ✅ UI.mostrarAlerta — nunca alert()
    UI.mostrarAlerta('alerta-comp', 'Erro ao buscar componente: ' + err.message, 'error');
  }
}

// ============================================================
// EDITAR
// ============================================================
// ✅ Renomeado: iniciarEdicaoComponente (padrão do projeto)
async function iniciarEdicaoComponente(id) {
  try {
    const c = await API.get(`/componentes/${id}`);
    editandoId = id;

    setVal('nome-comp', c.nome);
    setVal('tipo-comp', c.tipo_componente);
    setVal('desc-comp', c.descricao);

    // Dispara alterarCampos() para mostrar campos extras
    document.getElementById('tipo-comp')?.dispatchEvent(new Event('change'));

    // Campos extras por tipo
    setVal('modelo',          c.modelo);
    setVal('fabricante',      c.fabricante);
    setVal('n-serie',         c.numero_serie);
    setVal('tempo-vida',      c.tempo_medio_vida);
    setVal('data-compra',     c.data_compra);
    setVal('data-garantia',   c.data_fim_garantia);
    setVal('origem',          c.origem);
    setVal('tipo-madeira',    c.tipo_madeira);
    setVal('certificacao',    c.certificacao);
    setVal('categoria-comp',  c.categoria);
    setVal('marca-comp',      c.marca);
    setVal('tipo-ferramenta', c.tipo_ferramenta);

    document.getElementById('titulo-form-comp').textContent = '✏️ Editar Componente';
    if (btnCancelar) btnCancelar.style.display = 'inline-block';
    formComponente.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    // ✅ UI.mostrarAlerta — nunca alert()
    UI.mostrarAlerta('alerta-comp', 'Erro ao buscar componente: ' + err.message, 'error');
  }
}

function cancelarEdicaoComponente() {
  editandoId = null;
  formComponente.reset();
  alterarCampos();
  document.getElementById('titulo-form-comp').textContent = 'Cadastro de Componente';
  if (btnCancelar) btnCancelar.style.display = 'none';
}

// ============================================================
// SALVAR (POST ou PUT)
// ============================================================
formComponente.addEventListener('submit', async (e) => {
  e.preventDefault();

  const tipo = getVal('tipo-comp');

  const payload = {
    nome:            getVal('nome-comp'),
    tipo_componente: tipo,
    descricao:       getVal('desc-comp') || null,

    // Matéria-Prima
    origem:       tipo === 'MATERIA_PRIMA' ? (getVal('origem')       || null) : null,
    tipo_madeira: tipo === 'MATERIA_PRIMA' ? (getVal('tipo-madeira') || null) : null,
    certificacao: tipo === 'MATERIA_PRIMA' ? (getVal('certificacao') || null) : null,

    // Material Diverso
    categoria: tipo === 'MATERIAL_DIVERSO' ? (getVal('categoria-comp') || null) : null,

    // Máquina
    modelo:           tipo === 'MAQUINA' ? (getVal('modelo')        || null) : null,
    fabricante:       tipo === 'MAQUINA' ? (getVal('fabricante')    || null) : null,
    tempo_medio_vida: tipo === 'MAQUINA' ? (getValInt('tempo-vida'))         : null,
    data_compra:      tipo === 'MAQUINA' ? (getVal('data-compra')   || null) : null,
    data_fim_garantia:tipo === 'MAQUINA' ? (getVal('data-garantia') || null) : null,

    // Máquina + Ferramenta
    numero_serie: (tipo === 'MAQUINA' || tipo === 'FERRAMENTA')
      ? (getVal('n-serie') || null) : null,

    // Ferramenta
    tipo_ferramenta: tipo === 'FERRAMENTA' ? (getVal('tipo-ferramenta') || null) : null,

    // Material Diverso + Ferramenta
    marca: (tipo === 'MATERIAL_DIVERSO' || tipo === 'FERRAMENTA')
      ? (getVal('marca-comp') || null) : null,
  };

  try {
    if (editandoId) {
      await API.put(`/componentes/${editandoId}`, payload);
      UI.mostrarAlerta('alerta-comp', '✅ Componente atualizado com sucesso!', 'success');
    } else {
      await API.post('/componentes', payload);
      UI.mostrarAlerta('alerta-comp', '✅ Componente cadastrado com sucesso!', 'success');
    }
    cancelarEdicaoComponente();
    await carregarComponentes();
  } catch (err) {
    UI.mostrarAlerta('alerta-comp', '❌ ' + err.message, 'error');
  }
});

// ============================================================
// EXCLUIR
// ============================================================
async function excluirComponente(id, nome) {
  if (!confirm(`Excluir o componente "${nome}"?\nEsta ação não pode ser desfeita.`)) return;
  try {
    await API.delete(`/componentes/${id}`);
    UI.mostrarAlerta('alerta-comp', `✅ Componente "${nome}" excluído.`, 'success');
    await carregarComponentes();
  } catch (err) {
    UI.mostrarAlerta('alerta-comp', '❌ ' + err.message, 'error');
  }
}

// ============================================================
// HELPERS
// ============================================================
function setVal(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val ?? '';
}
function getVal(id) {
  return document.getElementById(id)?.value.trim() || '';
}
function getValInt(id) {
  const v = document.getElementById(id)?.value;
  return v !== '' && v != null ? parseInt(v) : null;
}

// ============================================================
// EVENTOS & INICIALIZAÇÃO
// ============================================================
if (btnCancelar) btnCancelar.addEventListener('click', cancelarEdicaoComponente);

document.getElementById('filtro-tipo')?.addEventListener('change', carregarComponentes);

carregarComponentes();
