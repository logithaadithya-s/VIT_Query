import { GlassCard } from "@/components/GlassCard";
import { UploadForm } from "@/components/UploadForm";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Upload Paper</h1>
        <p className="mt-2 text-zinc-400">
          Add a research paper to the repository. Duplicates above 70% similarity are blocked automatically.
        </p>
      </div>
      <GlassCard>
        <UploadForm />
      </GlassCard>
    </div>
  );
}
