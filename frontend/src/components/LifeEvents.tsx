import { LifeEvents as LE } from '../api';

export function LifeEventsPanel({ events }: { events: LE }) {
  return (
    <div className="space-y-3">
      {events.predictions.slice(0, 4).map((e) => (
        <div key={e.event} className="border border-slate-800 rounded-xl p-3">
          <div className="flex justify-between items-center">
            <span className="text-slate-100 capitalize font-medium">{e.event.replace('_', ' ')}</span>
            <span className="text-teal-400 font-bold">{e.probability}%</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{e.explanation}</p>
          {e.signals.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {e.signals.map((s) => (
                <span key={s.signal} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                  {s.why}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
