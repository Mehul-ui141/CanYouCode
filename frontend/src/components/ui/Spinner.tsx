/** Spinner — pulsing loading indicator. */

export default function Spinner({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <div className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse" />
      <div className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse delay-75" />
      <div className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse delay-150" />
    </div>
  );
}
