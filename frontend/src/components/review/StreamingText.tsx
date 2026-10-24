/** Streaming text component — renders text with a typing cursor effect. */

interface Props {
  text: string;
  isStreaming: boolean;
  className?: string;
}

export default function StreamingText({ text, isStreaming, className = "" }: Props) {
  if (!text && !isStreaming) return null;

  return (
    <div className={`whitespace-pre-wrap ${className}`}>
      {text}
      {isStreaming && <span className="cursor-blink" />}
    </div>
  );
}
