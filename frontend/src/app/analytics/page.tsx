"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { api, AnalyticsOverview } from "@/lib/api";
import { GlassCard } from "@/components/GlassCard";
import { FieldBarChart } from "@/components/FieldBarChart";

const COLORS = ["#8b5cf6", "#06b6d4", "#a78bfa", "#22d3ee", "#f472b6", "#fbbf24", "#34d399"];

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);

  useEffect(() => {
    api.getOverview().then(setData).catch(console.error);
  }, []);

  const pieData = (data?.field_distribution ?? []).filter((d) => d.count > 0);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Field Analytics</h1>
        <p className="mt-2 text-zinc-400">Deep dive into research distribution and gaps</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <GlassCard title="Field Distribution">
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="count"
                  nameKey="field"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={110}
                  paddingAngle={3}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "rgba(0,0,0,0.9)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 12,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-12 text-center text-zinc-500">No data yet</p>
          )}
        </GlassCard>

        <GlassCard title="Activity by Field">
          <FieldBarChart data={data?.field_distribution ?? []} />
        </GlassCard>
      </div>

      <GlassCard title="Under-Explored Fields" subtitle="Areas with scope for new research">
        <div className="grid gap-3 sm:grid-cols-2">
          {(data?.underexplored_fields ?? []).map((item, i) => (
            <motion.div
              key={item.field}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.04 }}
              className="rounded-xl border border-cyan-500/10 bg-cyan-500/5 p-4"
            >
              <div className="flex items-center justify-between">
                <p className="font-medium text-white">{item.field}</p>
                <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-zinc-400">
                  {item.count} papers
                </span>
              </div>
              <p className="mt-2 text-sm text-zinc-400">{item.scope_note}</p>
            </motion.div>
          ))}
        </div>
      </GlassCard>

      <GlassCard title="Department Activity">
        <div className="flex flex-wrap gap-3">
          {(data?.department_activity ?? []).map(({ department, count }) => (
            <div
              key={department}
              className="rounded-xl border border-white/10 bg-white/5 px-5 py-3"
            >
              <p className="text-sm text-zinc-400">{department}</p>
              <p className="text-2xl font-bold text-white">{count}</p>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
