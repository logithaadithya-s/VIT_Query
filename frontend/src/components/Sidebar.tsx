"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Brain,
  FileSearch,
  LayoutDashboard,
  Sparkles,
  Upload,
  BookOpen,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/plagiarism", label: "Plagiarism", icon: FileSearch },
  { href: "/papers", label: "Papers", icon: BookOpen },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/agent", label: "AI Agent", icon: Brain },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-white/10 bg-black/40 backdrop-blur-2xl">
      <div className="border-b border-white/10 p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 shadow-lg shadow-violet-500/30">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold tracking-tight text-white">ResearchIQ</p>
            <p className="text-xs text-zinc-400">Intelligence Platform</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200",
                active
                  ? "bg-gradient-to-r from-violet-600/30 to-cyan-500/20 text-white shadow-inner shadow-violet-500/10"
                  : "text-zinc-400 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon
                className={cn(
                  "h-4 w-4 transition-colors",
                  active ? "text-cyan-400" : "text-zinc-500 group-hover:text-violet-400"
                )}
              />
              {label}
              {active && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-cyan-400 shadow shadow-cyan-400/80" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 p-4">
        <div className="rounded-xl bg-gradient-to-br from-violet-600/20 to-cyan-500/10 p-4 ring-1 ring-white/10">
          <p className="text-xs font-semibold text-violet-300">AI Research Agent</p>
          <p className="mt-1 text-xs leading-relaxed text-zinc-400">
            Discover gaps & opportunities in your research corpus.
          </p>
          <Link
            href="/agent"
            className="mt-3 inline-flex text-xs font-medium text-cyan-400 hover:text-cyan-300"
          >
            Run analysis →
          </Link>
        </div>
      </div>
    </aside>
  );
}
