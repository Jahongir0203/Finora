// BE-1902: yuklama testi — Home, Activity, Stats 500 RPS'da p95 < 300 ms.
//
//   k6 run -e BASE_URL=https://staging-api.finora.uz -e TOKENS=tokens.txt \
//          backend/loadtest/home_activity_stats.js
//
// tokens.txt — staging'dagi test userlarining access tokenlari (har qatorda bitta).
// Tokenlar 15 daqiqa yashaydi: test oldidan `scripts` bilan yangilang. Prod'da ishlatilmaydi.
import http from "k6/http";
import { check } from "k6";
import { SharedArray } from "k6/data";

const BASE = __ENV.BASE_URL;
const tokens = new SharedArray("tokens", () =>
  open(__ENV.TOKENS || "tokens.txt").split("\n").filter((t) => t.trim().length > 0));

export const options = {
  scenarios: {
    mixed: {
      executor: "constant-arrival-rate",
      rate: 500,
      timeUnit: "1s",
      duration: "5m",
      preAllocatedVUs: 200,
      maxVUs: 800,
    },
  },
  thresholds: {
    "http_req_duration{endpoint:home}": ["p(95)<300"],
    "http_req_duration{endpoint:activity}": ["p(95)<300"],
    "http_req_duration{endpoint:stats}": ["p(95)<300"],
    http_req_failed: ["rate<0.01"],
  },
};

const ENDPOINTS = [
  ["home", "/v1/home"],
  ["activity", "/v1/transactions?limit=30"],
  ["stats", "/v1/stats?period=month"],
];

export default function () {
  const token = tokens[Math.floor(Math.random() * tokens.length)];
  const [name, path] = ENDPOINTS[Math.floor(Math.random() * ENDPOINTS.length)];
  const res = http.get(`${BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}`, "X-Timezone": "Asia/Tashkent" },
    tags: { endpoint: name },
  });
  check(res, { "status 200": (r) => r.status === 200 });
}
