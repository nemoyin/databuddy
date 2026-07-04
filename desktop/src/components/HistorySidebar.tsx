import { List, Button, Typography } from "antd";
import { PlusOutlined, MessageOutlined } from "@ant-design/icons";
import { useSession } from "../hooks/useSession";

interface Props {
  manager: ReturnType<typeof useSession>;
}

export function HistorySidebar({ manager }: Props) {
  return (
    <div>
      <Button
        type="primary"
        block
        icon={<PlusOutlined />}
        onClick={() => manager.newSession()}
        style={{ marginBottom: 16 }}
      >
        新建会话
      </Button>
      <List
        dataSource={manager.sessions}
        renderItem={item => (
          <List.Item
            onClick={() => manager.switchSession(item.id)}
            style={{
              cursor: "pointer",
              background:
                manager.currentSessionId === item.id ? "#e6f4ff" : "transparent",
              borderRadius: 6,
              padding: "8px 12px",
            }}
          >
            <List.Item.Meta
              avatar={<MessageOutlined />}
              title={<Typography.Text ellipsis>{item.title}</Typography.Text>}
              description={item.created_at?.slice(0, 10)}
            />
          </List.Item>
        )}
      />
    </div>
  );
}
