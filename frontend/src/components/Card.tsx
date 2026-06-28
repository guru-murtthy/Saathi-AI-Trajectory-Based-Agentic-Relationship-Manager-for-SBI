import { ReactNode } from 'react';

export function Card({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-5 shadow-lg">
      <div className="mb-3">
        <h2 className="text-slate-100 font-semibold text-lg">{title}</h2>
        {subtitle && <p className="text-slate-400 text-xs">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
