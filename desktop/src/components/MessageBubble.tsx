import { useState, useCallback } from "react";
import { Typography, Card, Table, Tag, Empty, Tooltip, message as antMsg } from "antd";
import { UserOutlined, RobotOutlined, ToolOutlined, FileOutlined, CopyOutlined, ReloadOutlined, LikeOutlined, DislikeOutlined, FilePdfOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChartRenderer } from "./ChartRenderer";
import type { ChatMessage } from "../hooks/useChat";

interface Props {
  message: ChatMessage;
  onReRun?: (question: string) => void;
  onExportPDF?: (content: string) => void;
}

const markdownStyles: React.CSSProperties = {
  fontSize: 14,
  lineHeight: 1.7,
};

/* Markdown 表格全局样式 */
const tableStyles = `
.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}
.markdown-body th, .markdown-body td {
  border: 1px solid #e8e8e8;
  padding: 6px 10px;
  text-align: left;
  vertical-align: top;
  white-space: normal;
  word-break: break-word;
}
.markdown-body th {
  background: #fafafa;
  font-weight: 600;
}
.markdown-body tr:nth-child(even) {
  background: #fafafa;
}
.markdown-body tr:hover {
  background: #f0f5ff;
}
.markdown-body p {
  margin: 0 0 6px 0;
}
`;
if (typeof document !== "undefined") {
  const styleTag = document.createElement("style");
  styleTag.textContent = tableStyles;
  document.head.appendChild(styleTag);
}

export function MessageBubble({ message, onReRun, onExportPDF }: Props) {
  const isUser = message.role === "user";
  const isTool = message.role === "tool";
  const isAssistant = !isUser && !isTool;

  const [liked, setLiked] = useState<"up" | "down" | null>(null);

  const icon = isUser ? <UserOutlined /> : isTool ? <ToolOutlined /> : <RobotOutlined />;
  const color = isUser ? "#e6f4ff" : isTool ? "#f6ffed" : "#fff";
  const maxWidth = isTool ? "90%" : "85%";

  const handleCopy = useCallback(() => {
    if (message.content) {
      navigator.clipboard.writeText(message.content).then(
        () => antMsg.success("已复制"),
        () => antMsg.error("复制失败"),
      );
    }
  }, [message.content]);

  return (
    <div style={{ display: "flex", gap: 12, marginBottom: 20, flexDirection: isUser ? "row-reverse" : "row" }}>
      <Tag style={{ borderRadius: "50%", width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        {icon}
      </Tag>
      <Card
        style={{ maxWidth, background: color, borderRadius: 12 }}
        styles={{ body: { padding: message.format === "table" ? "8px" : "8px 16px" } }}
      >
        {/* File attachments */}
        {message.files && message.files.length > 0 && (
          <div style={{ marginBottom: 8 }}>
            {message.files.map((f, i) => (
              <Tag key={i} icon={<FileOutlined />} style={{ marginBottom: 4 }}>{f.filename}</Tag>
            ))}
          </div>
        )}

        {/* Tool result: chart format */}
        {isTool && message.format === "chart" && message.data != null && (
          <ChartRenderer config={message.data as { chart_type: string; title: string; option: Record<string, unknown> }} />
        )}

        {/* Tool result: table format */}
        {isTool && message.format === "table" && message.data != null && renderTable(message.data)}

        {/* Tool result: text */}
        {isTool && message.format !== "table" && message.content && (
          <Typography.Paragraph style={{ margin: 0, whiteSpace: "pre-wrap" }}>{message.content}</Typography.Paragraph>
        )}

        {/* User message */}
        {isUser && message.content && (
          <Typography.Paragraph style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 14, lineHeight: 1.6 }}>
            {message.content}
          </Typography.Paragraph>
        )}

        {/* Assistant: markdown */}
        {isAssistant && message.content && (
          <div className="markdown-body" style={markdownStyles}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ children }) => (
                  <div style={{ overflowX: "auto", margin: "8px 0" }}>
                    <table style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: 13,
                      border: "1px solid #e8e8e8",
                    }}>
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th style={{
                    background: "#fafafa",
                    border: "1px solid #e8e8e8",
                    padding: "8px 12px",
                    fontWeight: 600,
                    textAlign: "center",
                    whiteSpace: "nowrap",
                  }}>
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td style={{
                    border: "1px solid #e8e8e8",
                    padding: "6px 12px",
                    textAlign: "center",
                    verticalAlign: "middle",
                  }}>
                    {children}
                  </td>
                ),
                tr: ({ children }) => (
                  <tr style={{ transition: "background 0.2s" }}>
                    {children}
                  </tr>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Assistant actions: copy, re-run, like, dislike */}
        {isAssistant && message.content && (
          <div style={{ display: "flex", gap: 4, marginTop: 10, paddingTop: 8, borderTop: "1px solid #f0f0f0", opacity: 0.5, transition: "opacity 0.2s" }}
            onMouseEnter={e => (e.currentTarget.style.opacity = "1")}
            onMouseLeave={e => (e.currentTarget.style.opacity = "0.5")}
          >
            <Tooltip title="复制">
              <CopyOutlined
                style={{ fontSize: 14, cursor: "pointer", padding: "2px 6px" }}
                onClick={handleCopy}
              />
            </Tooltip>
            {onReRun && (
              <Tooltip title="重新运行">
                <ReloadOutlined
                  style={{ fontSize: 14, cursor: "pointer", padding: "2px 6px" }}
                  onClick={() => onReRun(message.content)}
                />
              </Tooltip>
            )}
            {onExportPDF && (
              <Tooltip title="导出PDF">
                <FilePdfOutlined
                  style={{ fontSize: 14, cursor: "pointer", padding: "2px 6px", color: "#ff4d4f" }}
                  onClick={() => onExportPDF(message.content)}
                />
              </Tooltip>
            )}
            <Tooltip title={liked === "up" ? "已点赞" : "点赞"}>
              <LikeOutlined
                style={{ fontSize: 14, cursor: "pointer", padding: "2px 6px", color: liked === "up" ? "#1677ff" : undefined }}
                onClick={() => setLiked(liked === "up" ? null : "up")}
              />
            </Tooltip>
            <Tooltip title={liked === "down" ? "已点踩" : "点踩"}>
              <DislikeOutlined
                style={{ fontSize: 14, cursor: "pointer", padding: "2px 6px", color: liked === "down" ? "#ff4d4f" : undefined }}
                onClick={() => setLiked(liked === "down" ? null : "down")}
              />
            </Tooltip>
          </div>
        )}
      </Card>
    </div>
  );
}

function renderTable(data: unknown) {
  const d = data as Record<string, unknown>;
  const rows = (d.rows as Record<string, unknown>[]) || [];
  const columns = (d.columns as string[]) || [];
  const totalRows = d.total_rows as number;

  if (!rows.length || !columns.length) {
    return <Empty description="无数据" />;
  }

  return (
    <div>
      {totalRows != null && (
        <Typography.Text type="secondary" style={{ padding: "4px 8px", display: "block" }}>
          {totalRows > (rows.length) ? `共 ${totalRows} 行，显示前 ${rows.length} 行` : `共 ${rows.length} 行`}
        </Typography.Text>
      )}
      <Table
        dataSource={rows.map((row, i) => ({ ...row, _key: i }))}
        columns={columns.map(k => ({ title: k, dataIndex: k, key: k }))}
        size="small"
        pagination={rows.length > 20 ? { pageSize: 20 } : false}
        rowKey="_key"
        scroll={{ x: "max-content" }}
      />
    </div>
  );
}
