"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Trash2, BookOpen, User, Building } from "lucide-react";
import { api, Paper } from "@/lib/api";
import { GlassCard } from "@/components/GlassCard";
import { formatDate } from "@/lib/utils";

export default function PapersPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api.getPapers().then(setPapers).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const remove = async (id: number) => {
    if (!confirm("Delete this paper?")) return;
    await api.deletePaper(id);
    load();
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-violet-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Research Papers</h1>
        <p className="mt-2 text-zinc-400">{papers.length} papers in the repository</p>
      </div>

      {papers.length === 0 ? (
        <GlassCard>
          <div className="py-12 text-center">
            <BookOpen className="mx-auto h-12 w-12 text-zinc-600" />
            <p className="mt-4 text-zinc-400">No papers yet. Upload your first paper to get started.</p>
          </div>
        </GlassCard>
      ) : (
        <div className="space-y-4">
          {papers.map((paper, i) => (
            <motion.div
              key={paper.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <GlassCard className="group transition hover:border-violet-500/20">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white">{paper.title}</h3>
                    <div className="mt-2 flex flex-wrap gap-4 text-sm text-zinc-400">
                      {paper.author && (
                        <span className="flex items-center gap-1">
                          <User className="h-3.5 w-3.5" /> {paper.author}
                        </span>
                      )}
                      {paper.department && (
                        <span className="flex items-center gap-1">
                          <Building className="h-3.5 w-3.5" /> {paper.department}
                        </span>
                      )}
                      <span>{paper.publication_year || "N/A"}</span>
                      <span>{formatDate(paper.created_at)}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="rounded-full bg-violet-500/20 px-3 py-1 text-xs font-medium text-violet-300">
                        {paper.primary_field}
                      </span>
                      {paper.keywords?.slice(0, 4).map((kw) => (
                        <span
                          key={kw}
                          className="rounded-full border border-white/10 px-3 py-1 text-xs text-zinc-400"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => remove(paper.id)}
                    className="rounded-xl border border-red-500/20 p-2.5 text-red-400 opacity-0 transition hover:bg-red-500/10 group-hover:opacity-100"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
