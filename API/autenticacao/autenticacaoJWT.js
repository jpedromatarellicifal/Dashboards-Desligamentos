var jwt = require('jsonwebtoken');
require('dotenv').config();

exports.gerarTokenJwt = async function(email){
    return jwt.sign({ 'CodUsuario': email }, process.env.JWT_SECRET, { expiresIn: '1h' });                 
};

exports.verificaTokenJwtRota = async function(req, res) {
    const token = req.headers['authorization'];
    
    // Se o token não for fornecido
    if (!token) {
        return res.status(401).json({ valido: false, message: 'Token não informado.' });
    }

    // Verifica a validade do token
    jwt.verify(token, process.env.JWT_SECRET, function(err, decoded) {
        if (err) {
            return res.status(401).json({ valido: false, message: 'Token inválido.' });
        }
        
        // Se o token for válido
        res.status(200).json({ valido: true, message: 'Token válido.' });
    });
};

exports.verificaTokenJwt = async function(req, res, next) {
    const token = req.headers['authorization'];
    
    if (!token) {
        return res.status(401).json({ valido: false, message: 'Token não informado.' });
    }

    jwt.verify(token, process.env.JWT_SECRET, function(err, decoded) {
        if (err) {
            return res.status(401).json({ valido: false, message: 'Token inválido.' });
        }

        // Se o token for válido
        console.log('Token válido:', decoded);
        req.usuario = decoded.CodUsuario; // Armazena o usuário decodificado
        next();  // Continua a execução da rota após a validação
    });
};

