import { useState } from "react";
import { Layout, Typography, Button, List, Tooltip, message } from "antd";
import { PlusOutlined, MessageOutlined, CopyOutlined, DeleteOutlined } from "@ant-design/icons";
import { ChatPanel } from "./components/ChatPanel";
import { useSession } from "./hooks/useSession";

const { Content, Sider } = Layout;
const { Title } = Typography;

function App() {
  const { sessions, currentSessionId, newSession, switchSession, removeSession } = useSession();
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <Layout style={{ height: "100vh" }}>
      <Sider width={280} theme="light" style={{ borderRight: "1px solid #f0f0f0" }}>
        <div style={{ padding: 16, display: "flex", flexDirection: "column", height: "100%" }}>
          <Title level={4} style={{ margin: 0, marginBottom: 16 }}>JWBuddy</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => newSession()}
            block
            style={{ marginBottom: 16 }}
          >
            新会话
          </Button>
          <List
            size="small"
            dataSource={sessions}
            renderItem={item => (
              <List.Item
                key={item.id}
                onClick={() => switchSession(item.id)}
                onMouseEnter={() => setHoveredId(item.id)}
                onMouseLeave={() => setHoveredId(null)}
                style={{
                  cursor: "pointer",
                  background: item.id === currentSessionId ? "#e6f4ff" : undefined,
                  borderRadius: 6,
                  padding: "4px 8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <List.Item.Meta
                  avatar={<MessageOutlined />}
                  title={
                    <Typography.Text
                      ellipsis
                      style={{ maxWidth: hoveredId === item.id ? 120 : 180, fontSize: 14 }}
                    >
                      {item.title}
                    </Typography.Text>
                  }
                  description={item.created_at?.slice(0, 10)}
                  style={{ margin: 0, minWidth: 0 }}
                />
                {hoveredId === item.id && (
                  <span style={{ display: "flex", gap: 2, flexShrink: 0 }} onClick={e => e.stopPropagation()}>
                    <Tooltip title="复制问题">
                      <CopyOutlined
                        style={{ fontSize: 13, cursor: "pointer", padding: "2px 4px", color: "#888" }}
                        onClick={() => {
                          navigator.clipboard.writeText(item.title).then(
                            () => message.success("已复制"),
                            () => message.error("复制失败"),
                          );
                        }}
                      />
                    </Tooltip>
                    <Tooltip title="删除会话">
                      <DeleteOutlined
                        style={{ fontSize: 13, cursor: "pointer", padding: "2px 4px", color: "#888" }}
                        onClick={() => removeSession(item.id)}
                      />
                    </Tooltip>
                  </span>
                )}
              </List.Item>
            )}
            style={{ flex: 1, overflow: "auto" }}
          />
        </div>
      </Sider>
      <Layout>
        <Content style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <ChatPanel
            sessionId={currentSessionId}
            onNewSession={() => newSession()}
          />
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
