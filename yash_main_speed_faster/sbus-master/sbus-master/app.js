
const express = require('express');
// const { createServer } = require('node:http');
const { createServer } = require('http');
const { join } = require('path');
const { Server } = require('socket.io');

const app = express();
const server = createServer(app);
const io = new Server(server);
// const textEncoder = new TextEncoder();
var util = require('util');
var encoder = new util.TextEncoder('utf-8');

const utf8 = require('utf8');

var SerialPort = require('serialport');
const { encode } = require('punycode');
const parsers = SerialPort.parsers;

const parser = new parsers.Readline({
    delimiter: '\r\n'
});

var port = new SerialPort('/dev/ttyACM0',{ 
    baudRate: 115200,
    dataBits: 8,
    parity: 'none',
    stopBits: 1,
    flowControl: false,
    //lock: false
});

port.pipe(parser);

app.get('/', (req, res) => {
    res.sendFile(join(__dirname, '/templates/joy_adam_only.html'));
    // res.sendFile(join(__dirname, '/static/joy2.js'));
});

io.on('connection', function(socket) {
    
    socket.on('lights',function(data){

        // console.log("je");

        // var myString = JSON.parse( JSON.stringify( data.status ) )

        // const u8Array = new Uint8Array(30)

        // const uint8Array = encoder.encode(data.status, u8Array)

        
        console.log(data.status);
        
        port.write( data.status );
    
    });
    
});

server.listen(3000, () => {
    console.log('server running at http://localhost:3000');
});

// app.listen(3000);

// var http = require('http');
// var fs = require('fs');
// var index = fs.readFileSync('index.html');



// var app = http.createServer(function(req, res) {
//     res.writeHead(200, {'Content-Type': 'text/html'});
//     res.end(index);
// });

// var io = require('socket.io')(app);

// io.on('connection', function(socket) {
    
//     socket.on('lights',function(data){
        
//         console.log( data.status);
        
//         port.write( data.status );
    
//     });
    
// });

// app.listen(3000);
