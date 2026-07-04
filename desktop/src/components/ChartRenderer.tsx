import { useRef, useEffect, useState } from "react";
import * as echarts from "echarts";

interface ChartConfig {
  chart_type: string;
  title: string;
  option: Record<string, unknown>;
}

interface Props {
  config: ChartConfig;
  height?: number;
}

export function ChartRenderer({ config, height = 400 }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<echarts.ECharts | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartRef.current || !config?.option) return;
    setError(null);

    // 如果实例已存在，销毁重建
    if (instanceRef.current) {
      instanceRef.current.dispose();
    }

    try {
      const instance = echarts.init(chartRef.current);
      instanceRef.current = instance;

      const fullOption = {
        title: { text: config.title, left: "center", textStyle: { fontSize: 16 } },
        tooltip: { trigger: "axis" as const },
        ...config.option,
      };

      instance.setOption(fullOption, true);

      const handleResize = () => instance.resize();
      window.addEventListener("resize", handleResize);

      // 延迟 resize 确保容器已渲染
      setTimeout(() => instance.resize(), 100);

      return () => {
        window.removeEventListener("resize", handleResize);
        instance.dispose();
        instanceRef.current = null;
      };
    } catch (e) {
      setError(`图表渲染失败: ${e instanceof Error ? e.message : "未知错误"}`);
    }
  }, [config, height]);

  if (!config || !config.option) {
    return <p style={{ color: "#999", textAlign: "center", padding: 40 }}>图表配置为空</p>;
  }

  if (error) {
    return <p style={{ color: "#ff4d4f", textAlign: "center", padding: 40 }}>{error}</p>;
  }

  return (
    <div style={{ padding: 16, background: "#fff", borderRadius: 8, width: "100%" }}>
      <div ref={chartRef} style={{ width: "100%", height }} />
    </div>
  );
}
