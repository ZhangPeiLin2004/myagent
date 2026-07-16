


import { createContext, useContext, useState, ReactNode } from "react";

type SessionItem = {
  id: number;
  name: string;
};

type AppContextType = {
  sessions: SessionItem[];
  setSessions: (v: SessionItem[]) => void;
  currentSessionId: number | null;
  setCurrentSessionId: (v: number | null) => void;
  loading: boolean;
  setLoading: (v: boolean) => void;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  return (
    <AppContext.Provider value={{
      sessions, setSessions,
      currentSessionId, setCurrentSessionId,
      loading, setLoading
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppCtx() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppCtx must inside AppProvider");
  return ctx;
}
