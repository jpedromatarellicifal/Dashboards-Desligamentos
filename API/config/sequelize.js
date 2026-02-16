const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
  'db_cifalcomercial',
  'postgres',
  'HMEY6&or#zz*2fK7QwT6',
  {
    host: '192.168.50.30',
    dialect: 'postgres',
    port: 5432,
    logging: false 
  }
);

module.exports = sequelize;
