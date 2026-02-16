const repository = require('../repository/desligamento.js');

exports.getDesligamento = async function () {
  const desligamentos = await repository.getDesligamento();
  

  const anoAtual = new Date().getFullYear();
  const anoLimite = anoAtual - 2;

  const filtrados = desligamentos.filter(reg => {

    if (!reg.demissao) return true;

    const dataDemissao = new Date(reg.demissao);
    const anoDemissao = dataDemissao.getFullYear();

    return anoDemissao >= anoLimite;
  });

  return filtrados; // 🔥 retorna dados para a controller
};
