const { spawn } = require('child_process');
const http = require('http');

const PORT = 8888;

const pythonProcess = spawn('python', ['C:\\Users\\e\\Documents\\http_server.py'], {
  cwd: 'C:\\Users\\e\\Documents',
  stdio: ['ignore', 'pipe', 'pipe']
});

pythonProcess.stdout.on('data', (data) => console.log(`Python: ${data}`));
pythonProcess.stderr.on('data', (data) => console.error(`Python Error: ${data}`));

const server = http.createServer((req, res) => {
  if (req.url === '/api/risk' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const options = {
        hostname: 'localhost',
        port: 8888,
        path: '/api/risk',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      };
      const proxyReq = http.request(options, (proxyRes) => {
        let data = '';
        proxyRes.on('data', chunk => data += chunk);
        proxyRes.on('end', () => {
          res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
          res.end(data);
        });
      });
      proxyReq.write(body);
      proxyReq.end();
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(3000, () => {
  console.log(`Server running at http://localhost:3000`);
});