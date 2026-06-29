import { useState } from 'react';
import { api, RM } from '../api';

export function RMChat({ customerId }: { customerId: string }) {
  const [q, setQ] = useState('Why is Rahul a home loan prospect?');
  const [res, setRes] = useState<RM | null>(null);
  const [loading, setLoading] = useState(false);

  // Feedback states
  const [thumbsUp, setThumbsUp] = useState<boolean | null>(null);
  const [comment, setComment] = useState('');
  const [fbSubmitted, setFbSubmitted] = useState(false);
  const [fbSubmitting, setFbSubmitting] = useState(false);

  async function ask() {
    setLoading(true);
    setFbSubmitted(false);
    setThumbsUp(null);
    setComment('');
    try {
      setRes(await api.rm(customerId, q));
    } finally {
      setLoading(false);
    }
  }

  async function submitFeedback() {
    if (thumbsUp === null) return;
    setFbSubmitting(true);
    try {
      await api.feedback(customerId, thumbsUp, comment || null);
      setFbSubmitted(true);
    } catch (e) {
      console.error(e);
    } finally {
      setFbSubmitting(false);
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

          {/* User Feedback Loop Widget */}
          <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-700/50 mt-2">
            <p className="text-xs font-semibold text-slate-300">Was this RM advice helpful?</p>
            {!fbSubmitted ? (
              <div className="mt-2 space-y-2">
                <div className="flex gap-2">
                  <button
                    onClick={() => setThumbsUp(true)}
                    className={`px-3 py-1 rounded text-xs transition ${
                      thumbsUp === true ? 'bg-teal-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    👍 Helpful
                  </button>
                  <button
                    onClick={() => setThumbsUp(false)}
                    className={`px-3 py-1 rounded text-xs transition ${
                      thumbsUp === false ? 'bg-rose-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    👎 Needs Improvement
                  </button>
                </div>
                {thumbsUp !== null && (
                  <div className="flex flex-col gap-2 mt-2">
                    <input
                      type="text"
                      placeholder="Add an optional comment..."
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      className="bg-slate-900 text-slate-200 text-xs rounded px-2 py-1 outline-none border border-slate-700"
                    />
                    <button
                      onClick={submitFeedback}
                      disabled={fbSubmitting}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium py-1 px-3 rounded self-start"
                    >
                      {fbSubmitting ? 'Sending...' : 'Submit Feedback'}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-teal-400 mt-1">Thank you for your feedback!</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
