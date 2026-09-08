document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("image-input");
  const pickerBtn = document.getElementById("image-picker-btn");
  const grid = document.getElementById("image-preview-grid");
  const warning = document.getElementById("image-upload-warning");
  if (!input || !pickerBtn || !grid) return;

  const MAX_FILES = 5;
  let selectedFiles = [];

  pickerBtn.addEventListener("click", () => input.click());

  input.addEventListener("change", () => {
    const incoming = Array.from(input.files || []);
    let hadRejected = false;

    for (const file of incoming) {

      if (file.name.toLowerCase().endsWith(".svg") || file.type === "image/svg+xml") {
        hadRejected = true;
        continue;
      }
      
      if (!file.type.startsWith("image/")) {
        hadRejected = true;
        continue;
      }
      if (selectedFiles.length >= MAX_FILES) {
        hadRejected = true;
        continue;
      }
      const isDuplicate = selectedFiles.some((f) => f.name === file.name && f.size === file.size);
      if (!isDuplicate) {
        selectedFiles.push(file);
      }
    }

    if (hadRejected) {
      warning.textContent = "보안상 SVG 파일은 업로드할 수 없습니다. (JPG, PNG 등만 가능)";
      warning.style.display = "block";
    } else {
      warning.style.display = "none";
    }

    syncInputFiles();
    renderPreviews();
  });

  function syncInputFiles() {

    const dt = new DataTransfer();
    selectedFiles.forEach((f) => dt.items.add(f));
    input.files = dt.files;
  }

  function renderPreviews() {
    grid.innerHTML = "";
    if (selectedFiles.length === 0) {
      grid.style.display = "none";
      return;
    }
    grid.style.display = "grid";

    selectedFiles.forEach((file, idx) => {
      const url = URL.createObjectURL(file);

      const item = document.createElement("div");
      item.className = "image-preview-item";

      const img = document.createElement("img");
      img.src = url;
      img.alt = file.name;
      item.appendChild(img);

      if (idx === 0) {
        const badge = document.createElement("span");
        badge.className = "image-preview-badge";
        badge.textContent = "대표";
        item.appendChild(badge);
      }

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "image-preview-remove";
      removeBtn.setAttribute("aria-label", "선택 취소");
      removeBtn.textContent = "✕";
      removeBtn.addEventListener("click", () => {
        selectedFiles.splice(idx, 1);
        syncInputFiles();
        renderPreviews();
      });
      item.appendChild(removeBtn);

      grid.appendChild(item);
    });
  }
});
