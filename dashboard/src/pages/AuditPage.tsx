import { useState } from 'react';
import { Clock, AlertTriangle, Shield, Download, CheckCircle, Info } from 'lucide-react';
import { cn } from '../lib/utils';

interface TimelineEvent {
  timestamp: string;
  cycle: number;
  event: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface Violation {
  timestamp: string;
  cycle: number;
  rule: string;
  description: string;
  severity: 'warning' | 'critical';
  resolved: boolean;
}

const EVENTS: TimelineEvent[] = [
  { timestamp: '2026-03-28 10:00', cycle: 4, event: 'Inicio del ciclo 4', type: 'info' },
  { timestamp: '2026-03-28 10:05', cycle: 4, event: 'Recopilacion de prioridades ANP completada', type: 'success' },
  { timestamp: '2026-03-28 10:12', cycle: 4, event: 'Generacion de planes sectoriales (6 clusters)', type: 'success' },
  { timestamp: '2026-03-28 10:18', cycle: 4, event: 'Deteccion de conflicto: Economia vs Medio Ambiente', type: 'warning' },
  { timestamp: '2026-03-28 10:22', cycle: 4, event: 'Consolidacion del plan global', type: 'success' },
  { timestamp: '2026-03-28 10:25', cycle: 4, event: 'Alerta: desplazamiento excesivo en segmento Rural', type: 'warning' },
  { timestamp: '2026-03-28 10:30', cycle: 4, event: 'Generacion de comunicacion por segmento', type: 'success' },
  { timestamp: '2026-03-28 10:35', cycle: 4, event: 'Evaluacion de fitness completada', type: 'success' },
  { timestamp: '2026-03-28 10:38', cycle: 4, event: 'Ciclo 4 finalizado. Fitness global: 72%', type: 'info' },
  { timestamp: '2026-03-27 14:00', cycle: 3, event: 'Inicio del ciclo 3', type: 'info' },
  { timestamp: '2026-03-27 14:35', cycle: 3, event: 'Ciclo 3 finalizado. Fitness global: 68%', type: 'info' },
];

const VIOLATIONS: Violation[] = [
  {
    timestamp: '2026-03-28 10:25',
    cycle: 4,
    rule: 'MAX_DISPLACEMENT',
    description: 'Desplazamiento del segmento Rural supera el umbral de 10% (actual: 11.2%)',
    severity: 'warning',
    resolved: false,
  },
  {
    timestamp: '2026-03-28 10:18',
    cycle: 4,
    rule: 'INTERCLUSTER_CONFLICT',
    description: 'Conflicto no resuelto entre politicas de Economia e Medio Ambiente',
    severity: 'warning',
    resolved: true,
  },
  {
    timestamp: '2026-03-27 14:20',
    cycle: 3,
    rule: 'MIN_COHERENCE',
    description: 'Coherencia global cayo por debajo del minimo de 0.65 (actual: 0.63)',
    severity: 'critical',
    resolved: true,
  },
];

const typeIcons = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertTriangle,
};

const typeColors = {
  info: 'text-blue-400',
  success: 'text-[var(--accent-green)]',
  warning: 'text-[var(--accent-amber)]',
  error: 'text-[var(--accent-red)]',
};

export default function AuditPage() {
  const [_exporting, setExporting] = useState(false);

  const handleExport = () => {
    setExporting(true);
    // Placeholder - would trigger real export
    setTimeout(() => setExporting(false), 1500);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Auditoria</h1>
        <button
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-500/30 transition-colors"
        >
          <Download className="w-4 h-4" />
          Exportar Registro
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Timeline */}
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Linea Temporal
          </h2>
          <div className="space-y-1">
            {EVENTS.map((evt, i) => {
              const Icon = typeIcons[evt.type];
              return (
                <div key={i} className="flex gap-3 py-2">
                  <div className="flex flex-col items-center">
                    <Icon className={cn('w-4 h-4 shrink-0 mt-0.5', typeColors[evt.type])} />
                    {i < EVENTS.length - 1 && (
                      <div className="w-px flex-1 bg-white/10 mt-1" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0 pb-2">
                    <p className="text-sm text-[var(--text-primary)]">{evt.event}</p>
                    <span className="text-xs text-[var(--text-secondary)]">
                      {evt.timestamp} - Ciclo {evt.cycle}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Guardrail violations */}
        <div className="glass-card p-6">
          <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-indigo-400" />
            Violaciones de Guardrails
          </h2>
          <div className="space-y-3">
            {VIOLATIONS.map((v, i) => (
              <div
                key={i}
                className={cn(
                  'p-4 rounded-lg border',
                  v.severity === 'critical'
                    ? 'bg-red-500/5 border-red-500/20'
                    : 'bg-amber-500/5 border-amber-500/20',
                )}
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle
                      className={cn(
                        'w-4 h-4',
                        v.severity === 'critical' ? 'text-[var(--accent-red)]' : 'text-[var(--accent-amber)]',
                      )}
                    />
                    <span className="text-xs font-mono text-[var(--text-secondary)]">{v.rule}</span>
                  </div>
                  <span
                    className={cn(
                      'px-2 py-0.5 rounded-full text-xs font-medium',
                      v.resolved
                        ? 'bg-green-500/10 text-[var(--accent-green)]'
                        : v.severity === 'critical'
                          ? 'bg-red-500/10 text-[var(--accent-red)]'
                          : 'bg-amber-500/10 text-[var(--accent-amber)]',
                    )}
                  >
                    {v.resolved ? 'Resuelto' : 'Pendiente'}
                  </span>
                </div>
                <p className="text-sm text-[var(--text-primary)] mb-1">{v.description}</p>
                <span className="text-xs text-[var(--text-secondary)]">
                  {v.timestamp} - Ciclo {v.cycle}
                </span>
              </div>
            ))}
            {VIOLATIONS.length === 0 && (
              <p className="text-sm text-[var(--text-secondary)]">
                No se han registrado violaciones de guardrails.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
