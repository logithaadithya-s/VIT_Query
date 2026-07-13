"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const COLORS = ["#8b5cf6", "#06b6d4", "#a78bfa", "#22d3ee", "#c084fc", "#67e8f9"];

interface Props {
  data: { field: string; count: number }[];
}

export function FieldBarChart({ data }: Props) {
  const chartData = data.filter((d) => d.count > 0).slice(0, 8);

  if (!chartData.length) {
    return <p className="py-8 text-center text-sm text-zinc-500">No field data yet</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 20 }}>
        <XAxis type="number" stroke="#52525b" fontSize={12} />
        <YAxis
          type="category"
          dataKey="field"
          width={140}
          stroke="#52525b"
          fontSize={11}
          tick={{ fill: "#a1a1aa" }}
        />
        <Tooltip
          contentStyle={{
            background: "rgba(0,0,0,0.85)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "12px",
            color: "#fff",
          }}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]}>
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
