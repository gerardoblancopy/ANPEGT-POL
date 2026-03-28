import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, AlertTriangle, FileText } from 'lucide-react';
import { useCycle } from '../components/Layout';
import { fetchSectorPlans } from '../lib/api';
import { cn, formatNumber } from '../lib/utils';

interface Policy {
  title: string;
  description: string;
}

interface SectorPlan {
  cluster: string;
  policies: Policy[];
  budget_estimate?: number;
  risk_level: 'bajo' | 'medio' | 'alto';
  conflicts?: string[];
}

export default function SectorPlansPage() {
  const { cycle } = useCycle();
  const [data, setData] = useState<SectorPlan[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchSectorPlans(cycle)
      .then((d) => setData(Array.isArray(d) ? d as SectorPlan[] : null))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [cycle]);

  const plans: SectorPlan[] = data ?? [
    {
      cluster: 'Economia y Empleo',
      policies: [
        { title: 'Plan de creacion de empleo juvenil', description: 'Incentivos fiscales para PYMES que contraten menores de 30 anos.' },
        { title: 'Reforma del mercado laboral', description: 'Flexibilizacion de contratos temporales con protecciones adicionales.' },
        { title: 'Impulso a la digitalizacion empresarial', description: 'Subvenciones para transformacion digital de pequenas empresas.' },
      ],
      budget_estimate: 4500000000,
      risk_level: 'medio',
      conflicts: ['Medio Ambiente - regulacion industrial'],
    },
    {
      cluster: 'Sanidad',
      policies: [
        { title: 'Refuerzo de atencion primaria', description: 'Contratacion de 5.000 profesionales para centros de salud.' },
        { title: 'Plan de salud mental', description: 'Red nacional de atencion psicologica gratuita.' },
      ],
      budget_estimate: 3200000000,
      risk_level: 'bajo',
      conflicts: [],
    },
    {
      cluster: 'Educacion',
      policies: [
        { title: 'Modernizacion curricular', description: 'Actualizacion de contenidos con enfasis en competencias digitales.' },
        { title: 'Becas universales', description: 'Sistema de becas basado en renta familiar automatico.' },
        { title: 'Formacion profesional dual', description: 'Expansion del modelo de FP dual a todas las comunidades.' },
      ],
      budget_estimate: 2800000000,
      risk_level: 'bajo',
      conflicts: [],
    },
    {
      cluster: 'Seguridad',
      policies: [
        { title: 'Plan integral de seguridad ciudadana', description: 'Aumento de dotacion policial en zonas urbanas.' },
        { title: 'Ciberseguridad nacional', description: 'Centro de operaciones de ciberseguridad 24/7.' },
      ],
      budget_estimate: 1500000000,
      risk_level: 'medio',
      conflicts: ['Derechos civiles - vigilancia'],
    },
    {
      cluster: 'Medio Ambiente',
      policies: [
        { title: 'Transicion energetica', description: 'Objetivo 80% renovables para 2030.' },
        { title: 'Proteccion de espacios naturales', description: 'Ampliacion de la red de parques nacionales.' },
      ],
      budget_estimate: 2100000000,
      risk_level: 'alto',
      conflicts: ['Economia - regulacion industrial', 'Transporte - infraestructura'],
    },
    {
      cluster: 'Infraestructura y Transporte',
      policies: [
        { title: 'Red ferroviaria de alta velocidad', description: 'Conexion de todas las capitales de provincia.' },
        { title: 'Movilidad urbana sostenible', description: 'Financiacion de transporte publico electrico.' },
      ],
      budget_estimate: 5200000000,
      risk_level: 'alto',
      conflicts: ['Medio Ambiente - impacto territorial'],
    },
  ];

  const riskColors: Record<string, string> = {
    bajo: 'text-[var(--accent-green)] bg-green-500/10',
    medio: 'text-[var(--accent-amber)] bg-amber-500/10',
    alto: 'text-[var(--accent-red)] bg-red-500/10',
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card h-40 animate-pulse-subtle" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[var(--text-primary)]">Planes Sectoriales</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {plans.map((plan) => {
          const isExpanded = expanded === plan.cluster;
          return (
            <div
              key={plan.cluster}
              className="glass-card overflow-hidden transition-all duration-200"
            >
              <button
                onClick={() => setExpanded(isExpanded ? null : plan.cluster)}
                className="w-full p-5 text-left"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                      {plan.cluster}
                    </h3>
                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span className="flex items-center gap-1.5 text-[var(--text-secondary)]">
                        <FileText className="w-4 h-4" />
                        {plan.policies.length} politicas
                      </span>
                      {plan.budget_estimate && (
                        <span className="text-[var(--text-secondary)]">
                          {formatNumber(plan.budget_estimate / 1e6)}M EUR
                        </span>
                      )}
                      <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', riskColors[plan.risk_level])}>
                        Riesgo {plan.risk_level}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-[var(--text-secondary)]" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-[var(--text-secondary)]" />
                    )}
                  </div>
                </div>
                {plan.conflicts && plan.conflicts.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {plan.conflicts.map((c) => (
                      <span
                        key={c}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs bg-amber-500/10 text-[var(--accent-amber)] border border-amber-500/20"
                      >
                        <AlertTriangle className="w-3 h-3" />
                        {c}
                      </span>
                    ))}
                  </div>
                )}
              </button>

              {isExpanded && (
                <div className="px-5 pb-5 border-t border-white/5 pt-4 space-y-3">
                  {plan.policies.map((policy) => (
                    <div key={policy.title} className="p-3 rounded-lg bg-white/5">
                      <h4 className="text-sm font-medium text-[var(--text-primary)] mb-1">
                        {policy.title}
                      </h4>
                      <p className="text-xs text-[var(--text-secondary)]">{policy.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
