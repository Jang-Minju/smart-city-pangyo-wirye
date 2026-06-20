import { createServer } from 'vite';

const host = '127.0.0.1';
const portArgIndex = process.argv.indexOf('--port');
const requestedPort = portArgIndex >= 0 ? Number(process.argv[portArgIndex + 1]) : 5173;
const port = Number.isFinite(requestedPort) ? requestedPort : 5173;

const server = await createServer({
  server: {
    host,
    port,
  },
});

await server.listen();
server.printUrls();

process.on('SIGINT', async () => {
  await server.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await server.close();
  process.exit(0);
});

setInterval(() => {}, 1 << 30);
