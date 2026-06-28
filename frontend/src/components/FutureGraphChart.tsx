import {
  Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { FutureGraph } from '../api';

export function FutureGraphChart({ fg }: { fg: FutureGraph }) {
  const data = [
    ...fg.history.map((h) => ({ month: h.month, balance: h.balance })),
    ...fg.projection.map((p) => ({ month: p.month, projected: p.balance })),
  ];
  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data}>
          <XAxis dataKey="month" tick={{ fontSize: 9, fill: '#94a3b8' }} interval={3} />
          <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }} width={50}
            tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
          <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b' }} />
          <Area type="monotone" dataKey="balance" stroke="#64748b" fill="#334155" />
          <Area type="monotone" dataKey="projected" stroke="#0d9488" fill="#0d948855" />
        </AreaChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-400 mt-2">{fg.explanation}</p>
    </div>
  );
}
