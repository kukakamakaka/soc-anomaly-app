'use client';
import { useEffect, useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Filter, CheckCircle, Clock, RefreshCw,
  FileText, ChevronDown, ChevronUp, X, Loader2, AlertTriangle
} from 'lucide-react';
import { apiFetch } from '@/lib/auth';

interface Event {
  id: number;
  process_name: string;
  command_line: string;
  user: string;
  severity: string;
  anomaly_score: number;
  mitre_technique: string | null;
  is_acknowledged: boolean;
  acknowledged_at: string | null;
  created_at: string;
  source_ip?: string;
  hostname?: string;
}

const SEV_CFG: Record<string, { color: string; bg: string; dot: string }> = {
  critical: { color: 'text-red-400',    bg: 'bg-red-500/10 border-red-500/25',    dot: 'bg-red-400'    },
  high:     { color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/25', dot: 'bg-orange-400' },
  medium:   { color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/25', dot: 'bg-yellow-400' },
  low:      { color: 'text-blue-400',   bg: 'bg-blue-500/10 border-blue-500/25',   dot: 'bg-blue-400'   },
  normal:   { color: 'text-slate-400',  bg: 'bg-slate-500/10 border-slate-500/20', dot: 'bg-slate-500'  },
};

function Badge({ severity }: { severity: string }) {
  const c = SEV_CFG[severity] ?? SEV_CFG.normal;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold border uppercase ${c.bg} ${c.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot} ${severity === 'critical' ? 'animate-pulse' : ''}`} />
      {severity}
    </span>
  );
}

export default function EventsPage() {
  const [events, setEvents]           = useState<Event[]>([]);
  const [loading, setLoading]         = useState(true);
  const [refreshing, setRefreshing]   = useState(false);
  const [search, setSearch]           = useState('');
  const [debouncedSearch, setDebounced] = useState('');
  const [severityFilter, setSeverity] = useState('');
  const [ackFilter, setAckFilter]     = useState('');
  const [expandedId, setExpandedId]   = useState<number | null>(null);
  const [report, setReport]           = useState<{ id: number; text: string } | null>(null);
  const [reportLoading, setReportLoading] = useState<number | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef    = useRef<AbortController | null>(null);

  // Debounce search input — don't fire API on every keystroke
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => setDebounced(search), 320);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [search]);

  const loadEvents = useCallback(async (showRefresh = false) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    if (showRefresh) setRefreshing(true);
    try {
      const params = new URLSearchParams({ limit: '200' });
      if (severityFilter)  params.set('severity',     severityFilter);
      if (debouncedSearch) params.set('search',        debouncedSearch);
      if (ackFilter)       params.set('acknowledged',  ackFilter);
      const res = await apiFetch(`/api/events?${params.toString()}`, { signal: abortRef.current.signal });
      if (res.ok) setEvents(await res.json());
    } catch (e: unknown) {
      if (e instanceof Error && e.name === 'AbortError') return;
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [severityFilter, debouncedSearch, ackFilter]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const acknowledge = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    await apiFetch(`/api/events/${id}/acknowledge`, { method: 'PATCH' });
    setEvents(prev => prev.map(ev => ev.id === id ? { ...ev, is_acknowledged: true } : ev));
  };

  const loadReport = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (report?.id === id) { setReport(null); return; }
    setReportLoading(id);
    try {
      const res = await apiFetch(`/api/events/${id}/report`);
      if (res.ok) {
        const data = await res.json();
        setReport({ id, text: data.report });
      }
    } finally { setReportLoading(null); }
  };

  const totalCritical = events.filter(e => e.severity === 'critical').length;
  const totalHigh = events.filter(e => e.severity === 'high').length;
  const unacked = events.filter(e => !e.is_acknowledged && (e.severity === 'critical' || e.severity === 'high')).length;

  // loading.tsx skeleton handles initial load — return null avoids double-spinner
  if (loading) return null;

  return (
    <div className="p-6 space-y-5 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-black text-white tracking-tight">
            Anomaly <span className="text-blue-400">Events</span>
          </h1>
          <p className="text-xs text-slate-600 font-mono mt-0.5">{events.length} events loaded</p>
        </div>
        <button
          onClick={() => loadEvents(true)}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.06] text-slate-400 hover:text-white text-xs font-semibold transition-all disabled:opacity-50"
        >
          <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Quick stats */}
      <div className="flex gap-3 flex-wrap">
        {[
          { label: 'Critical',    value: totalCritical, color: 'text-red-400',    bg: 'bg-red-500/10 border-red-500/20'       },
          { label: 'High',        value: totalHigh,     color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20' },
          { label: 'Needs ACK',   value: unacked,       color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/20' },
          { label: 'Total',       value: events.length, color: 'text-blue-400',   bg: 'bg-blue-500/10 border-blue-500/20'     },
        ].map(({ label, value, color, bg }) => (
          <div key={label} className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-bold ${bg} ${color}`}>
            <AlertTriangle size={11} />
            {value} {label}
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search process, command, user..."
            className="w-full bg-black/30 border border-white/[0.07] focus:border-blue-500/40 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white font-mono placeholder-slate-700 outline-none transition-colors"
          />
          {search && <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400"><X size={13} /></button>}
        </div>
        <select
          value={severityFilter}
          onChange={e => setSeverity(e.target.value)}
          className="bg-black/30 border border-white/[0.07] focus:border-blue-500/40 rounded-xl px-3 py-2.5 text-xs text-slate-400 outline-none transition-colors"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="normal">Normal</option>
        </select>
        <select
          value={ackFilter}
          onChange={e => setAckFilter(e.target.value)}
          className="bg-black/30 border border-white/[0.07] focus:border-blue-500/40 rounded-xl px-3 py-2.5 text-xs text-slate-400 outline-none transition-colors"
        >
          <option value="">All Status</option>
          <option value="false">Unacknowledged</option>
          <option value="true">Acknowledged</option>
        </select>
        {(search || severityFilter || ackFilter) && (
          <button
            onClick={() => { setSearch(''); setSeverity(''); setAckFilter(''); }}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.07] text-slate-400 hover:text-white text-xs font-semibold transition-all border border-white/[0.06]"
          >
            <X size={12} /> Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="glass rounded-2xl overflow-hidden">
        <div className="grid grid-cols-[2fr_1fr_1fr_80px_80px_120px] gap-0 px-5 py-3 border-b border-white/[0.05] bg-white/[0.02]">
          {['Process / Command', 'User', 'MITRE ATT&CK', 'Score', 'Severity', 'Actions'].map(h => (
            <span key={h} className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">{h}</span>
          ))}
        </div>

        <div className="divide-y divide-white/[0.04] max-h-[calc(100vh-360px)] overflow-y-auto">
          {events.length === 0 ? (
            <div className="py-16 text-center text-slate-600 text-xs">
              <Filter size={28} className="mx-auto mb-3 opacity-30" />
              No events match your filters
            </div>
          ) : events.map((ev) => (
            <div key={ev.id}>
              <div
                className="grid grid-cols-[2fr_1fr_1fr_80px_80px_120px] gap-0 px-5 py-3.5 table-row-premium cursor-pointer"
                onClick={() => setExpandedId(expandedId === ev.id ? null : ev.id)}
              >
                {/* Process */}
                <div className="min-w-0 pr-4">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white font-mono truncate">{ev.process_name}</span>
                    {ev.is_acknowledged && <CheckCircle size={11} className="text-emerald-500 shrink-0" />}
                  </div>
                  <p className="text-[10px] text-slate-600 font-mono truncate mt-0.5">{ev.command_line || '—'}</p>
                </div>
                {/* User */}
                <div className="flex items-center">
                  <span className="text-[11px] text-slate-400 font-mono truncate">{ev.user || '—'}</span>
                </div>
                {/* MITRE */}
                <div className="flex items-center">
                  <span className="text-[10px] text-slate-500 truncate">{ev.mitre_technique?.split('\n')[0] || '—'}</span>
                </div>
                {/* Score */}
                <div className="flex items-center">
                  <span className={`text-xs font-bold font-mono ${ev.anomaly_score >= 0.6 ? 'text-red-400' : ev.anomaly_score >= 0.3 ? 'text-orange-400' : 'text-slate-400'}`}>
                    {ev.anomaly_score.toFixed(3)}
                  </span>
                </div>
                {/* Severity */}
                <div className="flex items-center">
                  <Badge severity={ev.severity} />
                </div>
                {/* Actions */}
                <div className="flex items-center gap-2">
                  {!ev.is_acknowledged && (ev.severity === 'critical' || ev.severity === 'high') && (
                    <button
                      onClick={(e) => acknowledge(ev.id, e)}
                      title="Acknowledge"
                      className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors border border-emerald-500/20"
                    >
                      <CheckCircle size={12} />
                    </button>
                  )}
                  <button
                    onClick={(e) => loadReport(ev.id, e)}
                    title="AI Report"
                    disabled={reportLoading === ev.id}
                    className="p-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 transition-colors border border-blue-500/20 disabled:opacity-50"
                  >
                    {reportLoading === ev.id ? <Loader2 size={12} className="animate-spin" /> : <FileText size={12} />}
                  </button>
                  <button className="p-1.5 text-slate-600 hover:text-slate-400 transition-colors">
                    {expandedId === ev.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </button>
                </div>
              </div>

              {/* Expanded row */}
              <AnimatePresence>
                {expandedId === ev.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 py-4 bg-white/[0.02] border-t border-white/[0.04] space-y-3">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-[11px]">
                        <div>
                          <span className="text-slate-600 uppercase tracking-wider block mb-1">Event ID</span>
                          <span className="text-white font-mono">#{ev.id}</span>
                        </div>
                        <div>
                          <span className="text-slate-600 uppercase tracking-wider block mb-1">Timestamp</span>
                          <span className="text-white font-mono flex items-center gap-1"><Clock size={10} /> {new Date(ev.created_at).toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-slate-600 uppercase tracking-wider block mb-1">Status</span>
                          <span className={`font-semibold ${ev.is_acknowledged ? 'text-emerald-400' : 'text-orange-400'}`}>
                            {ev.is_acknowledged ? 'Acknowledged' : 'Pending Response'}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-600 uppercase tracking-wider block mb-1">ML Score</span>
                          <span className="text-white font-mono">{ev.anomaly_score.toFixed(6)}</span>
                        </div>
                      </div>

                      {ev.mitre_technique && (
                        <div>
                          <span className="text-[10px] text-slate-600 uppercase tracking-wider block mb-1">MITRE ATT&CK Techniques</span>
                          <pre className="text-[10px] text-slate-300 font-mono bg-black/30 rounded-lg p-3 whitespace-pre-wrap border border-white/[0.05]">{ev.mitre_technique}</pre>
                        </div>
                      )}

                      {ev.command_line && (
                        <div>
                          <span className="text-[10px] text-slate-600 uppercase tracking-wider block mb-1">Full Command Line</span>
                          <code className="block text-[10px] text-emerald-300 font-mono bg-black/40 rounded-lg p-3 break-all border border-white/[0.05]">{ev.command_line}</code>
                        </div>
                      )}

                      {/* AI Report */}
                      {report?.id === ev.id && (
                        <div>
                          <span className="text-[10px] text-slate-600 uppercase tracking-wider block mb-1">Sentinel-AI Forensic Report</span>
                          <pre className="text-[10px] text-slate-300 font-mono bg-black/30 rounded-lg p-3 whitespace-pre-wrap border border-blue-500/10 max-h-64 overflow-y-auto">{report.text}</pre>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
