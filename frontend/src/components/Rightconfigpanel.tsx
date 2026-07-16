


import { useState } from "react";
import { runBacktest } from "../api/chatApi";

export default function RightConfigPanel() {
  const [start, setStart] = useState("2026-01-01");
  const [end, setEnd] = useState("2026-07-03");
  const [codes, setCodes] = useState("000001.SZ,600036.SH");
  const [report, setReport] = useState<any>(null);

  const handleBacktest = async () => {
    const list = codes.split(",").map(s=>s.trim());
    const res = await runBacktest(start, end, list);
    setReport(res.backtest_report);
  };

  return (
    <div className="w-72 bg-hermes-sidebar h-screen p-3 text-hermes-text overflow-auto">
      <h3 className="font-bold text-lg mb-4">Model & Backtest</h3>
      <div className="mb-3">
        <label className="text-sm block">Backtest Start</label>
        <input value={start} onChange={e=>setStart(e.target.value)} className="w-full bg-hermes-card p-1 rounded"/>
      </div>
      <div className="mb-3">
        <label className="text-sm block">Backtest End</label>
        <input value={end} onChange={e=>setEnd(e.target.value)} className="w-full bg-hermes-card p-1 rounded"/>
      </div>
      <div className="mb-3">
        <label className="text-sm block">Stock Codes(comma split)</label>
        <input value={codes} onChange={e=>setCodes(e.target.value)} className="w-full bg-hermes-card p-1 rounded"/>
      </div>
      <button onClick={handleBacktest} className="w-full bg-hermes-accent py-2 rounded mb-4">Run Backtest</button>
      {report && (
        <div className="bg-hermes-card p-2 rounded text-sm">
          <p>Precision: {report.precision}</p>
          <p>Recall: {report.recall}</p>
          <p>True Big Up: {report.total_true_big_up}</p>
          <p>Predict Signal: {report.total_pred_signal}</p>
        </div>
      )}
    </div>
  );
}
