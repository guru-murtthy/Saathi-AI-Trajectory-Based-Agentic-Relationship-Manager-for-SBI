import { FFI } from '../api';

const LABELS: Record<string, string> = {
  home_ownership: 'Home Ownership',
  marriage: 'Marriage',
  investment_readiness: 'Investment Readiness',
  business_creation: 'Business Creation',
  travel: 'Travel',
};

export function FFIGauge({ ffi }: { ffi: FFI }) {
  const pct = Math.round(ffi.ffi);
  return (
    <div>
      <div className="flex items-center gap-6">
        <div className="relative w-32 h-32">
          <svg viewBox="0 0 120 120" className="w-32 h-32 -rotate-90">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#1e293b" strokeWidth="12" />
            <circle
              cx="60" cy="60" r="52" fill="none" stroke="#0d9488" strokeWidth="12"
              strokeDasharray={`${(pct / 100) * 326} 326`} strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold text-white">{pct}</span>
            <span className="text-[10px] text-slate-400">FFI / 100</span>
          </div>
        </div>
        <div className="flex-1 space-y-2">
          {Object.entries(ffi.sub_scores).map(([k, v]) => (
            <div key={k}>
              <div className="flex justify-between text-xs text-slate-300">
                <span>{LABELS[k] ?? k}</span>
                <span>{Math.round(v)}%</span>
              </div>
              <div className="h-1.5 bg-slate-800 rounded">
                <div className="h-1.5 bg-teal-500 rounded" style={{ width: `${v}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
      <p className="mt-3 text-xs text-slate-400">{ffi.explanation}</p>
    </div>
  );
}
