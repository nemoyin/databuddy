import { Layout, Typography, Button, List } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { ChatPanel } from "./components/ChatPanel";
import { useSession } from "./hooks/useSession";

const { Content, Sider } = Layout;
const { Title } = Typography;

function App() {
  const { sessions, currentSessionId, newSession, switchSession } = useSession();

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
                onClick={() => switchSession(item.id)}
                style={{
                  cursor: "pointer",
                  background: item.id === currentSessionId ? "#e6f4ff" : undefined,
                  borderRadius: 6,
                  padding: "4px 8px",
                }}
              >
                <List.Item.Meta
                  title={<span style={{ fontSize: 14 }}>{item.title}</span>}
                />
              </List.Item>
            )}
            style={{ flex: 1, overflow: "auto" }}
          />
        </div>
      </Sider>
      <Layout>
        <Content style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <ChatPanel />
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
