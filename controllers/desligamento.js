const service = require('../services/desligamento.js');

// Campos permitidos (igual ao n8n)
const camposPermitidos = [
  "nomfun",
  "nomcid",
  "empregis",
  "nomdep",
  "admissao",
  "demissao",
  "sexo",
  "nomesupervisor",
  "nomegerente",
  "dessetordesp",
  "nomefuncao"
];


// 🔹 Função para normalizar nome da função (remove gênero)
function normalizarFuncao(texto) {
  if (!texto) return texto;

  let t = texto.trim().toLowerCase();

  // Jovem Aprendiz → APRENDIZ
  if (t.startsWith("jovem aprendiz")) return "APRENDIZ";

  // Pega só a primeira palavra
  t = t.split(" ")[0];

  // Remove gênero comum (a → o)
  const mapa = {
    vendedora: "vendedor",
    operadora: "operador",
    supervisora: "supervisor",
    gerentea: "gerente", // fallback raro
    atendente: "atendente"
  };

  if (mapa[t]) t = mapa[t];

  // Remove final "a" se existir versão masculina comum
  if (t.endsWith("a")) {
    const masculino = t.slice(0, -1) + "o";
    return masculino.toUpperCase();
  }

  return t.toUpperCase();
}


function replaceToPythonStyle(value, key = null) {

  // sexo nulo → Não Cadastrado
  if (key === "sexo" && (value === null || value === "None")) {
    return "Não Cadastrado";
  }

  // nomefuncao normalizado
  if (key === "nomefuncao" && typeof value === "string") {
    return normalizarFuncao(value);
  }

  // ✔️ DATA (IMPORTANTÍSSIMO)
  if (value instanceof Date) {
    return value.toISOString(); 
    // Ex: "2024-02-10T00:00:00.000Z"
  }

  if (value === null) return "None";
  if (value === true) return "True";
  if (value === false) return "False";

  if (Array.isArray(value)) {
    return value.map(v => replaceToPythonStyle(v));
  }

  if (typeof value === "object" && value !== null) {
    const obj = {};
    for (const k in value) {
      obj[k] = replaceToPythonStyle(value[k], k);
    }
    return obj;
  }

  return value;
}


// 🔥 CONTROLLER
exports.getDesligamento = async function (req, res) {
  try {
    const dados = await service.getDesligamento();
    console.log('Número de registros obtidos:', dados.length);

    const resultado = dados.map(item => {

      // 1️⃣ Filtrar campos permitidos
      const novoObjeto = {};

      for (const campo of camposPermitidos) {
        novoObjeto[campo] = item[campo] ?? null;
      }

      // 2️⃣ Converter estilo Python + tratamentos
      return replaceToPythonStyle(novoObjeto);
    });

    res.status(200).json(resultado);

  } catch (error) {
    console.error('Erro ao obter desligamento:', error);
    res.status(500).json({
      error: 'Ocorreu um erro ao obter os dados de desligamento.'
    });
  }
};
