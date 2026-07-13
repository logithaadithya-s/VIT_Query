"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileSearch, Loader2, AlertTriangle, CheckCircle } from "lucide-react";
import { api, PlagiarismReport } from "@/lib/api";
import { GlassCard } from "@/components/GlassCard";

export default function PlagiarismPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<PlagiarismReport | null>(null);

  const runCheck = async () => {
    if (!file) return;
    setLoading(true);
    setReport(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const result = await api.checkPlagiarism(form);
      setReport(result);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const statusColor =
    report?.status === "duplicate_detected"
      ? "text-red-400"
      : report?.status === "clear"
      ? "text-emerald-400"
      : "text-amber-400";

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Plagiarism Check</h1>
        <p className="mt-2 text-zinc-400">Compare a document against all stored papers without saving it.</p>
      </div>

      <GlassCard>
        <div className="space-y-6">
        <label className="block cursor-pointer">
          <div className="flex flex-col items-center gap-3 rounded-2xl border-2 border-dashed border-white/15 bg-white/[0.02] p-10 transition hover:border-violet-500/40">
            <FileSearch className="h-10 w-10 text-violet-400" />
            <span className="font-medium text-white">{file ? file.name : "Choose a document"}</span>
          </div>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={(e) => { setFile(e.target.files?.[0] || null); setReport(null); }}
          />
        </label>

          <button
            onClick={runCheck}
            disabled={!file || loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 py-4 font-semibold text-white disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileSearch className="h-5 w-5" />}
            {loading ? "Checking..." : "Run Plagiarism Check"}
          </button>
        </div>
      </GlassCard>

      <AnimatePresence>
        {report && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard
              title={`Result: ${report.status.replace(/_/g, " ")}`}
              subtitle={`Highest similarity: ${report.highest_similarity}%`}
            >
              {report.matches.length === 0 ? (
                <div className="flex items-center gap-3 text-emerald-400">
                  <CheckCircle className="h-6 w-6" />
                  <span>No significant similarity found</span>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className={`font-medium capitalize ${statusColor}`}>
                    {report.total_matches} matching paper(s) found
                  </p>
                  {report.matches.map((match) => (
                    <div
                      key={match.paper_id}
                      className={`rounded-xl border p-4 ${
                        match.is_duplicate
                          ? "border-red-500/30 bg-red-500/5"
                          : "border-amber-500/20 bg-amber-500/5"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {match.is_duplicate && <AlertTriangle className="h-4 w-4 text-red-400" />}
                        <p className="font-medium text-white">{match.title}</p>
                        <span className="ml-auto rounded-full bg-white/10 px-2 py-0.5 text-sm text-zinc-300">
                          {match.similarity_percent}%
                        </span>
                      </div>
                      {match.matching_passages?.slice(0, 2).map((p, i) => (
                        <p key={i} className="mt-2 text-sm italic text-zinc-500">
                          &ldquo;{p.source_excerpt.slice(0, 200)}...&rdquo;
                        </p>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
