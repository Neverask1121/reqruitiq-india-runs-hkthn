import { useEffect, useMemo, useState } from 'react';

type RankedCandidate = {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
};

type RankResponse = {
  generated_at?: string;
  total_candidates?: number;
  top_k?: number;
  candidates: RankedCandidate[];
};

const NAV = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'rankings', label: 'Rankings' },
];

function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="rounded-2xl border border-th-border bg-th-surface p-5 shadow-sm theme-transition">
      <div className="text-xs uppercase tracking-[0.2em] text-th-textm">{label}</div>
      <div className="mt-2 text-3xl font-bold text-th-text">{value}</div>
      <div className="mt-2 text-sm text-th-text2">{hint}</div>
    </div>
  );
}

function ScoreBar({ score }: { score: number }) {
  const width = Math.max(0, Math.min(100, score));
  const color = width >= 80 ? 'bg-emerald-500' : width >= 60 ? 'bg-electric' : 'bg-amber-500';

  return (
    <div className="flex items-center gap-3">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-th-alt">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${width}%` }} />
      </div>
      <span className="w-14 text-right text-sm font-semibold text-th-text">{score.toFixed(2)}</span>
    </div>
  );
}

function RankingsTable({
  candidates,
  onSelect,
}: {
  candidates: RankedCandidate[];
  onSelect: (candidate: RankedCandidate) => void;
}) {
  return (
    <div className="overflow-hidden rounded-3xl border border-th-border bg-th-surface shadow-sm theme-transition">
      <div className="border-b border-th-border px-6 py-4">
        <h2 className="text-lg font-semibold text-th-text">Ranked candidates</h2>
        <p className="text-sm text-th-text2">Sorted by descending score, then ascending candidate ID.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-th-border">
          <thead className="bg-th-thead">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-th-textm">Rank</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-th-textm">Candidate ID</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-th-textm">Score</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-th-textm">Reasoning</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-th-border">
            {candidates.map((candidate) => (
              <tr
                key={candidate.candidate_id}
                className="cursor-pointer hover:bg-th-hover"
                onClick={() => onSelect(candidate)}
              >
                <td className="px-6 py-4 text-sm font-semibold text-th-text">{candidate.rank}</td>
                <td className="px-6 py-4 text-sm text-th-text">{candidate.candidate_id}</td>
                <td className="px-6 py-4"><ScoreBar score={candidate.score} /></td>
                <td className="px-6 py-4 text-sm text-th-text2">{candidate.reasoning}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CandidatePreview({ candidate }: { candidate: RankedCandidate | null }) {
  if (!candidate) {
    return (
      <div className="rounded-3xl border border-th-border bg-th-surface p-6 shadow-sm theme-transition">
        <p className="text-sm text-th-text2">Select a ranked candidate to inspect the score and reasoning.</p>
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-th-border bg-th-surface p-6 shadow-sm theme-transition">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-th-textm">Selected candidate</div>
          <h3 className="mt-2 text-2xl font-bold text-th-text">{candidate.candidate_id}</h3>
        </div>
        <div className="rounded-2xl bg-th-alt px-4 py-3 text-right">
          <div className="text-xs uppercase tracking-[0.2em] text-th-textm">Rank</div>
          <div className="text-2xl font-bold text-th-text">#{candidate.rank}</div>
        </div>
      </div>
      <div className="mt-6">
        <div className="text-xs uppercase tracking-[0.2em] text-th-textm">Score</div>
        <div className="mt-2"><ScoreBar score={candidate.score} /></div>
      </div>
      <div className="mt-6">
        <div className="text-xs uppercase tracking-[0.2em] text-th-textm">Reasoning</div>
        <p className="mt-2 text-sm leading-6 text-th-text2">{candidate.reasoning}</p>
      </div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState<'dashboard' | 'rankings'>('dashboard');
  const [rankData, setRankData] = useState<RankResponse | null>(null);
  const [selected, setSelected] = useState<RankedCandidate | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;

    async function loadData() {
      try {
        setLoading(true);
        const response = await fetch('/ranked_candidates.json', { cache: 'no-store' });
        if (!response.ok) {
          throw new Error(`Unable to load ranked_candidates.json (${response.status})`);
        }
        const data = (await response.json()) as RankResponse;
        if (alive) {
          setRankData(data);
          setSelected(data.candidates[0] ?? null);
          setError('');
        }
      } catch (err) {
        if (alive) {
          setError(err instanceof Error ? err.message : 'Unable to load ranked output.');
        }
      } finally {
        if (alive) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      alive = false;
    };
  }, []);

  const candidates = rankData?.candidates ?? [];
  const top5 = useMemo(() => candidates.slice(0, 5), [candidates]);
  const averageScore = useMemo(() => {
    if (!candidates.length) return 0;
    return candidates.reduce((sum, item) => sum + item.score, 0) / candidates.length;
  }, [candidates]);

  return (
    <div className="min-h-screen bg-th-bg text-th-text">
      <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.3em] text-th-textm">Recruitment pipeline</div>
            <h1 className="mt-2 text-4xl font-black tracking-tight text-th-text">Real ranked output, no mock data</h1>
            <p className="mt-3 max-w-2xl text-sm text-th-text2">
              This dashboard reads the generated backend artifact from <code>/ranked_candidates.json</code>, which
              is produced from Member 2&apos;s parsed dataset and the existing scoring pipeline.
            </p>
          </div>
          <div className="flex gap-2 rounded-2xl border border-th-border bg-th-surface p-1 shadow-sm">
            {NAV.map((item) => (
              <button
                key={item.key}
                className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
                  page === item.key ? 'bg-electric text-white' : 'text-th-text2 hover:bg-th-alt hover:text-th-text'
                }`}
                onClick={() => setPage(item.key as 'dashboard' | 'rankings')}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {error ? (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            {error}. Generate the backend artifact first by running the ranker.
          </div>
        ) : null}

        {loading ? (
          <div className="rounded-2xl border border-th-border bg-th-surface px-5 py-4 text-sm text-th-text2">
            Loading ranked candidates...
          </div>
        ) : null}

        {!loading && candidates.length > 0 ? (
          <>
            <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
              <StatCard label="Candidates shown" value={String(candidates.length)} hint="Top 100 from the backend output." />
              <StatCard label="Average score" value={averageScore.toFixed(2)} hint="Computed from the ranked JSON artifact." />
              <StatCard label="Best candidate" value={candidates[0].candidate_id} hint={`Score ${candidates[0].score.toFixed(2)}`} />
              <StatCard label="Submission format" value="CSV + JSON" hint={`Header: candidate_id,rank,score,reasoning`} />
            </div>

            {page === 'dashboard' ? (
              <div className="mt-8 grid grid-cols-1 gap-6 xl:grid-cols-3">
                <div className="xl:col-span-2">
                  <div className="rounded-3xl border border-th-border bg-th-surface p-6 shadow-sm theme-transition">
                    <h2 className="text-lg font-semibold text-th-text">Top 5 candidates</h2>
                    <div className="mt-5 space-y-4">
                      {top5.map((candidate) => (
                        <div key={candidate.candidate_id} className="rounded-2xl border border-th-border bg-th-alt p-4">
                          <div className="flex items-center justify-between gap-4">
                            <div>
                              <div className="text-xs uppercase tracking-[0.2em] text-th-textm">Rank #{candidate.rank}</div>
                              <div className="mt-1 font-semibold text-th-text">{candidate.candidate_id}</div>
                            </div>
                            <div className="w-44">
                              <ScoreBar score={candidate.score} />
                            </div>
                          </div>
                          <p className="mt-3 text-sm text-th-text2">{candidate.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <CandidatePreview candidate={selected} />
              </div>
            ) : (
              <div className="mt-8 grid grid-cols-1 gap-6 xl:grid-cols-3">
                <div className="xl:col-span-2">
                  <RankingsTable candidates={candidates} onSelect={setSelected} />
                </div>
                <CandidatePreview candidate={selected} />
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}
