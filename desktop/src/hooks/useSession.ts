import { useState, useCallback, useEffect } from "react";
import { createSession, listSessions, deleteSession, type SessionData } from "../api/client";

export function useSession() {
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const fetchSessions = useCallback(async () => {
    try {
      const data = await listSessions();
      setSessions(data);
    } catch {
      // Server may not be running — silently degrade
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const newSession = useCallback(async (title?: string) => {
    setLoading(true);
    try {
      const session = await createSession(title);
      setSessions(prev => [session, ...prev]);
      setCurrentSessionId(session.id);
      return session;
    } finally {
      setLoading(false);
    }
  }, []);

  const switchSession = useCallback((id: string) => {
    setCurrentSessionId(id);
  }, []);

  const removeSession = useCallback(async (id: string) => {
    try {
      await deleteSession(id);
      setSessions(prev => prev.filter(s => s.id !== id));
      if (currentSessionId === id) {
        setCurrentSessionId("");
      }
    } catch {
      // silently fail
    }
  }, [currentSessionId]);

  return {
    sessions,
    currentSessionId,
    loading,
    newSession,
    switchSession,
    removeSession,
    fetchSessions,
  };
}
