"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [department, setDepartment] = useState("");
  const [year, setYear] = useState("2025");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<"success" | "error" | null>(null);
  const [message, setMessage] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setResult(null);

    const form = new FormData();
    form.append("file", file);
    form.append("title", title);
    form.append("author", author);
    form.append("department", department);
    if (year) form.append("publication_year", year);

    try {
      const data = await api.uploadPaper(form);
      setResult("success");
      setMessage(
        `"${data.title}" uploaded · Field: ${data.primary_field} · Similarity: ${data.plagiarism_report?.highest_similarity ?? 0}%`
      );
      setFile(null);
      setTitle("");
      setAuthor("");
      setDepartment("");
    } catch (err: unknown) {
      setResult("error");
      const e = err as { data?: { detail?: { message?: string; plagiarism_report?: { matches: { title: string; similarity_percent: number }[] } } } };
      let msg = e?.data?.detail?.message || "Upload failed";
      const matches = e?.data?.detail?.plagiarism_report?.matches;
      if (matches?.length) {
        msg += " — Matches: " + matches.map((m) => `${m.title} (${m.similarity_percent}%)`).join(", ");
      }
      setMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-6">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`relative rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-300 ${
          dragOver
            ? "border-cyan-400 bg-cyan-500/10"
            : file
            ? "border-violet-500/50 bg-violet-500/5"
            : "border-white/15 bg-white/[0.02] hover:border-violet-500/40 hover:bg-white/[0.04]"
        }`}
      >
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="absolute inset-0 cursor-pointer opacity-0"
        />
        {file ? (
          <div className="flex flex-col items-center gap-3">
            <FileText className="h-12 w-12 text-violet-400" />
            <p className="font-medium text-white">{file.name}</p>
            <p className="text-sm text-zinc-400">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="rounded-2xl bg-gradient-to-br from-violet-600/30 to-cyan-500/20 p-4">
              <Upload className="h-8 w-8 text-violet-300" />
            </div>
            <p className="font-medium text-white">Drop your research paper here</p>
            <p className="text-sm text-zinc-400">PDF, DOCX, or TXT · Max recommended 20MB</p>
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {[
          { label: "Title (optional)", value: title, set: setTitle, placeholder: "Auto-detected from document" },
          { label: "Author", value: author, set: setAuthor, placeholder: "Dr. Jane Smith" },
          { label: "Department", value: department, set: setDepartment, placeholder: "Computer Science" },
          { label: "Publication Year", value: year, set: setYear, placeholder: "2025" },
        ].map(({ label, value, set, placeholder }) => (
          <div key={label}>
            <label className="mb-1.5 block text-sm font-medium text-zinc-400">{label}</label>
            <input
              value={value}
              onChange={(e) => set(e.target.value)}
              placeholder={placeholder}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-zinc-600 outline-none transition focus:border-violet-500/50 focus:ring-2 focus:ring-violet-500/20"
            />
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={!file || loading}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-6 py-4 font-semibold text-white shadow-lg shadow-violet-500/25 transition hover:shadow-violet-500/40 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Analyzing & uploading...
          </>
        ) : (
          <>
            <Upload className="h-5 w-5" />
            Upload & Analyze
          </>
        )}
      </button>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`flex items-start gap-3 rounded-xl border p-4 ${
              result === "success"
                ? "border-emerald-500/30 bg-emerald-500/10"
                : "border-red-500/30 bg-red-500/10"
            }`}
          >
            {result === "success" ? (
              <CheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
            ) : (
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
            )}
            <p className={`text-sm ${result === "success" ? "text-emerald-200" : "text-red-200"}`}>
              {message}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </form>
  );
}
