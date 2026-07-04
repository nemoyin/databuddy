import { Typography, Card, Table, Tag, Empty } from "antd";
import { UserOutlined, RobotOutlined, ToolOutlined, FileOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import { ChartRenderer } from "./ChartRenderer";
import type { ChatMessage } from "../hooks/useChat";

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const isTool = message.role === "tool";

  const icon = isUser ? <UserOutlined /> : isTool ? <ToolOutlined /> : <RobotOutlined />;
  const color = isUser ? "#e6f4ff" : isTool ? "#f6ffed" : "#fff";
  const maxWidth = isTool ? "90%" : "85%";

  return (
    <div style={{ display: "flex", gap: 12, marginBottom: 16, flexDirection: isUser ? "row-reverse" : "row" }}>
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

        {/* Assistant: markdown */}
        {!isTool && message.content && (
          <div className="markdown-body">
            <ReactMarkdown>{message.content}</ReactMarkdown>
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
