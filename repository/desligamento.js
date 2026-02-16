const sequelize = require('../config/sequelize');

exports.getDesligamento = async function () {
  try {
    console.log('Executando a query para buscar desligamentos...');

    const result = await sequelize.query(
      `
      select f.nomfun,c.nomcid,f.empregis,d.nomdep,f.admissao,f.demissao, f.sexo, s.nomesupervisor ,g.nomegerente, s2.dessetordesp, f2.nomefuncao 
      from cifalcomercial.funcionario f 
      left outer join cifalcomercial.setordespesa e on f.funcodsetordesp = e.codsetordesp
      left outer join cifalcomercial.departamentos d on f.funcoddep = d.coddep
      left outer join cifalcomercial.cidades c on f.codcid = c.codcid 
      left join cifalcomercial.setordespesa s2 on f.funcodsetordesp = s2.codsetordesp
      left join cifalcomercial.gerente g on s2.codgerente  = g.codgerente
      left join cifalcomercial.supervisor s on s.codsupervisor = s2.codsup
      left join cifalcomercial.funcaoadm f2 on f2.codfuncao  = f.codfuncao 
      WHERE f.empregis IS NOT NULL;
      `,
      {
        type: sequelize.QueryTypes.SELECT
      }
    );

    return result;

  } catch (error) {
    console.error('Erro ao executar a query:', error);
    throw error;
  }
};
