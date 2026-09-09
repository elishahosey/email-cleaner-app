const { spawn } = require('child_process');
const path = require('path');

const frontendDir = path.resolve(__dirname, '..');
const backendDir = path.resolve(frontendDir, '..', 'backend');
const isWindows = process.platform === 'win32';
const bundledPython = path.join(
  backendDir,
  '.venv',
  isWindows ? 'Scripts' : 'bin',
  isWindows ? 'python.exe' : 'python'
);
const python = process.env.PYTHON || bundledPython;
const reactScripts = path.join(
  frontendDir,
  'node_modules',
  'react-scripts',
  'scripts',
  'start.js'
);

const children = [];
let stopping = false;

function run(command, args, cwd, name) {
  const child = spawn(command, args, {
    cwd,
    stdio: 'inherit',
    shell: false,
    env: process.env,
  });
  children.push(child);
  child.on('error', error => {
    console.error(`[${name}] Could not start: ${error.message}`);
    stop(1);
  });
  child.on('exit', code => {
    if (!stopping && code !== 0) {
      console.error(`[${name}] Exited with code ${code}.`);
      stop(code || 1);
    }
  });
  return child;
}

function stop(exitCode = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (!child.killed) child.kill(isWindows ? undefined : 'SIGTERM');
  }
  setTimeout(() => process.exit(exitCode), 250);
}

console.log(`[Email Cleaner] Using Python: ${python}`);
console.log('[Email Cleaner] Starting Django on http://localhost:8000');
run(python, ['manage.py', 'runserver', '127.0.0.1:8000'], backendDir, 'backend');

console.log('[Email Cleaner] Starting React on http://localhost:3000');
run(process.execPath, [reactScripts], frontendDir, 'frontend');

process.on('SIGINT', () => stop(0));
process.on('SIGTERM', () => stop(0));
