import { useState } from "react";
import { Modal, Form, Input, message } from "antd";

const API_BASE = "http://localhost:8000";

interface Props {
  open: boolean;
  onClose: () => void;
}

export function DataSourceDialog({ open, onClose }: Props) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    const values = await form.validateFields();
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/admin/datasources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (resp.ok) {
        message.success("数据源连接成功");
        onClose();
      } else {
        message.error("连接失败");
      }
    } catch {
      message.error("连接失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="添加数据源"
      open={open}
      onCancel={onClose}
      onOk={handleSubmit}
      confirmLoading={loading}
    >
      <Form form={form} layout="vertical">
        <Form.Item name="name" label="数据源名称" rules={[{ required: true }]}>
          <Input placeholder="例如: 信访数据库" />
        </Form.Item>
        <Form.Item name="url" label="连接字符串" rules={[{ required: true }]}>
          <Input.TextArea
            placeholder="postgresql+asyncpg://user:pass@host:5432/db"
            rows={3}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}
