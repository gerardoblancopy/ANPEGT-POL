import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useCycle } from '../components/Layout';
import { fetchPriorities } from '../lib/api';

interface Priority {
  topic: string;
  weight: number;
  prev_weight?: number;
}

interface PrioritiesData {
  priorities?: Priority[];
  evolution?: { cycle: number; [topic: string]: number }[];
}

export default function PrioritiesPage() {
  const { cycle, cycles } = useCycle();
  const [data, setData] = useState<PrioritiesData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchPriorities(cycle)
      .then((d) => setData(d as PrioritiesData))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [cycle]);

  const priorities: Priority[] = data?.priorities ?? [
    { topic: 'Empleo y economia', weight: 0.92, prev_weight: 0.88 },
    { topic: 'Sanidad publica', weight: 0.87, prev_weight: 0.85 },
    { topic: 'Educacion', weight: 0.81, prev_weight: 0.83 },
    { topic: 'Seguridad ciudadana', weight: 0.76, prev_weight: 0.72 },
    { topic: 'Vivienda', weight: 0.71, prev_weight: 0.65 },
    { topic: 'Medio ambiente', weight: 0.68, prev_weight: 0.70 },
    { topic: 'Transporte', weight: 0.59, prev_weight: 0.55 },
    { topic: 'Cultura y deporte', weight: 0.45, prev_weight: 0.48 },
  ];

  const evolution = data?.evolution ?? [
    { cycle: 1, empleo: 0.80, sanidad: 0.82, educacion: 0.78, seguridad: 0.65, vivienda: 0.55 },
    { cycle: 2, empleo: 0.85, sanidad: 0.84, educacion: 0.80, seguridad: 0.70, vivienda: 0.60 },
    { cycle: 3, empleo: 0.88, sanidad: 0.85, educacion: 0.83, seguridad: 0.72, vivienda: 0.65 },
    { cycle: 4, empleo: 0.92, sanidad: 0.87, educacion: 0.81, seguridad: 0.76, vivienda: 0.71 },
  ];

  const barData = priorities
    .slice()
    .sort((a, b) => b.weight - a.weight)
    .map((p) => ({ name: p.topic, peso: +(p.weight * 100).toFixed(1) }));

  const evoKeys = evolution.length > 0
    ? Object.keys(evolution[0]).filter((k) => k !== 'cycle')
    : [];

  const AREA_COLORS = ['#3b82f6', '#6366f1', '#22c55e', '#f59e0b', '#ef4444'];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="glass-card h-80 animate-pulse-subtle" />
        <div className="glass-card h-64 animate-pulse-subtle" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[var(--text-primary)]">Prioridades ANP</h1>

      {/* Horizontal bar chart */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
          Peso de Prioridades - Ciclo {cycle}
        </h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
              <XAxis type="number" stroke="var(--text-secondary)" fontSize={12} domain={[0, 100]} />
              <YAxis
                type="category"
                dataKey="name"
                stroke="var(--text-secondary)"
                fontSize={12}
                width={140}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid rgba(148,163,184,0.2)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                }}
                formatter={(v) => [`${v}%`, 'Peso']}
              />
              <Bar dataKey="peso" fill="var(--accent-blue)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Evolution area chart */}
      {cycles.length > 1 && (
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
            Evolucion de Prioridades
          </h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={evolution}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                <XAxis
                  dataKey="cycle"
                  stroke="var(--text-secondary)"
                  fontSize={12}
                  tickFormatter={(v: number) => `C${v}`}
                />
                <YAxis
                  stroke="var(--text-secondary)"
                  fontSize={12}
                  domain={[0, 1]}
                  tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid rgba(148,163,184,0.2)',
                    borderRadius: '8px',
                    color: 'var(--text-primary)',
                  }}
                  formatter={(v) => [`${(Number(v) * 100).toFixed(1)}%`]}
                />
                {evoKeys.map((key, i) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={AREA_COLORS[i % AREA_COLORS.length]}
                    fill={AREA_COLORS[i % AREA_COLORS.length]}
                    fillOpacity={0.1}
                    strokeWidth={2}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
          Detalle de Prioridades
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Tema</th>
                <th className="text-right py-3 px-4 text-[var(--text-secondary)] font-medium">Peso Actual</th>
                <th className="text-right py-3 px-4 text-[var(--text-secondary)] font-medium">Peso Anterior</th>
                <th className="text-right py-3 px-4 text-[var(--text-secondary)] font-medium">Delta</th>
              </tr>
            </thead>
            <tbody>
              {priorities.map((p) => {
                const delta = p.prev_weight !== undefined ? p.weight - p.prev_weight : 0;
                return (
                  <tr key={p.topic} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4 text-[var(--text-primary)]">{p.topic}</td>
                    <td className="py-3 px-4 text-right text-[var(--text-primary)] font-medium">
                      {(p.weight * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-right text-[var(--text-secondary)]">
                      {p.prev_weight !== undefined ? `${(p.prev_weight * 100).toFixed(1)}%` : '-'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`inline-flex items-center gap-1 ${
                        delta > 0
                          ? 'text-[var(--accent-green)]'
                          : delta < 0
                            ? 'text-[var(--accent-red)]'
                            : 'text-[var(--text-secondary)]'
                      }`}>
                        {delta > 0 ? <TrendingUp className="w-3.5 h-3.5" /> : delta < 0 ? <TrendingDown className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
                        {delta > 0 ? '+' : ''}{(delta * 100).toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
