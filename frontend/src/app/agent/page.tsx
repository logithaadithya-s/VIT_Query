"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Sparkles,
  TrendingUp,
  Target,
  Lightbulb,
  RefreshCw,
  Zap,
  Bot,
} from "lucide-react";
import { api, AgentInsights } from "@/lib/api";
import { GlassCard } from "@/components/GlassCard";

export default function AgentPage() {
  const [insights, setInsights] = useState<AgentInsights | null>(null);
  const [loading, setLoading] = useState(true);

  const run = () => {
    setLoading(true);
    api.getAgentInsights().then(setInsights).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { run(); }, []);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 p-2.5">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">AI Research Agent</h1>
              <p className="mt-1 text-zinc-400">
                Analyzes what&apos;s being worked on vs. what needs attention
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={run}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/10 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Re-run Analysis
        </button>
      </div>

      {loading && !insights ? (
        <div className="flex h-[50vh] flex-col items-center justify-center gap-4">
          <div className="relative">
            <div className="h-16 w-16 animate-spin rounded-full border-2 border-violet-500 border-t-transparent" />
            <Sparkles className="absolute inset-0 m-auto h-6 w-6 text-violet-400" />
          </div>
          <p className="text-zinc-400">Agent is analyzing your research corpus...</p>
        </div>
      ) : insights ? (
        <>
          {/* Agent badge + executive summary */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="border-violet-500/20 bg-gradient-to-br from-violet-600/10 to-cyan-500/5">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-violet-400" />
                <span className="rounded-full bg-violet-500/20 px-3 py-1 text-xs font-medium text-violet-300">
                  {insights.agent_label}
                </span>
              </div>
              <p className="mt-4 text-lg leading-relaxed text-zinc-200">{insights.executive_summary}</p>
            </GlassCard>
          </motion.div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Active research */}
            <GlassCard title="Areas Being Worked On" subtitle="Active research domains">
              <div className="space-y-4">
                {insights.active_research_areas.map((area, i) => (
                  <motion.div
                    key={area.field}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="rounded-xl border border-emerald-500/15 bg-emerald-500/5 p-4"
                  >
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-emerald-400" />
                      <p className="font-semibold text-white">{area.field}</p>
                      <span className="ml-auto text-sm text-emerald-400">{area.paper_count} papers</span>
                    </div>
                    <p className="mt-2 text-sm text-zinc-400">{area.summary}</p>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {area.key_themes?.map((t) => (
                        <span key={t} className="rounded-full bg-white/5 px-2 py-0.5 text-xs text-zinc-400">
                          {t}
                        </span>
                      ))}
                    </div>
                  </motion.div>
                ))}
                {!insights.active_research_areas.length && (
                  <p className="text-sm text-zinc-500">Upload papers to identify active areas</p>
                )}
              </div>
            </GlassCard>

            {/* Underexplored */}
            <GlassCard title="Areas That Need Work" subtitle="Gaps with research scope">
              <div className="space-y-4">
                {insights.underexplored_areas.slice(0, 6).map((area, i) => (
                  <motion.div
                    key={area.field}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="rounded-xl border border-amber-500/15 bg-amber-500/5 p-4"
                  >
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-amber-400" />
                      <p className="font-semibold text-white">{area.field}</p>
                      <span className="ml-auto text-sm text-amber-400">{area.paper_count} papers</span>
                    </div>
                    <p className="mt-2 text-sm text-zinc-400">{area.gap_analysis}</p>
                    <p className="mt-2 text-sm text-cyan-300/80">{area.research_scope}</p>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </div>

          {/* Emerging opportunities */}
          <GlassCard title="Emerging Opportunities" subtitle="New directions to explore">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {insights.emerging_opportunities.map((opp, i) => (
                <motion.div
                  key={opp.field}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="rounded-xl border border-violet-500/15 bg-violet-500/5 p-4"
                >
                  <div className="flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-violet-400" />
                    <p className="font-medium text-white">{opp.field}</p>
                  </div>
                  <p className="mt-2 text-sm text-zinc-400">{opp.rationale}</p>
                  <ul className="mt-3 space-y-1">
                    {opp.suggested_projects.map((p) => (
                      <li key={p} className="text-xs text-cyan-300/70">→ {p}</li>
                    ))}
                  </ul>
                </motion.div>
              ))}
            </div>
          </GlassCard>

          {/* Strategic recommendations */}
          <GlassCard title="Strategic Recommendations">
            <div className="space-y-3">
              {insights.strategic_recommendations.map((rec, i) => (
                <div key={i} className="flex items-start gap-3 rounded-xl bg-white/[0.03] p-4">
                  <Zap className="mt-0.5 h-4 w-4 shrink-0 text-cyan-400" />
                  <p className="text-sm text-zinc-300">{rec}</p>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Agent integration suggestions */}
          <GlassCard
            title="Recommended Agents to Integrate"
            subtitle="Upgrade analysis with these AI agents"
          >
            <div className="grid gap-4 sm:grid-cols-2">
              {insights.integration_suggestions.map((agent) => (
                <div
                  key={agent.name}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-violet-500/30"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-white">{agent.name}</p>
                    <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-zinc-400">
                      {agent.type}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-zinc-400">{agent.best_for}</p>
                  <p className="mt-3 rounded-lg bg-black/30 p-3 font-mono text-xs text-cyan-300/80">
                    {agent.setup}
                  </p>
                  {agent.env_var && (
                    <p className="mt-2 text-xs text-violet-400">Env: {agent.env_var}</p>
                  )}
                </div>
              ))}
            </div>
          </GlassCard>
        </>
      ) : null}
    </div>
  );
}
