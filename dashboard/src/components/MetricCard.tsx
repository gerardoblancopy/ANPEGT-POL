import { TrendingUp, TrendingDown } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { cn } from '../lib/utils';

interface MetricCardProps {
  label: string;
  value: string;
  delta?: number;
  sparklineData?: { v: number }[];
  className?: string;
  accentColor?: string;
}

export default function MetricCard({
  label,
  value,
  delta,
  sparklineData,
  className,
  accentColor = '#3b82f6',
}: MetricCardProps) {
  return (
    <div
      className={cn(
        'glass-card p-5 flex flex-col gap-3 transition-all duration-200 glass-card-hover',
        className,
      )}
    >
      <span className="text-sm text-[var(--text-secondary)] font-medium">
        {label}
      </span>
      <div className="flex items-end justify-between gap-4">
        <span className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">
          {value}
        </span>
        {delta !== undefined && (
          <span
            className={cn(
              'flex items-center gap-1 text-sm font-medium',
              delta >= 0 ? 'text-[var(--accent-green)]' : 'text-[var(--accent-red)]',
            )}
          >
            {delta >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {delta >= 0 ? '+' : ''}
            {(delta * 100).toFixed(1)}%
          </span>
        )}
      </div>
      {sparklineData && sparklineData.length > 1 && (
        <div className="h-10 mt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sparklineData}>
              <Line
                type="monotone"
                dataKey="v"
                stroke={accentColor}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
