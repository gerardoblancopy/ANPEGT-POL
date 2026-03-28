import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Users, TrendingUp, TrendingDown } from 'lucide-react';
import { useCycle } from '../components/Layout';
import { fetchFitness } from '../lib/api';

interface SegmentDetail {
  name: string;
  fitness: number;
  displacement: number;
  description: string;
  population_pct: number;
}

interface FitnessData {
  segments?: SegmentDetail[];
  per_cycle?: { cycle: number; [seg: string]: number }[];
}

const BAR_COLORS = ['#3b82f6', '#6366f1', '#22c55e', '#f59e0b', '#ef4444'];

export default function SegmentsPage() {
  const { cycle } = useCycle();
  const [data, setData] = useState<FitnessData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchFitness(cycle)
      .then((d) => setData(d as FitnessData))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [cycle]);

  const segments: SegmentDetail[] = data?.segments ?? [
    { name: 'Jovenes (18-30)', fitness: 0.66, displacement: 0.08, description: 'Votantes jovenes, primera vez o recientes. Sensibles a empleo, vivienda y educacion.', population_pct: 18 },
    { name: 'Familias (30-55)', fitness: 0.74, displacement: 0.04, description: 'Familias con hijos. Priorizan sanidad, educacion y seguridad.', population_pct: 35 },
    { name: 'Mayores (55+)', fitness: 0.78, displacement: 0.03, description: 'Poblacion senior. Enfocados en pensiones, sanidad y estabilidad.', population_pct: 28 },
    { name: 'Rural', fitness: 0.61, displacement: 0.11, description: 'Habitantes de municipios de menos de 10.000 habitantes. Demandan infraestructura y servicios.', population_pct: 19 },
  ];

  const perCycle = data?.per_cycle ?? [
    { cycle: 1, jovenes: 0.48, familias: 0.62, mayores: 0.65, rural: 0.45 },
    { cycle: 2, jovenes: 0.55, familias: 0.67, mayores: 0.70, rural: 0.52 },
    { cycle: 3, jovenes: 0.61, familias: 0.71, mayores: 0.74, rural: 0.57 },
    { cycle: 4, jovenes: 0.66, familias: 0.74, mayores: 0.78, rural: 0.61 },
  ];

  const segKeys = perCycle.length > 0 ? Object.keys(perCycle[0]).filter((k) => k !== 'cycle') : [];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="glass-card h-80 animate-pulse-subtle" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass-card h-40 animate-pulse-subtle" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[var(--text-primary)]">Segmentos Electorales</h1>

      {/* Fitness per segment per cycle */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
          Fitness por Segmento por Ciclo
        </h2>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={perCycle}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
              <XAxis
                dataKey="cycle"
                stroke="var(--text-secondary)"
                fontSize={12}
                tickFormatter={(v: number) => `Ciclo ${v}`}
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
              <Legend />
              {segKeys.map((key, i) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={BAR_COLORS[i % BAR_COLORS.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Displacement metrics */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
          Desplazamiento por Segmento
        </h2>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={segments.map((s) => ({ name: s.name.split(' ')[0], desplazamiento: +(s.displacement * 100).toFixed(1) }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
              <XAxis dataKey="name" stroke="var(--text-secondary)" fontSize={12} />
              <YAxis stroke="var(--text-secondary)" fontSize={12} />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid rgba(148,163,184,0.2)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                }}
                formatter={(v) => [`${v}%`, 'Desplazamiento']}
              />
              <Bar dataKey="desplazamiento" fill="var(--accent-amber)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segment detail cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {segments.map((seg) => (
          <div key={seg.name} className="glass-card p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <Users className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-[var(--text-primary)]">{seg.name}</h3>
                  <span className="text-xs text-[var(--text-secondary)]">{seg.population_pct}% de poblacion</span>
                </div>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-[var(--text-primary)]">
                  {(seg.fitness * 100).toFixed(0)}
                </span>
                <span className="text-xs text-[var(--text-secondary)] block">fitness</span>
              </div>
            </div>
            <p className="text-xs text-[var(--text-secondary)] mb-3">{seg.description}</p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-[var(--text-secondary)]">Desplazamiento:</span>
              <span className={`text-xs font-medium flex items-center gap-1 ${
                seg.displacement > 0.1
                  ? 'text-[var(--accent-red)]'
                  : seg.displacement > 0.05
                    ? 'text-[var(--accent-amber)]'
                    : 'text-[var(--accent-green)]'
              }`}>
                {seg.displacement > 0.05 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {(seg.displacement * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
