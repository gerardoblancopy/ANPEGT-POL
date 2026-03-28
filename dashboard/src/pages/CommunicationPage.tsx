import { useState, useEffect } from 'react';
import { MessageSquare, Mic, Hash, Camera, ThumbsUp } from 'lucide-react';
import { useCycle } from '../components/Layout';
import { fetchCommunicationPlans, fetchSocialPosts, fetchSpeeches } from '../lib/api';
import { cn } from '../lib/utils';

interface SegmentComm {
  segment: string;
  messages: string[];
  tone: string;
  emphasis: string[];
}

interface SocialPost {
  platform: string;
  content: string;
  segment: string;
}

interface Speech {
  title: string;
  excerpt: string;
  soundbites: string[];
}

interface CommData {
  segments?: SegmentComm[];
}

export default function CommunicationPage() {
  const { cycle } = useCycle();
  const [commData, setCommData] = useState<CommData | null>(null);
  const [posts, setPosts] = useState<SocialPost[] | null>(null);
  const [speeches, setSpeeches] = useState<Speech[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchCommunicationPlans(cycle).catch(() => null),
      fetchSocialPosts(cycle).catch(() => null),
      fetchSpeeches(cycle).catch(() => null),
    ])
      .then(([comm, social, sp]) => {
        setCommData(comm as CommData);
        setPosts(Array.isArray(social) ? social as SocialPost[] : null);
        setSpeeches(Array.isArray(sp) ? sp as Speech[] : null);
      })
      .finally(() => setLoading(false));
  }, [cycle]);

  const segments: SegmentComm[] = commData?.segments ?? [
    {
      segment: 'Jovenes (18-30)',
      messages: [
        'Tu futuro empieza con un empleo digno',
        'Educacion que te prepara para el mundo real',
        'Vivienda accesible: tu derecho, nuestra prioridad',
      ],
      tone: 'Cercano, directo, esperanzador',
      emphasis: ['Empleo juvenil', 'Formacion profesional', 'Vivienda'],
    },
    {
      segment: 'Familias (30-55)',
      messages: [
        'Sanidad publica de calidad para los tuyos',
        'Educacion que abre puertas',
        'Seguridad en tu barrio, tranquilidad en tu hogar',
      ],
      tone: 'Confiable, protector, pragmatico',
      emphasis: ['Sanidad', 'Educacion', 'Seguridad'],
    },
    {
      segment: 'Mayores (55+)',
      messages: [
        'Pensiones dignas, compromiso inquebrantable',
        'Sanidad cercana y accesible',
        'Experiencia valorada, futuro asegurado',
      ],
      tone: 'Respetuoso, tranquilizador, firme',
      emphasis: ['Pensiones', 'Sanidad', 'Servicios sociales'],
    },
    {
      segment: 'Rural',
      messages: [
        'Cada pueblo merece servicios de calidad',
        'Conectividad y transporte para todos',
        'El campo como motor economico',
      ],
      tone: 'Empatico, comprometido, concreto',
      emphasis: ['Infraestructura rural', 'Conectividad', 'Agricultura'],
    },
  ];

  const socialPosts: SocialPost[] = posts ?? [
    { platform: 'twitter', content: 'El empleo juvenil no es un eslogan, es nuestro primer compromiso. Plan de 500.000 empleos para menores de 30. #FuturoReal #EmpleoJoven', segment: 'Jovenes' },
    { platform: 'instagram', content: 'Imagina un pais donde tu formacion te lleva directamente al empleo. Nuestro plan de FP dual lo hace posible. Desliza para saber mas.', segment: 'Jovenes' },
    { platform: 'facebook', content: 'Las familias merecen tranquilidad. Nuestro plan refuerza la atencion primaria con 5.000 nuevos profesionales. Porque la salud no puede esperar.', segment: 'Familias' },
    { platform: 'twitter', content: 'Cada pueblo cuenta. Nuestro plan de infraestructura rural conecta 2.000 municipios con fibra optica y transporte digno. #NingunPuebloSolo', segment: 'Rural' },
  ];

  const speechData: Speech[] = speeches ?? [
    {
      title: 'Discurso de Presentacion del Plan Economico',
      excerpt: 'Hoy presentamos un plan que pone a las personas en el centro de la economia. No hablamos de cifras abstractas, hablamos de familias que llegan a fin de mes, de jovenes que encuentran su primer empleo...',
      soundbites: [
        'Una economia que funciona es una economia que llega a todos.',
        'El empleo digno no es un privilegio, es un derecho.',
        'Invertir en educacion es invertir en el futuro de todos.',
      ],
    },
  ];

  const platformIcons: Record<string, typeof Hash> = {
    twitter: Hash,
    instagram: Camera,
    facebook: ThumbsUp,
  };

  const platformStyles: Record<string, string> = {
    twitter: 'bg-sky-500/10 border-sky-500/20',
    instagram: 'bg-pink-500/10 border-pink-500/20',
    facebook: 'bg-blue-600/10 border-blue-600/20',
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="glass-card h-12 w-96 animate-pulse-subtle" />
        <div className="glass-card h-64 animate-pulse-subtle" />
      </div>
    );
  }

  const active = segments[activeTab];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[var(--text-primary)]">Comunicacion</h1>

      {/* Segment tabs */}
      <div className="flex flex-wrap gap-2">
        {segments.map((seg, i) => (
          <button
            key={seg.segment}
            onClick={() => setActiveTab(i)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150',
              i === activeTab
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'glass-card text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
            )}
          >
            {seg.segment}
          </button>
        ))}
      </div>

      {/* Active segment details */}
      {active && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-6">
            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-blue-400" />
              Mensajes Clave
            </h2>
            <div className="space-y-3 mb-6">
              {active.messages.map((m, i) => (
                <div key={i} className="p-3 rounded-lg bg-white/5 text-sm text-[var(--text-primary)]">
                  {m}
                </div>
              ))}
            </div>
            <div className="space-y-3">
              <div>
                <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Tono</span>
                <p className="text-sm text-[var(--text-primary)] mt-1">{active.tone}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Enfasis</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {active.emphasis.map((e) => (
                    <span key={e} className="px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400">
                      {e}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Social posts for this segment */}
          <div className="space-y-4">
            <h2 className="text-base font-semibold text-[var(--text-primary)]">
              Publicaciones en Redes
            </h2>
            {socialPosts
              .filter((p) => p.segment === active.segment.split(' ')[0])
              .map((post, i) => {
                const Icon = platformIcons[post.platform] ?? MessageSquare;
                return (
                  <div
                    key={i}
                    className={cn(
                      'p-4 rounded-lg border',
                      platformStyles[post.platform] ?? 'glass-card',
                    )}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="w-4 h-4" />
                      <span className="text-xs font-medium text-[var(--text-secondary)] capitalize">
                        {post.platform}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--text-primary)]">{post.content}</p>
                  </div>
                );
              })}
            {socialPosts.filter((p) => p.segment === active.segment.split(' ')[0]).length === 0 && (
              <div className="glass-card p-4">
                <p className="text-sm text-[var(--text-secondary)]">
                  No hay publicaciones generadas para este segmento en el ciclo actual.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Speeches */}
      <div className="glass-card p-6">
        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
          <Mic className="w-5 h-5 text-indigo-400" />
          Discursos
        </h2>
        <div className="space-y-4">
          {speechData.map((speech, i) => (
            <div key={i} className="space-y-3">
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">{speech.title}</h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{speech.excerpt}</p>
              <div>
                <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
                  Soundbites destacados
                </span>
                <div className="space-y-2 mt-2">
                  {speech.soundbites.map((sb, j) => (
                    <div
                      key={j}
                      className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-sm text-[var(--text-primary)] italic"
                    >
                      &ldquo;{sb}&rdquo;
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
          {speechData.length === 0 && (
            <p className="text-sm text-[var(--text-secondary)]">
              No hay discursos generados para este ciclo.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
