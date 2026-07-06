import { useState, useCallback, useRef, useEffect } from "react";
import { streamChat, createSession, fetchSessionMessages } from "../api/client";
import type { UploadedFileInfo } from "../api/client";

export type UploadedFile = UploadedFileInfo;

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  data?: unknown;
  format?: string;
  files?: UploadedFile[];
}

export interface StreamStep {
  type: "thinking" | "tool_call" | "tool_result" | "text" | "error";
  label: string;
  detail?: string;
}

export interface StreamingStatus {
  active: boolean;
  elapsed: number;
  currentAction: string;
  steps: StreamStep[];
}

const TOOL_LABELS: Record<string, string> = {
  query_file: "📊 查询分析文件",
  sql_query: "🗄️ 查询数据库",
  chart_generate: "📈 生成可视化图表",
  document_parse: "📄 解析文档",
};

export function useChat(sessionId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState<StreamingStatus>({
    active: false, elapsed: 0, currentAction: "", steps: [],
  });
  const sessionIdRef = useRef<string>(sessionId || "");
  const timerRef = useRef<number | null>(null);

  // Sync sessionId from parent
  useEffect(() => {
    if (sessionId && sessionId !== sessionIdRef.current) {
      sessionIdRef.current = sessionId;
      loadMessages(sessionId);
    }
  }, [sessionId]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  const loadMessages = useCallback(async (sid: string) => {
    setLoading(true);
    try {
      const stored = await fetchSessionMessages(sid);
      const msgs: ChatMessage[] = stored.map((m, i) => {
        const base: ChatMessage = {
          id: `${sid}-${i}`,
          role: m.role,
          content: m.content || "",
          format: m.format || "markdown",
        };
        if (m.data) base.data = m.data;
        if (m.files) base.files = m.files.map((f: string) => ({ filename: f, file_path: f, size: 0 }));
        return base;
      });
      setMessages(msgs);
    } catch {
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const startTimer = useCallback(() => {
    const start = Date.now();
    timerRef.current = window.setInterval(() => {
      setStreaming(prev => prev.active
        ? { ...prev, elapsed: Math.floor((Date.now() - start) / 1000) }
        : prev
      );
    }, 200);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const sendMessage = useCallback(async (text: string, files?: UploadedFile[]) => {
    if (!sessionIdRef.current) {
      const session = await createSession();
      sessionIdRef.current = session.id;
    }

    const filePaths = files?.map(f => f.file_path);

    // Add user message
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      files: files || undefined,
    };
    setMessages(prev => [...prev, userMsg]);

    // Start streaming state
    setLoading(true);
    setStreaming({ active: true, elapsed: 0, currentAction: "🧠 正在思考分析...", steps: [] });
    startTimer();

    try {
      let assistantContent = "";
      const assistantId = `assistant-${Date.now()}`;

      for await (const event of streamChat(sessionIdRef.current, text, filePaths)) {
        // ── thinking ──
        if (event.type === "thinking") {
          setStreaming(prev => ({
            ...prev,
            currentAction: "🧠 思考分析中...",
          }));
        }
        // ── tool_call ──
        else if (event.type === "tool_call") {
          const name = (event.name as string) || "";
          const label = TOOL_LABELS[name] || `🔧 执行 ${name}`;
          const args = event.args as Record<string, unknown> || {};
          let detail = "";
          if (name === "query_file") {
            const sql = (args.sql as string) || "";
            if (sql.startsWith("SELECT") || sql.startsWith("select")) {
              detail = `SQL: ${sql.slice(0, 60)}${sql.length > 60 ? "..." : ""}`;
            } else {
              detail = `文件: ${args.file_path || ""}`;
            }
          } else if (name === "chart_generate") {
            const question = (args.question as string) || "";
            const chartType = (args.chart_type as string) || "";
            detail = chartType
              ? `${chartType} — ${question.slice(0, 30)}`
              : question.slice(0, 40);
          }

          setStreaming(prev => ({
            ...prev,
            currentAction: label,
            steps: [...prev.steps, { type: "tool_call", label, detail }],
          }));
        }
        // ── tool_result ──
        else if (event.type === "tool_result") {
          const format = (event.format as string) || "text";
          if (format === "chart") {
            setStreaming(prev => ({
              ...prev,
              currentAction: "✅ 图表已生成",
              steps: [...prev.steps, { type: "tool_result", label: "📊 图表生成完成" }],
            }));
          } else if (format === "table") {
            setStreaming(prev => ({
              ...prev,
              currentAction: "✅ 数据查询完成",
              steps: [...prev.steps, { type: "tool_result", label: "📋 数据查询完成" }],
            }));
          }
          // Add tool result message
          setMessages(prev => [...prev, {
            id: `tool-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            role: "tool",
            content: "",
            data: event.data,
            format: format,
          }]);
        }
        // ── text (streaming assistant response) ──
        else if (event.type === "text") {
          if (!assistantContent) {
            setStreaming(prev => ({
              ...prev,
              currentAction: "✍️ 生成分析报告...",
              steps: [...prev.steps, { type: "text", label: "✍️ 生成分析报告" }],
            }));
          }
          assistantContent += event.content || "";
          setMessages(prev => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.id === assistantId) {
              last.content = assistantContent;
            } else {
              next.push({ id: assistantId, role: "assistant", content: assistantContent, format: "markdown" });
            }
            return [...next];
          });
        }
        // ── error ──
        else if (event.type === "error") {
          setStreaming(prev => ({
            ...prev,
            currentAction: "❌ 出错",
            steps: [...prev.steps, { type: "error", label: `❌ ${event.content as string}` }],
          }));
        }
      }

    } finally {
      stopTimer();
      setStreaming({ active: false, elapsed: 0, currentAction: "", steps: [] });
      setLoading(false);
    }
  }, [loadMessages, startTimer, stopTimer]);

  return { messages, loading, streaming, sendMessage, sessionId: sessionIdRef.current };
}
