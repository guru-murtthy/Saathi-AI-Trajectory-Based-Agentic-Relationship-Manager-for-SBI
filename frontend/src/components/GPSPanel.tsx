import { useState } from 'react';
import { api, GPS } from '../api';

export function GPSPanel({ customerId }: { customerId: string }) {
  const [gps, setGps] = useState<GPS | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const res = await api.gps(customerId, {
        goal_kind: 'Buy House',
        target_amount: 1800000,
        current_amount: 300000,
        target_date: '2029-06-01',
      });
      setGps(res);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button onClick={run} disabled={loading}
        className="bg-teal-600 hover:bg-teal-500 text-white text-sm px-4 py-2 rounded-lg">
        {loading ? 'Planning...' : 'Generate plan: Buy House \u20b918L'}
      </button>
      {gps && (
        <div className="mt-4 space-y-2">
          <div className="grid grid-cols-3 gap-2 text-center">
            <Stat label="Gap" value={`\u20b9${(gps.gap / 100000).toFixed(1)}L`} />
            <Stat label="Monthly" value={`\u20b9${Math.round(gps.required_monthly).toLocaleString()}`} />
            <Stat label="Months" value={`${gps.months_to_goal}`} />
          </div>
          <table className="w-full text-xs text-slate-300 mt-2">
            <tbody>
              {gps.plan.map((p) => (
                <tr key={p.instrument} className="border-t border-slate-800">
                  <td className="py-1">{p.instrument}</td>
                  <td className="text-right">{p.allocation_pct}%</td>
                  <td className="text-right">\u20b9{Math.round(p.monthly_amount).toLocaleString()}/mo</td>
                </tr>
              ))}
            </tbody>
          </table>
          {gps.feasibility && (
            <p className={`text-xs ${gps.feasibility.on_track ? 'text-teal-400' : 'text-amber-400'}`}>
              {gps.feasibility.on_track
                ? 'On track with current saving capacity.'
                : `Shortfall \u20b9${Math.round(gps.feasibility.shortfall).toLocaleString()}/mo.`}
            </p>
          )}
          <p className="text-[11px] text-slate-500">{gps.explanation}</p>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800/60 rounded-lg py-2">
      <div className="text-white font-bold">{value}</div>
      <div className="text-[10px] text-slate-400">{label}</div>
    </div>
  );
}
