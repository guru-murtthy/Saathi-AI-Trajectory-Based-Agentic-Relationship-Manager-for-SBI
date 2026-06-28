import { useState } from 'react';
import { api, RM } from '../api';

export function RMChat({ customerId }: { customerId: string }) {
  const [q, setQ] = useState('Why is Rahul a home loan prospect?');
  const [res, setRes] = useState<RM | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);
    try {
      setRes(await api.rm(customerId, q));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)}
          className="flex-1 bg-slate-800 text-slate-100 text-sm rounded-lg px-3 py-2 outline-none" />
        <button onClick={ask} disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm px-4 rounded-lg">
          {loading ? '...' : 'Ask RM'}
        </button>
      </div>
      {res && (
        <div className="mt-3 space-y-2">
          <div className="flex gap-2 text-[10px]">
            {['Observe', 'Reason', 'Predict', 'Explain', 'Recommend'].map((s) => (
              <span key={s} className="bg-slate-800 text-teal-300 px-2 py-0.5 rounded">{s}</span>
            ))}
          </div>
          <div className="bg-slate-800/60 rounded-lg p-3">
            <p className="text-sm text-slate-100 whitespace-pre-wrap">{res.narrative}</p>
          </div>
          <div className="border border-teal-700/40 rounded-lg p-3">
            <p className="text-xs text-teal-300 font-semibold">Recommendation</p>
            <p className="text-sm text-slate-100">{res.loop.recommend.action}</p>
            <p className="text-[11px] text-slate-400 mt-1">Why: {res.loop.recommend.reasoning}</p>
            {res.loop.recommend.requires_human_approval && (
              <span className="inline-block mt-2 text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded">
                Requires human approval
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
