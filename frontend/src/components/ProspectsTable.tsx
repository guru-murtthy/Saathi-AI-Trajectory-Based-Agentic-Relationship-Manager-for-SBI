import { useEffect, useState } from 'react';
import { api, Prospects } from '../api';

export function ProspectsTable({ onSelect }: { onSelect: (id: string) => void }) {
  const [data, setData] = useState<Prospects | null>(null);
  useEffect(() => {
    api.prospects('home_purchase').then(setData).catch(() => {});
  }, []);
  if (!data) return <p className="text-slate-500 text-sm">Loading prospects...</p>;
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-slate-400 text-xs text-left">
          <th className="py-1">Customer</th><th>City</th><th className="text-right">FFI</th>
          <th className="text-right">Home %</th>
        </tr>
      </thead>
      <tbody>
        {data.prospects.slice(0, 8).map((p) => (
          <tr key={p.customer_id} onClick={() => onSelect(p.customer_id)}
            className="border-t border-slate-800 hover:bg-slate-800/50 cursor-pointer text-slate-200">
            <td className="py-1.5">{p.name}</td>
            <td className="text-slate-400">{p.city}</td>
            <td className="text-right">{Math.round(p.ffi)}</td>
            <td className="text-right text-teal-400 font-semibold">{p.probability}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
