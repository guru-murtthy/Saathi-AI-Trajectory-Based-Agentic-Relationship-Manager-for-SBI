import { DNA } from '../api';

export function DNAPanel({ dna }: { dna: DNA }) {
  return (
    <div className="grid grid-cols-1 gap-3">
      {Object.entries(dna.dna).map(([strand, data]) => (
        <div key={strand}>
          <div className="flex justify-between text-sm text-slate-200 capitalize">
            <span>{strand.replace('_', ' ')} DNA</span>
            <span className="font-semibold">{data.score}%</span>
          </div>
          <div className="h-2 bg-slate-800 rounded">
            <div className="h-2 bg-indigo-500 rounded" style={{ width: `${data.score}%` }} />
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">
            {data.drivers.map((d) => d.label).join(', ')}
          </p>
        </div>
      ))}
    </div>
  );
}
