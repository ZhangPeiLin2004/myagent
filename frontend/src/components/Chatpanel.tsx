


import { useState } from "react";
import MessageCard from "./MessageCard";
import { stockPredict } from "../api/chatApi";

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);

  const handleSend = async () => {
    setMessages(p => [...p, {role:"user", content: input}]);
    const codeMatch = input.match(/(\d{6}\.[SZH])/);
    const dateMatch = input.match(/(\d{4}-\d{2}-\d{2})/);
    if (!codeMatch || !dateMatch) {
      setMessages(p => [...p, {role:"assistant", content:"请输入股票代码与截止日期，例如：000001.SZ 2026-07-03"}]);
      return;
    }
    const code = codeMatch[1];
    const date = dateMatch[1];
    const res = await stockPredict(code, date);
    const info = res.predict_result;
    const reply = `预测结果：
股票：${info.stock_code}
预测明日：${info.target_date}
上涨>1.5%概率：${info.prob_up_1p5}
阈值：${info.threshold}
是否大涨信号：${info.is_big_rise}`;
    setMessages(p => [...p, {role:"assistant", content: reply}]);
    setInput("");
  };

  return (
    <div className="flex-1 bg-hermes-bg flex flex-col h-screen">
      <div className="flex-1 p-4 overflow-auto">
        {messages.map((m, i) => <MessageCard key={i} role={m.role as any} content={m.content}/>)}
      </div>
      <div className="p-3 border-t border-gray-700 flex gap-2">
        <textarea
          value={input}
          onChange={e=>setInput(e.target.value)}
          className="flex-1 bg-hermes-card text-white p-2 rounded"
          placeholder="输入预测指令，如 000001.SZ 2026-07-03"
        />
        <button onClick={handleSend} className="bg-hermes-accent px-4 rounded text-white">发送</button>
      </div>
    </div>
  );
}
