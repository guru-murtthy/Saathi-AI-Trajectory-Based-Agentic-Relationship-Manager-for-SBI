import { useEffect, useState } from 'react';
import { api, DNA, FFI, FutureGraph, LifeEvents } from './api';
import { Card } from './components/Card';
import { FFIGauge } from './components/FFIGauge';
import { DNAPanel } from './components/DNAPanel';
import { FutureGraphChart } from './components/FutureGraphChart';
import { LifeEventsPanel } from './components/LifeEvents';
import { GPSPanel } from './components/GPSPanel';
import { RMChat } from './components/RMChat';
import { ProspectsTable } from './components/ProspectsTable';

export default function App() {
  const [customerId, setCustomerId] = useState('rahul');
  const [ffi, setFfi] = useState<FFI | null>(null);
  const [dna, setDna] = useState<DNA | null>(null);
  const [events, setEvents] = useState<LifeEvents | null>(null);
  const [fg, setFg] = useState<FutureGraph | null>(null);
  const [peers, setPeers] = useState<string[]>([]);

  useEffect(() => {
    api.ffi(customerId).then(setFfi).catch(() => setFfi(null));
    api.dna(customerId).then(setDna).catch(() => setDna(null));
    api.lifeEvents(customerId).then(setEvents).catch(() => setEvents(null));
    api.futureGraph(customerId).then(setFg).catch(() => setFg(null));
    api.peers(customerId).then((p) => setPeers(p.insights)).catch(() => setPeers([]));
  }, [customerId]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Saathi AI 3.0
            <span className="text-teal-400"> \u00b7 Financial Future OS</span>
          </h1>
          <p className="text-xs text-slate-400">SBI Relationship Manager Console</p>
        </div>
        <div className="text-right">
          <p className="text-sm">Customer: <span className="font-semibold text-teal-300">{customerId}</span></p>
        </div>
      </header>

      <main className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <Card title="Financial Future Index (FFI)" subtitle="Credit score for the future">
            {ffi ? <FFIGauge ffi={ffi} /> : <Empty />}
          </Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Card title="Financial DNA" subtitle="Behavioural strands">
              {dna ? <DNAPanel dna={dna} /> : <Empty />}
            </Card>
            <Card title="Life Event Predictions" subtitle="With reasoning">
              {events ? <LifeEventsPanel events={events} /> : <Empty />}
            </Card>
          </div>
          <Card title="Financial Future Graph" subtitle="24-month projection">
            {fg ? <FutureGraphChart fg={fg} /> : <Empty />}
          </Card>
          <Card title="Agentic Relationship Manager" subtitle="Observe \u00b7 Reason \u00b7 Predict \u00b7 Explain \u00b7 Recommend">
            <RMChat customerId={customerId} />
          </Card>
        </div>

        <div className="space-y-5">
          <Card title="Financial GPS" subtitle="Goal planning">
            <GPSPanel customerId={customerId} />
          </Card>
          <Card title="Community Intelligence" subtitle="Peer cohort insights">
            {peers.length ? (
              <ul className="space-y-2">
                {peers.map((p, i) => (
                  <li key={i} className="text-sm text-slate-300 flex gap-2">
                    <span className="text-teal-400">\u2022</span>{p}
                  </li>
                ))}
              </ul>
            ) : <Empty />}
          </Card>
          <Card title="SBI High-Value Prospects" subtitle="Home loan \u00b7 click to inspect">
            <ProspectsTable onSelect={setCustomerId} />
          </Card>
        </div>
      </main>
    </div>
  );
}

function Empty() {
  return <p className="text-slate-600 text-sm">No data. Is the backend running on :8000?</p>;
}
