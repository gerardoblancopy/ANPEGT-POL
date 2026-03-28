import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { AlertTriangle } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ScoreGauge from '../components/ScoreGauge';
import { useCycle } from '../components/Layout';
import { fetchOverview } from '../lib/api';

interface OverviewData {
  fitness_global?: number;
  coherencia?: number;
  alineacion?: number;
  viabilidad?: number;
  fitness_delta?: number;
  coherencia_delta?: number;
  alineacion_delta?: number;
  viabilidad_delta?: number;
  fitness_history?: { cycle: number; [segment: string]: number }[];
  priorities_by_node?: { node: string; count: number }[];
  guardrail_alerts?: { message: string; level: string }[];
}

const SEGMENT_COLORS = ['#3b82f6', '#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'];

export default function OverviewPage() {
  const { cycle } = useCycle();
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchOverview()
      .then((d) => setData(d as OverviewData))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [cycle]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass-card p-5 h-28 animate-pulse-subtle" />
          ))}
        </div>
        <div className="glass-card h-80 animate-pulse-subtle" />
      </div>
    );
  }

  const fitness = data?.fitness_global ?? 0.72;
  const coherencia = data?.coherencia ?? 0.85;
  const alineacion = data?.alineacion ?? 0.68;
  const viabilidad = data?.viabilidad ?? 0.61;

  const fitnessHistory = data?.fitness_history ?? [
    { cycle: 1, general: 0.55, jovenes: 0.48, mayores: 0.62, rural: 0.51 },
    { cycle: 2, general: 0.62, jovenes: 0.55, mayores: 0.67, rural: 0.58 },
    { cycle: 3, general: 0.68, jovenes: 0.61, mayores: 0.71, rural: 0.63 },
    { cycle: 4, general: 0.72, jovenes: 0.66, mayores: 0.74, rural: 0.67 },
  ];

  const prioritiesByNode = data?.priorities_by_node ?? [
    { node: 'Economia', count: 8 },
    { node: 'Sanidad', count: 6 },
    { node: 'Educacion', count: 7 },
    { node: 'Seguridad', count: 5 },
    { node: 'Medio Ambiente', count: 4 },
    { node: 'Infraestructura', count: 3 },
  ];

  const alerts = data?.guardrail_alerts ?? [
    { message: 'Desplazamiento excesivo en segmento jovenes (ciclo 3->4)', level: 'warning' },
    { message: 'Conflicto inter-sectorial: Economia vs Medio Ambiente', level: 'warning' },
    { message: 'Coherencia global por debajo del umbral en ciclo 2', level: 'critical' },
  ];

  const segments = fitnessHistory.length > 0
    ? Object.keys(fitnessHistory[0]).filter((k) => k !== 'cycle')
    : [];

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          label="Fitness Global"
          value={(fitness * 100).toFixed(0)}
          delta={data?.fitness_delta ?? 0.04}
          sparklineData={fitnessHistory.map((h) => ({ v: (h as Record<string, number>)['general'] ?? fitness }))}
          accentColor="var(--accent-blue)"
        />
        <MetricCard
          label="Coherencia"
          value={(coherencia * 100).toFixed(0)}
          delta={data?.coherencia_delta ?? 0.02}
          accentColor="var(--accent-green)"
        />
        <MetricCard
          label="Alineacion Promedio"
          value={(alineacion * 100).toFixed(0)}
          delta={data?.alineacion_delta ?? -0.01}
          accentColor="var(--accent-indigo)"
        />
        <MetricCard
          label="Viabilidad"
          value={(viabilidad * 100).toFixed(0)}
          delta={data?.viabilidad_delta ?? 0.03}
          accentColor="var(--accent-amber)"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Fitness evolution */}
        <div className="glass-card p-6 lg:col-span-2">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
            Evolucion de Fitness por Segmento
          </h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={fitnessHistory}>
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
                  tickFormatter={(v: number) => `${(v * 100).toFixed(0)}`}
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
                <Legend />
                {segments.map((seg, i) => (
                  <Line
                    key={seg}
                    type="monotone"
                    dataKey={seg}
                    stroke={SEGMENT_COLORS[i % SEGMENT_COLORS.length]}
                    strokeWidth={2}
                    dot={{ r: 3, fill: SEGMENT_COLORS[i % SEGMENT_COLORS.length] }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Score gauge */}
        <div className="glass-card p-6 flex flex-col items-center justify-center gap-4">
          <h2 className="text-base font-semibold text-[var(--text-primary)]">
            Coherencia Global
          </h2>
          <ScoreGauge score={coherencia} label="Coherencia del Plan" size={180} />
          <div className="flex gap-6 mt-2">
            <ScoreGauge score={alineacion} label="Alineacion" size={100} />
            <ScoreGauge score={viabilidad} label="Viabilidad" size={100} />
          </div>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priorities bar chart */}
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
            Prioridades por Nodo
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={prioritiesByNode} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                <XAxis type="number" stroke="var(--text-secondary)" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="node"
                  stroke="var(--text-secondary)"
                  fontSize={12}
                  width={110}
                />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid rgba(148,163,184,0.2)',
                    borderRadius: '8px',
                    color: 'var(--text-primary)',
                  }}
                />
                <Bar dataKey="count" fill="var(--accent-indigo)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alerts */}
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
            Alertas de Guardrails
          </h2>
          <div className="space-y-3">
            {alerts.map((alert, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 p-3 rounded-lg ${
                  alert.level === 'critical'
                    ? 'bg-red-500/10 border border-red-500/20'
                    : 'bg-amber-500/10 border border-amber-500/20'
                }`}
              >
                <AlertTriangle
                  className={`w-5 h-5 shrink-0 mt-0.5 ${
                    alert.level === 'critical' ? 'text-[var(--accent-red)]' : 'text-[var(--accent-amber)]'
                  }`}
                />
                <span className="text-sm text-[var(--text-primary)]">{alert.message}</span>
              </div>
            ))}
            {alerts.length === 0 && (
              <p className="text-sm text-[var(--text-secondary)]">
                No hay alertas activas en este ciclo.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
