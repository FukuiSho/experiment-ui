import net from 'node:net';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const HOST = '127.0.0.1';
const PORT_START = 8001;
const PORT_END = 8010;

function isPortFree(port) {
    return new Promise((resolve) => {
        const server = net.createServer();
        server.once('error', () => resolve(false));
        server.once('listening', () => {
            server.close(() => resolve(true));
        });
        server.listen(port, HOST);
    });
}

async function findFreePort() {
    for (let port = PORT_START; port <= PORT_END; port += 1) {
        // eslint-disable-next-line no-await-in-loop
        if (await isPortFree(port)) return port;
    }
    throw new Error(`No free port in range ${PORT_START}-${PORT_END}`);
}

function writePortFile(repoRoot, port) {
    const filePath = path.join(repoRoot, '.cloneai-port');
    fs.writeFileSync(filePath, String(port), 'utf8');
}

function removePortFile(repoRoot) {
    const filePath = path.join(repoRoot, '.cloneai-port');
    try {
        fs.unlinkSync(filePath);
    } catch {
        // ignore
    }
}

async function main() {
    const repoRoot = path.resolve(process.cwd());
    const serviceDir = path.join(repoRoot, 'services', 'cloneai');

    const port = await findFreePort();
    writePortFile(repoRoot, port);

    console.log(`[cloneai] Starting FastAPI on http://${HOST}:${port}`);

    const child = spawn(
        'python',
        ['-m', 'uvicorn', 'clone_server:app', '--host', HOST, '--port', String(port)],
        {
            cwd: serviceDir,
            stdio: 'inherit',
            env: process.env,
        }
    );

    const cleanup = () => {
        removePortFile(repoRoot);
    };

    child.on('exit', (code) => {
        cleanup();
        process.exit(code ?? 0);
    });

    process.on('SIGINT', () => {
        cleanup();
        child.kill('SIGINT');
    });

    process.on('SIGTERM', () => {
        cleanup();
        child.kill('SIGTERM');
    });
}

main().catch((err) => {
    console.error('[cloneai] Failed to start:', err);
    process.exit(1);
});
