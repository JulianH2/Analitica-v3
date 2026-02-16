function enableDrag() {
  const el = document.getElementById("ai-copilot-float-window");
  const handle = document.getElementById("float-drag-handle");

  if (!el || !handle) return false;

  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  handle.onmousedown = (e) => {
    isDragging = true;
    offsetX = e.clientX - el.getBoundingClientRect().left;
    offsetY = e.clientY - el.getBoundingClientRect().top;
  };

  document.onmousemove = (e) => {
    if (!isDragging) return;

    el.style.left = e.clientX - offsetX + "px";
    el.style.top = e.clientY - offsetY + "px";

    el.style.right = "auto";
    el.style.bottom = "auto";
  };

  document.onmouseup = () => {
    isDragging = false;
  };

  return true;
}

const observer = new MutationObserver(() => {
  if (enableDrag()) {
    observer.disconnect();
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});
