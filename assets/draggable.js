// Tracks handles that already have drag listeners so we never double-bind the
// same DOM node. When Dash re-renders the float window it creates a BRAND-NEW
// element, so the WeakSet entry for the old node is gone and we re-initialise
// automatically. The MutationObserver is intentionally NOT disconnected so it
// keeps running for every subsequent re-render.

const _dragInitialized = new WeakSet();

function enableDrag() {
  const el = document.getElementById("ai-copilot-float-window");
  const handle = document.getElementById("float-drag-handle");

  if (!el || !handle) return false;

  // This particular handle node was already set up — skip.
  if (_dragInitialized.has(handle)) return true;
  _dragInitialized.add(handle);

  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  handle.addEventListener("mousedown", (e) => {
    isDragging = true;
    const rect = el.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
    e.preventDefault(); // prevent text selection while dragging
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    el.style.left   = e.clientX - offsetX + "px";
    el.style.top    = e.clientY - offsetY + "px";
    el.style.right  = "auto";
    el.style.bottom = "auto";
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
  });

  return true;
}

// Keep observing — Dash destroys and recreates the element on every re-render,
// so we need the observer alive to re-enable drag each time.
const _dragObserver = new MutationObserver(() => {
  enableDrag();
});

_dragObserver.observe(document.body, {
  childList: true,
  subtree: true,
});
