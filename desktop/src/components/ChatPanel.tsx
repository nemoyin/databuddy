import { useState } from "react";
import { Input, Spin, Upload, Tag, message, Button, Space } from "antd";
import { SendOutlined, UploadOutlined, FileOutlined, FilePdfOutlined } from "@ant-design/icons";
import type { UploadFile, RcFile } from "antd/es/upload";
import { MessageBubble } from "./MessageBubble";
import { useChat } from "../hooks/useChat";
import type { UploadedFile } from "../hooks/useChat";
import { uploadFile } from "../api/client";

const API_BASE = "http://localhost:8000";

export function ChatPanel() {
  const [input, setInput] = useState("");
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const { messages, loading, sendMessage } = useChat();

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
    // 收集最后一条 assistant 消息的内容
    const lastAssistant = [...messages].reverse().find(m => m.role === "assistant" && m.content);
    if (!lastAssistant) {
      message.warning("没有可导出的分析内容");
      return;
    }

    // 收集附近的 table/chart tool_result 数据
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

      // 下载 PDF
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
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && <Spin style={{ display: "block", margin: "16px auto" }} />}
      </div>

      {/* File tags */}
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

      {/* Toolbar: export + input */}
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
