document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("pay-btn");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const productId = btn.dataset.productId;

    btn.disabled = true;
    btn.textContent = "결제 처리 중...";

    try {
      const res = await fetch("/api/payment/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId }),
      });
      const data = await res.json();

      if (data.ok) {
        location.href = data.redirect_url;
      } else if (data.need_town_verification) {
        alert(data.error);
        location.href = "/location/verify";
      } else {
        alert(data.error || "결제에 실패했습니다.");
        btn.disabled = false;
        btn.textContent = "다시 시도하기";
      }
    } catch (e) {
      alert("결제 중 오류가 발생했습니다.");
      btn.disabled = false;
    }
  });
});
