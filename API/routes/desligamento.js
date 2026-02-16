const express = require('express');
const router = express.Router();

const desligamentoController = require('../controllers/desligamento.js');

router.get('/rh_desligamento', desligamentoController.getDesligamento);

module.exports = router;
