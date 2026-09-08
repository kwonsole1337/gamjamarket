document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("preview-btn");
  const textarea = document.getElementById("description");
  const pane = document.getElementById("preview-pane");
  if (!btn || !textarea || !pane) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.textContent = "불러오는 중...";
    try {
      const res = await fetch("/api/product/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: textarea.value }),
      });
      const data = await res.json();
      if (data.ok) {
        pane.innerHTML = data.html;
      } else {
        pane.textContent = "미리보기 오류: " + data.error;
      }
    } catch (e) {
      pane.textContent = "미리보기를 불러오지 못했어요.";
    } finally {
      btn.disabled = false;
      btn.textContent = "미리보기";
    }
  });
});
