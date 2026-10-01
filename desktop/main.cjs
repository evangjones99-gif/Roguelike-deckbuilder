const { app, BrowserWindow, session } = require('electron');
const path = require('node:path');
const { installAudioLifecycle } = require('./audio-lifecycle.cjs');

// No remote content, Node integration, privileged preload or telemetry.
app.whenReady().then(() => {
  session.defaultSession.webRequest.onBeforeRequest((details, callback) => {
    callback({ cancel: !details.url.startsWith('file:') && !details.url.startsWith('devtools:') });
  });
  const win = new BrowserWindow({
    width: 1440, height: 900, minWidth: 1024, minHeight: 720,
    title: 'Hollowpact', backgroundColor: '#111516', autoHideMenuBar: true,
    icon: path.join(__dirname,'icon.png'),
    webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true, autoplayPolicy: 'no-user-gesture-required' }
  });
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.webContents.on('will-navigate', event => event.preventDefault());
  const entry = path.join(__dirname, '../dist/index.html');
  installAudioLifecycle(win, entry);
  win.loadFile(entry);
});
app.on('window-all-closed', () => app.quit());
