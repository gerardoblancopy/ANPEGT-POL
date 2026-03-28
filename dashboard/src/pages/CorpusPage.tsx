import { Database, CheckCircle, XCircle, FileText } from 'lucide-react';

interface CorpusSource {
  name: string;
  type: string;
  enabled: boolean;
  documents: number;
  lastUpdated: string;
}

const SOURCES: CorpusSource[] = [
  { name: 'CIS Barometros', type: 'Encuestas', enabled: true, documents: 48, lastUpdated: '2026-03-15' },
  { name: 'INE Estadisticas', type: 'Datos demograficos', enabled: true, documents: 125, lastUpdated: '2026-03-10' },
  { name: 'BOE Legislacion', type: 'Documentos legales', enabled: true, documents: 340, lastUpdated: '2026-03-20' },
  { name: 'Prensa Nacional', type: 'Medios', enabled: true, documents: 2150, lastUpdated: '2026-03-27' },
  { name: 'Redes Sociales', type: 'Sentimiento publico', enabled: true, documents: 15400, lastUpdated: '2026-03-27' },
  { name: 'Programas Electorales', type: 'Documentos politicos', enabled: true, documents: 12, lastUpdated: '2026-02-01' },
  { name: 'Eurostat', type: 'Datos europeos', enabled: false, documents: 0, lastUpdated: '-' },
  { name: 'Think Tanks', type: 'Analisis experto', enabled: false, documents: 0, lastUpdated: '-' },
];

export default function CorpusPage() {
  const enabledCount = SOURCES.filter((s) => s.enabled).length;
  const totalDocs = SOURCES.reduce((sum, s) => sum + s.documents, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[var(--text-primary)]">Corpus Documental</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Database className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <span className="text-2xl font-bold text-[var(--text-primary)]">{SOURCES.length}</span>
            <span className="text-sm text-[var(--text-secondary)] block">Fuentes configuradas</span>
          </div>
        </div>
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-[var(--accent-green)]" />
          </div>
          <div>
            <span className="text-2xl font-bold text-[var(--text-primary)]">{enabledCount}</span>
            <span className="text-sm text-[var(--text-secondary)] block">Fuentes activas</span>
          </div>
        </div>
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center">
            <FileText className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <span className="text-2xl font-bold text-[var(--text-primary)]">
              {totalDocs.toLocaleString('es-ES')}
            </span>
            <span className="text-sm text-[var(--text-secondary)] block">Documentos totales</span>
          </div>
        </div>
      </div>

      {/* Sources table */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">
          Fuentes de Datos
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Estado</th>
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Fuente</th>
                <th className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium">Tipo</th>
                <th className="text-right py-3 px-4 text-[var(--text-secondary)] font-medium">Documentos</th>
                <th className="text-right py-3 px-4 text-[var(--text-secondary)] font-medium">Ultima Actualizacion</th>
              </tr>
            </thead>
            <tbody>
              {SOURCES.map((source) => (
                <tr key={source.name} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4">
                    {source.enabled ? (
                      <span className="flex items-center gap-1.5 text-[var(--accent-green)]">
                        <CheckCircle className="w-4 h-4" /> Activa
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-[var(--text-secondary)]">
                        <XCircle className="w-4 h-4" /> Inactiva
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-[var(--text-primary)] font-medium">{source.name}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400">
                      {source.type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-[var(--text-primary)]">
                    {source.documents.toLocaleString('es-ES')}
                  </td>
                  <td className="py-3 px-4 text-right text-[var(--text-secondary)]">
                    {source.lastUpdated}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
