const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// serve static UI
app.use(express.static(path.join(__dirname, 'public')));

// ensure files dir
const FILES_DIR = path.join(__dirname, 'files');
if (!fs.existsSync(FILES_DIR)) fs.mkdirSync(FILES_DIR, { recursive: true });

io.on('connection', (socket) => {
  console.log('client connected', socket.id);
  socket.on('chat message', (msg) => {
    console.log('received message:', msg);
    io.emit('chat message', msg);
  });
  socket.on('disconnect', () => {
    console.log('client disconnected', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
