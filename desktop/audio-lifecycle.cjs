const { fileURLToPath } = require('node:url');

// Fixed renderer events carry no privileged capability or renderer-supplied main arguments.
const READY = "window.dispatchEvent(new Event('hollowpact-native-audio-ready'))";
const INACTIVE = "window.dispatchEvent(new Event('hollowpact-native-audio-inactive'))";
const ACTIVE = "(()=>{const receipt={cancelledEpoch:null};window.dispatchEvent(new CustomEvent('hollowpact-native-audio-active',{detail:receipt}));if(!Number.isInteger(receipt.cancelledEpoch)||receipt.cancelledEpoch<0)throw Error('Native audio cancellation barrier unacknowledged');return receipt.cancelledEpoch;})()";

function installAudioLifecycle(win, entry) {
  let generation = 0, documentGeneration = 0, ready = false, closed = false, tail = Promise.resolve();
  const alive = () => !closed && !win.isDestroyed() && !win.webContents.isDestroyed();
  const local = () => {
    if (!alive()) return false;
    try { const url = new URL(win.webContents.getURL()); return url.protocol === 'file:' && fileURLToPath(url) === entry; }
    catch { return false; }
  };
  const inactive = () => !win.isVisible() || win.isMinimized();
  const mute = () => { if (alive()) win.webContents.setAudioMuted(true); };
  const invalidate = () => { ready = false; generation++; documentGeneration++; mute(); };
  const transition = () => {
    if (!alive()) return;
    const blocked = inactive(), token = ++generation;
    mute();
    tail = tail.catch(() => {}).then(async () => {
      if (!alive() || !ready || !local()) return;
      // userGesture:false: native visibility/readiness alone never authorizes a context.
      await win.webContents.executeJavaScript(blocked ? INACTIVE : ACTIVE, false);
      if (alive() && token === generation && ready && !blocked && !inactive() && local()) {
        win.webContents.setAudioMuted(false);
      }
    }).catch(() => { mute(); });
  };
  mute();
  for (const event of ['hide', 'minimize', 'show', 'restore']) win.on(event, transition);
  win.webContents.on('did-start-loading', invalidate);
  win.webContents.on('render-process-gone', invalidate);
  win.webContents.on('did-finish-load', async () => {
    const documentToken = documentGeneration;
    try {
      if (!local()) return;
      await win.webContents.executeJavaScript(READY, false);
      if (!alive() || documentToken !== documentGeneration || !local()) return;
      ready = true;
      transition();
    } catch { invalidate(); }
  });
  win.on('closed', () => { closed = true; ready = false; generation++; documentGeneration++; });
}
module.exports = { installAudioLifecycle };
