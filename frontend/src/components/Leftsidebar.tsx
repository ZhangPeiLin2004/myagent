


import { useAppCtx } from "../context/AppContext";
import { createSession, listSession } from "../api/chatApi";
import { useEffect, useState } from "react";

export default function LeftSidebar() {
  const { sessions, setSessions, setCurrentSessionId } = useAppCtx();
  const [newName, setNewName] = useState("");

  const refresh = async () => {
    const data = await listSession();
    setSessions(data);
  };

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createSession(newName);
    setNewName("");
    refresh();
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="w-60 bg-hermes-sidebar h-screen p-3 flex flex-col">
      <h2 className="text-white text-lg font-bold mb-4">Hermes Agent</h2>
      <div className="flex gap-2 mb-4">
        <input
          value={newName}
          onChange={e => setNewName(e.target.value)}
          placeholder="New session name"
          className="flex-1 px-2 py-1 rounded bg-hermes-card text-white text-sm"
        />
        <button onClick={handleCreate} className="bg-hermes-accent px-2 rounded text-sm">+</button>
      </div>
      <div className="flex-1 overflow-auto">
        {sessions.map(s => (
          <div
            key={s.id}
            onClick={() => setCurrentSessionId(s.id)}
            className="p-2 mb-1 rounded bg-hermes-card text-white cursor-pointer hover:opacity-80"
          >
            {s.name}
          </div>
        ))}
      </div>
    </div>
  );
}
