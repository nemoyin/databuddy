import { Table, Tag } from "antd";
import type { ColumnsType } from "antd/es/table";

interface Props {
  data: Record<string, unknown>[];
  maxHeight?: number;
}

export function DataTable({ data, maxHeight = 400 }: Props) {
  if (!data || data.length === 0) {
    return <p style={{ color: "#999" }}>无数据</p>;
  }

  const columns: ColumnsType<Record<string, unknown>> = Object.keys(data[0]).map(key => ({
    title: key,
    dataIndex: key,
    key,
    ellipsis: true,
    sorter: (a: Record<string, unknown>, b: Record<string, unknown>) => {
      const va = a[key], vb = b[key];
      if (typeof va === "number" && typeof vb === "number") return va - vb;
      return String(va).localeCompare(String(vb));
    },
    render: (val: unknown) => {
      if (val === null || val === undefined) return <Tag>NULL</Tag>;
      if (typeof val === "boolean") return val ? "是" : "否";
      return String(val);
    },
  }));

  return (
    <Table
      columns={columns}
      dataSource={data.map((row, i) => ({ ...row, _key: i }))}
      rowKey="_key"
      size="small"
      scroll={{ x: "max-content", y: maxHeight }}
      pagination={data.length > 20 ? { pageSize: 20, showSizeChanger: true } : false}
      bordered
    />
  );
}
