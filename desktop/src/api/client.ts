const API_BASE = "http://localhost:8000";

export interface SessionData {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

export async function createSession(title = "新会话"): Promise<SessionData> {
  const resp = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return resp.json();
}

export async function listSessions(): Promise<SessionData[]> {
  const resp = await fetch(`${API_BASE}/sessions`);
  return resp.json();
}

export async function deleteSession(sessionId: string): Promise<{ ok: boolean }> {
  const resp = await fetch(`${API_BASE}/sessions/${sessionId}`, { method: "DELETE" });
  return resp.json();
}

export interface MessageData {
  role: "user" | "assistant" | "tool";
  content: string;
  format?: string;
  data?: unknown;
  name?: string;
  files?: string[];
  timestamp?: string;
}

export async function fetchSessionMessages(sessionId: string): Promise<MessageData[]> {
  const resp = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
  if (!resp.ok) return [];
  return resp.json();
}

export interface UploadedFileInfo {
  filename: string;
  file_path: string;
  size: number;
}

export async function uploadFile(file: File): Promise<UploadedFileInfo> {
  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || "上传失败");
  }
  return resp.json();
}

// Use POST-based SSE for longer messages
export async function* streamChat(
  sessionId: string,
  message: string,
  files?: string[]
): AsyncGenerator<{ type: string; content?: string; data?: unknown; format?: string; name?: string; args?: unknown }> {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message, files: files || [] }),
  });

  if (!resp.body) return;

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6));
        } catch { /* skip malformed */ }
      }
    }
  }
}
