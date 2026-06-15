/**
 * Módulo de comunicação com a API.
 * Camada de Apresentação — Abstração das chamadas HTTP.
 */

const API_BASE_URL = "http://localhost:8000";

const API = {

  /**
   * Requisição GET.
   */
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      const erro = await response.json().catch(() => ({}));
      throw new Error(
        erro.detail?.mensagem || erro.detail || `Erro ${response.status}`
      );
    }
    return response.json();
  },

  /**
   * Requisição POST.
   */
  async post(endpoint, dados) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    if (!response.ok) {
      const erro = await response.json().catch(() => ({}));
      const msg =
        erro.detail?.mensagem ||
        (Array.isArray(erro.detail)
          ? erro.detail.map((e) => e.msg).join("; ")
          : erro.detail) ||
        `Erro ${response.status}`;
      throw new Error(msg);
    }
    return response.json();
  },

  /**
   * Requisição PUT.
   */
  async put(endpoint, dados) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    if (!response.ok) {
      const erro = await response.json().catch(() => ({}));
      throw new Error(
        erro.detail?.mensagem || erro.detail || `Erro ${response.status}`
      );
    }
    return response.json();
  },

  /**
   * Requisição PATCH.
   * ✅ NOVO — usado para atualizações parciais (ex: status da encomenda)
   */
  async patch(endpoint, dados = null) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "PATCH",
      headers: dados ? { "Content-Type": "application/json" } : {},
      body: dados ? JSON.stringify(dados) : null,
    });
    if (!response.ok) {
      const erro = await response.json().catch(() => ({}));
      throw new Error(
        erro.detail?.mensagem || erro.detail || `Erro ${response.status}`
      );
    }
    return response.status !== 204 ? response.json() : null;
  },

  /**
   * Requisição DELETE.
   */
  async delete(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      const erro = await response.json().catch(() => ({}));
      throw new Error(
        erro.detail?.mensagem || erro.detail || `Erro ${response.status}`
      );
    }
    return response.status !== 204 ? response.json() : null;
  },
};

/**
 * Utilitários de UI.
 */
const UI = {

  /**
   * Exibe mensagem de alerta.
   */
  mostrarAlerta(elementId, mensagem, tipo = "success") {
    const el = document.getElementById(elementId);
    if (!el) return;
    const icones = { success: "✅", error: "❌", info: "ℹ️" };
    el.className = `alert alert-${tipo}`;
    el.innerHTML = `${icones[tipo] || "📌"} ${mensagem}`;
    el.style.display = "flex";
    setTimeout(() => {
      el.className = "alert alert-hidden";
    }, 5000);
  },

  /**
   * Formata moeda BR.
   */
  formatarMoeda(valor) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(valor || 0);
  },

  /**
   * Formata data BR.
   */
  formatarData(data) {
    if (!data) return "—";
    const [ano, mes, dia] = data.split("-");
    return `${dia}/${mes}/${ano}`;
  },

  /**
   * Gera badge de status.
   */
  badgeStatus(status) {
    const mapa = {
      PENDENTE:    "badge-pendente",
      EM_PRODUCAO: "badge-producao",
      ENTREGUE:    "badge-entregue",
      CANCELADA:   "badge-cancelada",
    };
    return `<span class="badge ${mapa[status] || ""}">${status}</span>`;
  },

  /**
   * Badge de tipo de componente.
   */
  badgeTipoComp(tipo) {
    const mapa = {
      MAQUINA:          "badge-maquina",
      FERRAMENTA:       "badge-ferramenta",
      MATERIA_PRIMA:    "badge-materia",
      MATERIAL_DIVERSO: "badge-material",
    };
    const rotulos = {
      MAQUINA:          "Máquina",
      FERRAMENTA:       "Ferramenta",
      MATERIA_PRIMA:    "Matéria-Prima",
      MATERIAL_DIVERSO: "Mat. Diverso",
    };
    return `<span class="badge ${mapa[tipo] || ""}">${rotulos[tipo] || tipo}</span>`;
  },

  /**
   * Limpa tabela e exibe mensagem de vazio.
   */
  tabelaVazia(tbodyId, colunas) {
    const tbody = document.getElementById(tbodyId);
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="${colunas}"
              style="text-align:center; color:var(--cinza-escuro); padding:2rem;">
            Nenhum registro encontrado.
          </td>
        </tr>
      `;
    }
  },
};
