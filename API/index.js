const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
const cron = require('node-cron');



app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'email']
}));

// Configura o bodyParser
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Define as rotas
// (inserir definições de rotas aqui)
var rotasdesligamento = require('./routes/desligamento.js');
app.use('/v1', rotasdesligamento);




app.get('/', function (req, res) {
    res.send('Olá! Seja bem-vindo à nossa API');
});

app.listen(3000, () => {
    console.log('API On-line!');
});

