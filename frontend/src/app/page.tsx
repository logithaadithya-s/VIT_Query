"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Building2, Layers, TrendingUp } from "lucide-react";
import { api, AnalyticsOverview } from "@/lib/api";
import { StatCard } from "@/components/StatCard";
import { GlassCard } from "@/components/GlassCard";
import { FieldBarChart } from "@/components/FieldBarChart";

export default function DashboardPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOverview().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-violet-500 border-t-transparent" />
      </div>
    );
  }

  const summary = data?.summary;

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Research{" "}
          <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
            Intelligence
          </span>
        </h1>
        <p className="mt-2 text-zinc-400">
          Monitor your institution&apos;s research landscape, detect duplicates, and find new directions.
        </p>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Papers"
          value={summary?.total_papers ?? 0}
          icon={BookOpen}
          gradient="bg-gradient-to-br from-violet-600 to-violet-800"
          delay={0}
        />
        <StatCard
          label="Research Fields"
          value={summary?.unique_fields ?? 0}
          icon={Layers}
          gradient="bg-gradient-to-br from-cyan-600 to-cyan-800"
          delay={0.1}
        />
        <StatCard
          label="Departments"
          value={summary?.departments_represented ?? 0}
          icon={Building2}
          gradient="bg-gradient-to-br from-fuchsia-600 to-fuchsia-800"
          delay={0.2}
        />
        <StatCard
          label="Opportunities"
          value={data?.opportunity_fields?.length ?? 0}
          icon={TrendingUp}
          gradient="bg-gradient-to-br from-amber-600 to-orange-700"
          delay={0.3}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <GlassCard title="Most Researched Fields" subtitle="Active domains in your repository">
          <FieldBarChart data={data?.top_researched_fields ?? []} />
        </GlassCard>

        <GlassCard title="Research Opportunities" subtitle="Emerging areas with high potential">
          <div className="space-y-3">
            {(data?.opportunity_fields ?? []).slice(0, 5).map((item, i) => (
              <motion.div
                key={item.field}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="rounded-xl border border-white/5 bg-white/[0.03] p-4"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-cyan-500/20 px-2 py-0.5 text-xs font-medium text-cyan-300">
                    {item.signal_strength}
                  </span>
                  <p className="font-medium text-white">{item.field}</p>
                </div>
                <p className="mt-2 text-sm text-zinc-400">{item.reason}</p>
              </motion.div>
            ))}
            {!data?.opportunity_fields?.length && (
              <p className="py-6 text-center text-sm text-zinc-500">Upload papers to detect opportunities</p>
            )}
          </div>
        </GlassCard>
      </div>

      <GlassCard title="Trending Keywords">
        <div className="flex flex-wrap gap-2">
          {(data?.trending_keywords ?? []).map(({ keyword, count }) => (
            <span
              key={keyword}
              className="rounded-full border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-sm text-violet-200"
            >
              {keyword} <span className="text-violet-400">({count})</span>
            </span>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
