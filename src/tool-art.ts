import { TOOL_ART_URL, TOOL_ART_WINDOWS, type ToolArtFamily } from './art';

/** Decorative, static card paintings: redraw only after load or layout changes. */
export function createToolIllustrations() {
  const image = new Image();
  let ready = false;
  let disposed = false;
  let frame = 0;
  const canvases = new Set<HTMLCanvasElement>();
  function paint(canvas: HTMLCanvasElement) {
    if (!ready || !canvas.isConnected) return;
    const family = canvas.dataset.toolArt as ToolArtFamily;
    const windows = TOOL_ART_WINDOWS[family];
    if (!windows) return;
    const box = canvas.getBoundingClientRect();
    if (box.width <= 0 || box.height <= 0) return;
    const ratio = Math.min(2, window.devicePixelRatio || 1);
    const width = Math.round(box.width * ratio), height = Math.round(box.height * ratio);
    if (canvas.width !== width) canvas.width = width;
    if (canvas.height !== height) canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const { rect: [x, y, w, h], anchor: [ax, ay] } = canvas.closest('.large-card') ? windows.large : windows.hand;
    const scale = Math.max(width / w, height / h);
    // Sample only the selected source window; never include neighboring cells.
    const sw = width / scale, sh = height / scale;
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(image, x + (w - sw) * ax, y + (h - sh) * ay, sw, sh, 0, 0, width, height);
    canvas.parentElement?.classList.add('illustration-ready');
  }
  function schedule() {
    if (disposed || frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      for (const canvas of canvases) paint(canvas);
    });
  }
  const observer = new ResizeObserver(schedule);
  image.onload = () => {
    ready = image.naturalWidth === 1774 && image.naturalHeight === 887;
    if (ready) schedule();
  };
  // The existing family symbol stays visible while loading and on failure.
  image.onerror = () => { ready = false; };
  image.src = TOOL_ART_URL;
  return {
    refresh() {
      if (disposed) return;
      observer.disconnect(); canvases.clear();
      for (const canvas of document.querySelectorAll<HTMLCanvasElement>('canvas[data-tool-art]')) {
        canvases.add(canvas); observer.observe(canvas);
      }
      schedule();
    },
    dispose() {
      disposed = true; observer.disconnect(); canvases.clear();
      if (frame) cancelAnimationFrame(frame);
      frame = 0; image.onload = null; image.onerror = null;
    },
  };
}
