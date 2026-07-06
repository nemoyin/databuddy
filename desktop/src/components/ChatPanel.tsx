import { useState, useRef, useEffect } from "react";
import { Input, Upload, Tag, message, Button, Space, Typography } from "antd";
import { SendOutlined, UploadOutlined, FileOutlined, FilePdfOutlined, LoadingOutlined, CheckCircleOutlined } from "@ant-design/icons";
import type { UploadFile, RcFile } from "antd/es/upload";
import { MessageBubble } from "./MessageBubble";
import { useChat } from "../hooks/useChat";
import type { ChatMessage, UploadedFile } from "../hooks/useChat";
import { uploadFile } from "../api/client";

const API_BASE = "http://localhost:8000";

/** 导出单条 assistant 消息为 PDF */
async function exportMessageAsPDF(content: string, allMessages: ChatMessage[], msgIdx: number) {
  // 找到本条回答对应的用户问题作为标题
  let title = "JWBuddy 分析报告";
  for (let i = msgIdx - 1; i >= 0; i--) {
    if (allMessages[i].role === "user" && allMessages[i].content) {
      title = allMessages[i].content.slice(0, 40);
      if (allMessages[i].content.length > 40) title += "...";
      break;
    }
  }

  const { message: antMsg } = await import("antd");
  antMsg.loading({ content: "生成 PDF...", key: "pdf-export" });
  try {
    const resp = await fetch(`${API_BASE}/export/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        content,
      }),
    });
    if (!resp.ok) throw new Error("导出失败");
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `JWBuddy_分析报告_${Date.now()}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
    antMsg.success({ content: "PDF 导出成功", key: "pdf-export" });
  } catch (e) {
    const antd = await import("antd");
    antd.message.error({ content: `PDF 导出失败: ${e instanceof Error ? e.message : ""}`, key: "pdf-export" });
  }
}

interface Props {
  sessionId?: string;
  onNewSession?: () => void;
}

export function ChatPanel({ sessionId, onNewSession }: Props) {
  const [input, setInput] = useState("");
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const { messages, loading, streaming, sendMessage } = useChat(sessionId);

  const handleUpload = async (file: RcFile) => {
    setUploading(true);
    try {
      const info = await uploadFile(file);
      setUploadedFiles(prev => [...prev, info]);
      setFileList(prev => [...prev, {
        uid: info.file_path,
        name: info.filename,
        status: "done",
      }]);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "上传失败";
      message.error(msg);
      setFileList(prev => prev.filter(f => f.name !== file.name));
    } finally {
      setUploading(false);
    }
    return false;
  };

  const handleRemove = (file: UploadFile) => {
    setFileList(prev => prev.filter(f => f.uid !== file.uid));
    setUploadedFiles(prev => prev.filter(f => f.file_path !== file.uid));
  };

  const handleSend = () => {
    if ((!input.trim() && uploadedFiles.length === 0) || loading) return;
    sendMessage(input.trim() || "请分析上传的文件", uploadedFiles.length > 0 ? uploadedFiles : undefined);
    setInput("");
    setFileList([]);
    setUploadedFiles([]);
  };

  const handleExportPDF = async () => {
    const lastAssistant = [...messages].reverse().find(m => m.role === "assistant" && m.content);
    if (!lastAssistant) {
      message.warning("没有可导出的分析内容");
      return;
    }

    const lastIdx = messages.indexOf(lastAssistant);
    const nearbyToolResults = messages.slice(Math.max(0, lastIdx - 5), lastIdx)
      .filter(m => m.role === "tool" && m.format === "table" && m.data != null);
    const tables = nearbyToolResults.map(m => m.data as Record<string, unknown>);

    message.loading({ content: "生成 PDF...", key: "pdf" });
    try {
      const resp = await fetch(`${API_BASE}/export/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: `JWBuddy 分析报告`,
          content: lastAssistant.content,
          tables,
        }),
      });

      if (!resp.ok) throw new Error("导出失败");

      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `JWBuddy_分析报告_${Date.now()}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      message.success({ content: "PDF 导出成功", key: "pdf" });
    } catch (e) {
      message.error({ content: `PDF 导出失败: ${e instanceof Error ? e.message : ""}`, key: "pdf" });
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ flex: 1, overflow: "auto", padding: 16 }}>
        {!sessionId && messages.length === 0 && !loading && (
          <div style={{ textAlign: "center", padding: "80px 20px", color: "#999" }}>
            <h2 style={{ color: "#666", marginBottom: 8 }}>JWBuddy</h2>
            <p>选择左侧会话，或点击「新建会话」开始</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onReRun={
              msg.role === "assistant"
                ? () => {
                    for (let i = idx - 1; i >= 0; i--) {
                      if (messages[i].role === "user" && messages[i].content) {
                        sendMessage(messages[i].content);
                        break;
                      }
                    }
                  }
                : undefined
            }
            onExportPDF={
              msg.role === "assistant" && msg.content
                ? () => exportMessageAsPDF(msg.content, messages, idx)
                : undefined
            }
          />
        ))}
        {/* ⏱ 流式进度面板 */}
        {streaming.active && (
          <div style={{
            margin: "8px 16px 16px",
            padding: "12px 16px",
            background: "#f6f8fa",
            borderRadius: 8,
            border: "1px solid #e8e8e8",
            fontSize: 13,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <LoadingOutlined style={{ color: "#1677ff" }} />
              <span style={{ fontWeight: 600, color: "#333" }}>{streaming.currentAction}</span>
              <span style={{ marginLeft: "auto", color: "#888", fontVariantNumeric: "tabular-nums", fontFamily: "monospace" }}>
                ⏱ {String(Math.floor(streaming.elapsed / 60)).padStart(2, "0")}:{String(streaming.elapsed % 60).padStart(2, "0")}
              </span>
            </div>
            {/* 已完成步骤列表 */}
            {streaming.steps.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 3, marginTop: 4 }}>
                {streaming.steps.map((step, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 6, color: "#666" }}>
                    <CheckCircleOutlined style={{ color: "#52c41a", fontSize: 12 }} />
                    <span>{step.label}</span>
                    {step.detail && <span style={{ color: "#999", fontSize: 12 }}>— {step.detail}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {fileList.length > 0 && (
        <div style={{ padding: "4px 16px 0" }}>
          {fileList.map(f => (
            <Tag
              key={f.uid}
              closable
              onClose={() => handleRemove(f)}
              icon={<FileOutlined />}
              style={{ marginBottom: 4 }}
            >
              {f.name}
            </Tag>
          ))}
        </div>
      )}

      <div style={{ padding: "8px 16px", borderTop: "1px solid #f0f0f0" }}>
        <Space style={{ marginBottom: 8 }}>
          <Button
            size="small"
            icon={<FilePdfOutlined />}
            onClick={handleExportPDF}
            disabled={messages.length === 0}
          >
            导出 PDF
          </Button>
        </Space>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Upload
            beforeUpload={(file) => { handleUpload(file as RcFile); return false; }}
            fileList={fileList}
            onRemove={handleRemove}
            showUploadList={false}
          >
            <UploadOutlined style={{ fontSize: 20, cursor: "pointer", color: uploading ? "#bbb" : "#1677ff" }} />
          </Upload>
          <Input.Search
            value={input}
            onChange={e => setInput(e.target.value)}
            onSearch={handleSend}
            placeholder="输入你的问题，或上传文件..."
            enterButton={<SendOutlined />}
            size="large"
            loading={loading}
            style={{ flex: 1 }}
          />
        </div>
      </div>
    </div>
  );
}
