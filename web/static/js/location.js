function haversineMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

async function submitVerification(payload, status) {
  try {
    const res = await fetch("/api/location/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.ok) {
      status.textContent = `✅ ${data.town} 인증이 완료되었습니다!`;
      setTimeout(() => location.reload(), 800);
    } else {
      status.textContent = "동네인증에 실패했어요. 다시 시도해주세요.";
    }
  } catch (e) {
    status.textContent = "요청을 보내는 중 오류가 발생했어요.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("geo-btn");
  const status = document.getElementById("geo-status");
  const townsDataEl = document.getElementById("towns-data");
  if (!btn || !townsDataEl) return;

  const towns = JSON.parse(townsDataEl.textContent);

  function fallbackPayload() {
    const t = towns[0];
    return { lat: 35.1796, lng: 129.0756, town_id: t ? t.id : null, client_verified: false };
  }

  btn.addEventListener("click", () => {
    if (!("geolocation" in navigator)) {
      status.textContent = "위치 정보를 가져오지 못했어요. 잠시 후 다시 시도해주세요.";
      submitVerification(fallbackPayload(), status);
      return;
    }

    status.textContent = "내 위치를 확인하는 중...";

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude: lat, longitude: lng } = pos.coords;

        let nearest = null;
        let nearestDist = Infinity;
        for (const t of towns) {
          const d = haversineMeters(lat, lng, t.lat, t.lng);
          if (d < nearestDist) {
            nearestDist = d;
            nearest = t;
          }
        }

        const withinRadius = nearest && nearestDist <= nearest.radius_m;

        status.textContent = "인증 요청을 보내는 중...";

        const payload = {
          lat,
          lng,
          town_id: nearest ? nearest.id : null,
          client_verified: withinRadius,
        };

        submitVerification(payload, status);
      },
      () => {

        status.textContent = "위치 정보를 가져오지 못했어요. 잠시 후 다시 시도해주세요.";
        submitVerification(fallbackPayload(), status);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  });
});
