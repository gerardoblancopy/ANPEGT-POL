interface ScoreGaugeProps {
  score: number;
  label: string;
  size?: number;
}

function getColor(score: number): string {
  if (score >= 0.7) return 'var(--accent-green)';
  if (score >= 0.4) return 'var(--accent-amber)';
  return 'var(--accent-red)';
}

export default function ScoreGauge({ score, label, size = 140 }: ScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(1, score));
  const color = getColor(clamped);
  const radius = (size - 20) / 2;
  const cx = size / 2;
  const cy = size / 2 + 10;
  const circumference = Math.PI * radius;
  const offset = circumference * (1 - clamped);

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        {/* Background arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="rgba(148, 163, 184, 0.15)"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Foreground arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
        />
        {/* Score text */}
        <text
          x={cx}
          y={cy - 12}
          textAnchor="middle"
          fill="var(--text-primary)"
          fontSize="24"
          fontWeight="700"
        >
          {(clamped * 100).toFixed(0)}
        </text>
      </svg>
      <span className="text-sm text-[var(--text-secondary)] font-medium">{label}</span>
    </div>
  );
}
