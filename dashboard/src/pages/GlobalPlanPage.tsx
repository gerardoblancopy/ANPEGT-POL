import { useState, useEffect } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import { useCycle } from '../components/Layout';
import { fetchGlobalPlan } from '../lib/api';

interface Proposal {
  title: string;
  sector: string;
  status: string;
}

interface Conflict {
  description: string;
  resolved: boolean;
}

interface GlobalPlanData {
  summary?: string;
  coherence_score?: number;
  proposals?: Proposal[];
  conflicts?: Conflict[];
}

export default function GlobalPlanPage() {
  const { cycle } = useCycle();
  const [data, setData] = useState<GlobalPlanData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchGlobalPlan(cycle)
      .then((d) => setData(d as GlobalPlanData))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [cycle]);

  const summary = data?.summary ??
    'El plan consolidado del ciclo actual integra propuestas de 6 sectores estrategicos, ' +
    'con un enfoque prioritario en empleo, sanidad y educacion. Se han identificado 3 conflictos ' +
    'inter-sectoriales de los cuales 2 han sido resueltos mediante ajustes de politica. La coherencia ' +
    'global se mantiene por encima del umbral minimo establecido.';

  const coherenceScore = data?.coherence_score ?? 0.82;

  const proposals: Proposal[] = data?.proposals ?? [
    { title: 'Plan de empleo juvenil con incentivos fiscales', sector: 'Economia', status: 'aprobado' },
    { title: 'Red nacional de atencion psicologica', sector: 'Sanidad', status: 'aprobado' },
    { title: 'Modernizacion curricular digital', sector: 'Educacion', status: 'aprobado' },
    { title: 'Centro de ciberseguridad nacional', sector: 'Seguridad', status: 'aprobado' },
    { title: 'Transicion energetica acelerada', sector: 'Medio Ambiente', status: 'en revision' },
    { title: 'Red ferroviaria de alta velocidad', sector: 'Infraestructura', status: 'en revision' },
    { title: 'Expansion de FP dual', sector: 'Educacion', status: 'aprobado' },
    { title: 'Transporte publico electrico', sector: 'Infraestructura', status: 'aprobado' },
  ];

  const conflicts: Conflict[] = data?.conflicts ?? [
    { description: 'Regulacion industrial vs objetivos de empleo: ajustadas exenciones temporales para sectores en transicion.', resolved: true },
    { description: 'Impacto territorial de infraestructura vs proteccion ambiental: trazados alternativos aprobados.', resolved: true },
    { description: 'Vigilancia de seguridad vs privacidad ciudadana: pendiente de revision por comite de derechos.', resolved: false },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="glass-card h-32 animate-pulse-subtle" />
        <div className="glass-card h-64 animate-pulse-subtle" />
      </div>
    );
  }

  const resolved = conflicts.filter((c) => c.resolved);
  const unresolved = conflicts.filter((c) => !c.resolved);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[var(--text-primary)]">Plan Consolidado</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Summary */}
        <div className="glass-card p-6 lg:col-span-2">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-3">
            Resumen del Orquestador
          </h2>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            {summary}
          </p>
        </div>

        {/* Coherence gauge */}
        <div className="glass-card p-6 flex flex-col items-center justify-center">
          <ScoreGauge score={coherenceScore} label="Coherencia del Plan" size={180} />
        </div>
      </div>

      {/* Proposals */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
          Propuestas Consolidadas
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Propuesta</th>
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Sector</th>
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Estado</th>
              </tr>
            </thead>
            <tbody>
              {proposals.map((p) => (
                <tr key={p.title} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4 text-[var(--text-primary)]">{p.title}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400">
                      {p.sector}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        p.status === 'aprobado'
                          ? 'bg-green-500/10 text-[var(--accent-green)]'
                          : 'bg-amber-500/10 text-[var(--accent-amber)]'
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Conflicts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--accent-green)] mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Conflictos Resueltos ({resolved.length})
          </h2>
          <div className="space-y-3">
            {resolved.map((c, i) => (
              <div key={i} className="p-3 rounded-lg bg-green-500/5 border border-green-500/10">
                <p className="text-sm text-[var(--text-primary)]">{c.description}</p>
              </div>
            ))}
            {resolved.length === 0 && (
              <p className="text-sm text-[var(--text-secondary)]">No hay conflictos resueltos.</p>
            )}
          </div>
        </div>
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--accent-red)] mb-4 flex items-center gap-2">
            <XCircle className="w-5 h-5" />
            Conflictos Pendientes ({unresolved.length})
          </h2>
          <div className="space-y-3">
            {unresolved.map((c, i) => (
              <div key={i} className="p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <p className="text-sm text-[var(--text-primary)]">{c.description}</p>
              </div>
            ))}
            {unresolved.length === 0 && (
              <p className="text-sm text-[var(--text-secondary)]">No hay conflictos pendientes.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
