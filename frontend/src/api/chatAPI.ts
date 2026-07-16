


const baseUrl = "/api";

export async function createSession(name: string) {
  const res = await fetch(`${baseUrl}/session/create?name=${encodeURIComponent(name)}`, {
    method: "POST"
  });
  return res.json();
}

export async function listSession() {
  const res = await fetch(`${baseUrl}/session/list`);
  return res.json();
}

export async function stockPredict(code: string, endDate: string) {
  const res = await fetch(`${baseUrl}/stock/predict?stock_code=${code}&window_end_date=${endDate}`, {
    method: "POST"
  });
  return res.json();
}

export async function runBacktest(start: string, end: string, codes: string[]) {
  const params = new URLSearchParams();
  params.append("backtest_start", start);
  params.append("backtest_end", end);
  codes.forEach(c => params.append("target_codes", c));
  const res = await fetch(`${baseUrl}/stock/backtest?${params.toString()}`, {
    method: "POST"
  });
  return res.json();
}
