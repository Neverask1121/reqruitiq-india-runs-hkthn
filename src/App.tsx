import { useState, useEffect, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, CartesianGrid
} from 'recharts';

// ─── Theme Toggle Component ──────────────────────────────────────────────────

function ThemeToggle({ dark, onToggle, collapsed }: { dark: boolean; onToggle: () => void; collapsed: boolean }) {
  return (
    <button
      onClick={onToggle}
      className={`flex items-center gap-3 w-full rounded-lg cursor-pointer transition-all duration-300 group
        ${collapsed ? 'justify-center px-2 py-3' : 'px-4 py-2.5'}
        text-slate-400 hover:text-slate-200 hover:bg-white/5
      `}
      title={collapsed ? (dark ? 'Light Mode' : 'Dark Mode') : undefined}
    >
      <div className="relative w-5 h-5 flex-shrink-0">
        {/* Sun */}
        <svg
          className={`absolute inset-0 w-5 h-5 transition-all duration-500 ${dark ? 'opacity-0 rotate-90 scale-0' : 'opacity-100 rotate-0 scale-100'}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        {/* Moon */}
        <svg
          className={`absolute inset-0 w-5 h-5 transition-all duration-500 ${dark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      </div>
      {!collapsed && (
        <span className="text-sm font-medium truncate">
          {dark ? 'Dark Mode' : 'Light Mode'}
        </span>
      )}
      {!collapsed && (
        <div className={`ml-auto w-9 h-5 rounded-full p-0.5 transition-colors duration-300 ${dark ? 'bg-blue-500' : 'bg-slate-600'}`}>
          <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-300 ${dark ? 'translate-x-4' : 'translate-x-0'}`} />
        </div>
      )}
    </button>
  );
}

// ─── Helper Components ────────────────────────────────────────────────────────

function ScoreBadge({ score }: { score: number }) {
  const cls = score >= 90
    ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20'
    : score >= 80
    ? 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20'
    : score >= 70
    ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20'
    : 'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border theme-transition ${cls}`}>
      {score}%
    </span>
  );
}

function ProgressBar({ value, color = 'bg-electric' }: { value: number; color?: string }) {
  return (
    <div className="w-full bg-gray-100 dark:bg-white/5 rounded-full h-2 overflow-hidden theme-transition">
      <div
        className={`h-full rounded-full ${color} transition-all duration-700 ease-out`}
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isShortlisted = status === 'Shortlisted';
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium theme-transition ${
      isShortlisted
        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20'
        : 'bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20'
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${isShortlisted ? 'bg-emerald-500' : 'bg-amber-500'}`} />
      {status}
    </span>
  );
}

// Card wrapper — single place for surface theming
function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-th-surface border border-th-border rounded-xl shadow-sm theme-transition ${className}`}>
      {children}
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────

const navItems = [
  { key: 'dashboard', icon: '🏠', label: 'Dashboard' },
  { key: 'job', icon: '📄', label: 'Job Intelligence' },
  { key: 'rankings', icon: '👥', label: 'Rankings' },
  { key: 'analytics', icon: '📊', label: 'Analytics' },
  { key: 'compare', icon: '⚖️', label: 'Compare' },
  { key: 'profile', icon: '👤', label: 'Profile' },
];

function Sidebar({ active, onNav, collapsed, dark, onToggleTheme }: {
  active: string; onNav: (k: string) => void; collapsed: boolean; dark: boolean; onToggleTheme: () => void;
}) {
  return (
    <aside className={`fixed top-0 left-0 h-screen sidebar-bg flex flex-col sidebar-transition z-50 ${collapsed ? 'w-[68px]' : 'w-[240px]'}`}>
      {/* Logo */}
      <div className={`flex items-center gap-3 px-5 py-6 border-b border-white/5 ${collapsed ? 'justify-center px-3' : ''}`}>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/20">
          <span className="text-white font-bold text-sm">T</span>
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="text-white font-bold text-base leading-tight tracking-tight">TalentAI</h1>
            <p className="text-slate-500 text-[10px] font-medium tracking-widest uppercase">Recruiter</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map((item) => {
          const isActive = active === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onNav(item.key)}
              className={`w-full flex items-center gap-3 rounded-lg sidebar-transition cursor-pointer
                ${collapsed ? 'justify-center px-2 py-3' : 'px-4 py-2.5'}
                ${isActive
                  ? 'bg-blue-500/10 text-blue-400 nav-active-bar'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }
              `}
              title={collapsed ? item.label : undefined}
            >
              <span className="text-lg flex-shrink-0">{item.icon}</span>
              {!collapsed && <span className="text-sm font-medium truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Theme Toggle */}
      <div className="px-2 pb-2">
        <ThemeToggle dark={dark} onToggle={onToggleTheme} collapsed={collapsed} />
      </div>

      {/* Footer */}
      <div className={`px-4 py-4 border-t border-white/5 ${collapsed ? 'px-2' : ''}`}>
        <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-semibold">HR</span>
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <p className="text-white text-sm font-medium truncate">HR Manager</p>
              <p className="text-slate-500 text-xs truncate">admin@talentai.io</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

// ─── Dashboard Page ───────────────────────────────────────────────────────────

function DashboardPage({ candidates, onViewCandidate }: { candidates: any[]; onViewCandidate: (id: number) => void }) {
  const stats = [
    { label: 'Candidates Analyzed', value: candidates.length.toLocaleString(), icon: '👥',
      light: 'bg-blue-50 border-blue-100 text-blue-600',
      dark: 'dark:bg-blue-500/10 dark:border-blue-500/20 dark:text-blue-400' },
    { label: 'Top Match Score', value: candidates.length ? `${Math.max(...candidates.map(c => c.matchScore))}%` : '—', icon: '🎯',
      light: 'bg-purple-50 border-purple-100 text-purple-600',
      dark: 'dark:bg-purple-500/10 dark:border-purple-500/20 dark:text-purple-400' },
    { label: 'Qualified Candidates', value: candidates.filter(c => c.matchScore >= 80).length.toLocaleString(), icon: '✅',
      light: 'bg-emerald-50 border-emerald-100 text-emerald-600',
      dark: 'dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400' },
    { label: 'Behavior Signals Used', value: '23', icon: '🧠',
      light: 'bg-cyan-50 border-cyan-100 text-cyan-600',
      dark: 'dark:bg-cyan-500/10 dark:border-cyan-500/20 dark:text-cyan-400' },
  ];
  const top10 = candidates.slice(0, 10);

  return (
    <div className="animate-fade-in-up">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-th-text">Dashboard</h2>
        <p className="text-th-text2 text-sm mt-1">AI-powered recruitment intelligence at a glance</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        {stats.map((s, i) => (
          <div key={i} className={`border rounded-xl p-5 theme-transition hover:shadow-md transition-shadow duration-300 ${s.light} ${s.dark}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{s.icon}</span>
              <svg className="w-4 h-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <p className="text-3xl font-bold">{s.value}</p>
            <p className="text-sm mt-1 font-medium opacity-70">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Top 10 Table */}
      <Card>
        <div className="px-6 py-5 border-b border-th-border flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-th-text">Top 10 AI Recommended Candidates</h3>
            <p className="text-th-text2 text-sm mt-0.5">Ranked by composite match score</p>
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-500/10 px-3 py-1.5 rounded-full border border-purple-100 dark:border-purple-500/20 theme-transition">
            <span className="animate-pulse-soft">✨</span> AI Ranked
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-th-thead border-b border-th-border theme-transition">
                {['Rank', 'Candidate', 'Role', 'Match Score', 'Action'].map(h => (
                  <th key={h} className="text-left text-xs font-semibold text-th-textm uppercase tracking-wider px-6 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {top10.map((c, i) => (
                <tr key={c.id} className="border-b border-th-border hover:bg-th-hover theme-transition">
                  <td className="px-6 py-4">
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                      i < 3 ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' : 'bg-gray-100 dark:bg-white/10 text-th-text2'
                    }`}>{i + 1}</span>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm font-semibold text-th-text">{c.name}</p>
                    <p className="text-xs text-th-text2">{c.company}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-th-text2">{c.role}</td>
                  <td className="px-6 py-4"><ScoreBadge score={c.matchScore} /></td>
                  <td className="px-6 py-4">
                    <button onClick={() => onViewCandidate(c.id)}
                      className="text-xs font-medium text-electric dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 px-3 py-1.5 rounded-lg transition-colors duration-200 cursor-pointer">
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// ─── Job Intelligence Page ────────────────────────────────────────────────────

function JobIntelligencePage() {
  const jobDetails = [
    { label: 'Role', value: 'Senior Data Engineer', icon: '💼' },
    { label: 'Experience', value: '5+ years', icon: '📅' },
    { label: 'Industry', value: 'FinTech', icon: '🏦' },
    { label: 'Location', value: 'Remote', icon: '🌐' },
  ];
  const requiredSkills = ['Python', 'SQL', 'AWS', 'Docker', 'Spark'];
  const preferredSkills = ['Kubernetes', 'GCP', 'Terraform'];
  const hiddenReqs = ['Leadership', 'Startup Mindset', 'Product Thinking', 'Ownership'];

  return (
    <div className="animate-fade-in-up">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-th-text">Job Intelligence</h2>
        <p className="text-th-text2 text-sm mt-1">AI-analyzed role requirements and insights</p>
      </div>

      {/* Job Overview */}
      <Card className="p-6 mb-6">
        <h3 className="text-base font-semibold text-th-text mb-5 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-electric" />Job Overview
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {jobDetails.map((d, i) => (
            <div key={i} className="bg-th-alt rounded-xl p-4 border border-th-border theme-transition">
              <span className="text-xl">{d.icon}</span>
              <p className="text-xs text-th-textm mt-2 font-medium uppercase tracking-wide">{d.label}</p>
              <p className="text-base font-semibold text-th-text mt-1">{d.value}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Skills */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald" />Required Skills
          </h3>
          <div className="flex flex-wrap gap-2">
            {requiredSkills.map((s) => (
              <span key={s} className="bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20 px-4 py-2 rounded-lg text-sm font-medium theme-transition">
                {s}
              </span>
            ))}
          </div>
        </Card>
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber" />Preferred Skills
          </h3>
          <div className="flex flex-wrap gap-2">
            {preferredSkills.map((s) => (
              <span key={s} className="bg-th-surface text-th-text2 border-2 border-dashed border-th-border px-4 py-2 rounded-lg text-sm font-medium theme-transition">
                {s}
              </span>
            ))}
          </div>
        </Card>
      </div>

      {/* AI Insights */}
      <div className="rounded-xl bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700 p-6 shadow-lg shadow-blue-500/10">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xl animate-pulse-soft">✨</span>
          <h3 className="text-white text-base font-semibold">AI-Discovered Hidden Requirements</h3>
        </div>
        <p className="text-blue-100 text-sm mb-5">
          Our AI analyzed 500+ similar job postings and identified these implicit requirements that significantly impact candidate success in this role.
        </p>
        <div className="flex flex-wrap gap-3">
          {hiddenReqs.map((r) => (
            <span key={r} className="bg-white/15 backdrop-blur text-white px-4 py-2 rounded-full text-sm font-medium border border-white/20 hover:bg-white/25 transition-colors duration-200">
              {r}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Rankings Page ────────────────────────────────────────────────────────────

function RankingsPage({ candidates, onViewCandidate }: { candidates: any[]; onViewCandidate: (id: number) => void }) {
  const [search, setSearch] = useState('');
  const [expFilter, setExpFilter] = useState('All');
  const [skillFilter, setSkillFilter] = useState('All');
  const [locFilter, setLocFilter] = useState('All');
  const [scoreFilter, setScoreFilter] = useState('All');

  const filtered = candidates.filter((c) => {
    if (search && !c.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (scoreFilter === '90+' && c.matchScore < 90) return false;
    if (scoreFilter === '80-90' && (c.matchScore < 80 || c.matchScore >= 90)) return false;
    if (scoreFilter === '70-80' && (c.matchScore < 70 || c.matchScore >= 80)) return false;
    if (scoreFilter === '<70' && c.matchScore >= 70) return false;
    return true;
  });

  const selectCls = "bg-th-surface border border-th-border rounded-lg px-3 py-2.5 text-sm text-th-text focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all duration-200 cursor-pointer theme-transition";

  return (
    <div className="animate-fade-in-up">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-th-text">Candidate Rankings</h2>
        <p className="text-th-text2 text-sm mt-1">AI-ranked candidates with multi-dimensional scoring</p>
      </div>

      {/* Filters */}
      <Card className="p-5 mb-6">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex-1 min-w-[220px]">
            <input type="text" placeholder="🔍  Search candidates..."
              value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-th-input border border-th-border rounded-lg px-4 py-2.5 text-sm text-th-text focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 placeholder:text-th-textm transition-all duration-200 theme-transition"
            />
          </div>
          <select value={expFilter} onChange={(e) => setExpFilter(e.target.value)} className={selectCls}>
            <option value="All">Experience: All</option><option value="0-2">0-2 years</option><option value="2-5">2-5 years</option><option value="5+">5+ years</option>
          </select>
          <select value={skillFilter} onChange={(e) => setSkillFilter(e.target.value)} className={selectCls}>
            <option value="All">Skill: All</option><option value="Python">Python</option><option value="SQL">SQL</option><option value="AWS">AWS</option>
          </select>
          <select value={locFilter} onChange={(e) => setLocFilter(e.target.value)} className={selectCls}>
            <option value="All">Location: All</option><option value="Remote">Remote</option><option value="Hybrid">Hybrid</option><option value="On-site">On-site</option>
          </select>
          <select value={scoreFilter} onChange={(e) => setScoreFilter(e.target.value)} className={selectCls}>
            <option value="All">Score: All</option><option value="90+">90%+</option><option value="80-90">80-90%</option><option value="70-80">70-80%</option><option value="<70">Below 70%</option>
          </select>
        </div>
      </Card>

      {/* Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-th-thead border-b border-th-border theme-transition">
                {['Rank', 'Name', 'Match Score', 'Skill', 'Behavior', 'Experience', 'Action'].map(h => (
                  <th key={h} className={`text-left text-xs font-semibold text-th-textm uppercase tracking-wider px-5 py-3 ${h === 'Match Score' ? 'min-w-[160px]' : ''}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((c, i) => (
                <tr key={c.id} className="border-b border-th-border hover:bg-th-hover theme-transition">
                  <td className="px-5 py-4">
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                      i < 3 ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' : 'bg-gray-100 dark:bg-white/10 text-th-text2'
                    }`}>{i + 1}</span>
                  </td>
                  <td className="px-5 py-4">
                    <p className="text-sm font-semibold text-th-text">{c.name}</p>
                    <p className="text-xs text-th-text2">{c.role}</p>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex-1"><ProgressBar value={c.matchScore} color={c.matchScore >= 85 ? 'bg-emerald' : c.matchScore >= 70 ? 'bg-electric' : 'bg-amber'} /></div>
                      <span className="text-xs font-semibold text-th-text w-9 text-right">{c.matchScore}%</span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-th-text2 font-medium">{c.skillScore}%</td>
                  <td className="px-5 py-4 text-sm text-th-text2 font-medium">{c.behaviorScore}%</td>
                  <td className="px-5 py-4 text-sm text-th-text2 font-medium">{c.experienceScore}%</td>
                  <td className="px-5 py-4">
                    <button onClick={() => onViewCandidate(c.id)}
                      className="text-xs font-medium text-electric dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 px-3 py-1.5 rounded-lg transition-colors duration-200 cursor-pointer">
                      View Profile →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// ─── Candidate Profile Page ───────────────────────────────────────────────────

function CandidateProfilePage({ candidate, onBack }: { candidate: any; onBack: () => void }) {
  const c = candidate;
  const behavioralColors: Record<string, { light: string; dark: string }> = {
    Leadership:        { light: 'text-blue-600 bg-blue-50 border-blue-100',     dark: 'dark:text-blue-400 dark:bg-blue-500/10 dark:border-blue-500/20' },
    Collaboration:     { light: 'text-emerald-600 bg-emerald-50 border-emerald-100', dark: 'dark:text-emerald-400 dark:bg-emerald-500/10 dark:border-emerald-500/20' },
    'Learning Agility':{ light: 'text-purple-600 bg-purple-50 border-purple-100',  dark: 'dark:text-purple-400 dark:bg-purple-500/10 dark:border-purple-500/20' },
    Consistency:       { light: 'text-cyan-600 bg-cyan-50 border-cyan-100',     dark: 'dark:text-cyan-400 dark:bg-cyan-500/10 dark:border-cyan-500/20' },
    Ownership:         { light: 'text-amber-600 bg-amber-50 border-amber-100',   dark: 'dark:text-amber-400 dark:bg-amber-500/10 dark:border-amber-500/20' },
  };
  const behavioralIcons: Record<string, string> = {
    Leadership: '👑', Collaboration: '🤝', 'Learning Agility': '🚀', Consistency: '📌', Ownership: '🎯',
  };

  return (
    <div className="animate-fade-in-up">
      <button onClick={onBack}
        className="flex items-center gap-2 text-sm text-th-text2 hover:text-electric mb-6 transition-colors duration-200 cursor-pointer">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Rankings
      </button>

      {/* Header */}
      <Card className="p-6 mb-6">
        <div className="flex flex-wrap items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-blue-500/20">
            {c.name.split(' ').map((n: string) => n[0]).join('')}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold text-th-text">{c.name}</h2>
            <p className="text-th-text2 text-sm mt-1">{c.role} at <span className="font-medium text-th-text">{c.company}</span></p>
            <div className="flex flex-wrap items-center gap-3 mt-3">
              <ScoreBadge score={c.matchScore} />
              <StatusBadge status={c.status} />
            </div>
          </div>
        </div>
      </Card>

      {/* AI Summary */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-500/10 dark:to-blue-500/10 rounded-xl border border-purple-100 dark:border-purple-500/20 p-6 mb-6 theme-transition">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg animate-pulse-soft">✨</span>
          <h3 className="text-base font-semibold text-purple-800 dark:text-purple-300">AI Summary</h3>
        </div>
        <p className="text-purple-900/80 dark:text-purple-200/80 text-sm italic leading-relaxed">{c.aiSummary}</p>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald" /> Strengths
          </h3>
          <ul className="space-y-3">
            {c.strengths.map((s: string, i: number) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <span className="text-emerald-500 mt-0.5 font-bold">✓</span>
                <span className="text-th-text2">{s}</span>
              </li>
            ))}
          </ul>
        </Card>
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose" /> Weaknesses
          </h3>
          <ul className="space-y-3">
            {c.weaknesses.map((w: string, i: number) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <span className="text-rose-500 mt-0.5 font-bold">✗</span>
                <span className="text-th-text2">{w}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Skill Match */}
      <Card className="p-6 mb-6">
        <h3 className="text-base font-semibold text-th-text mb-5 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-electric" /> Skill Match
        </h3>
        <div className="space-y-4">
          {Object.entries(c.skills as Record<string, number>).map(([skill, score]) => (
            <div key={skill} className="flex items-center gap-4">
              <span className="text-sm font-medium text-th-text2 w-20 text-right">{skill}</span>
              <div className="flex-1"><ProgressBar value={Number(score)} color={Number(score) >= 85 ? 'bg-emerald' : Number(score) >= 70 ? 'bg-electric' : 'bg-amber'} /></div>
              <span className="text-sm font-semibold text-th-text w-12 text-right">{score}%</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Behavioral Signals */}
      <Card className="p-6">
        <h3 className="text-base font-semibold text-th-text mb-5 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-purple" /> Behavioral Signals
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.entries(c.behavioral as Record<string, number>).map(([signal, score]) => {
            const colors = behavioralColors[signal] || { light: 'bg-gray-50 text-gray-600 border-gray-100', dark: 'dark:bg-white/5 dark:text-gray-400 dark:border-white/10' };
            return (
              <div key={signal} className={`rounded-xl p-4 border text-center theme-transition ${colors.light} ${colors.dark}`}>
                <span className="text-2xl">{behavioralIcons[signal] || '📊'}</span>
                <p className="text-xs font-medium mt-2 opacity-80">{signal}</p>
                <p className="text-2xl font-bold mt-1">{score}<span className="text-sm font-normal opacity-60">/10</span></p>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

// ─── Analytics Page ───────────────────────────────────────────────────────────

function AnalyticsPage({ candidates }: { candidates: any[] }) {
  // Compute score distribution
  const ranges = ['0-20', '20-40', '40-60', '60-80', '80-100'];
  const distribution = ranges.map(range => {
    const [low, high] = range.split('-').map(Number);
    const count = candidates.filter(c => c.matchScore >= low && c.matchScore < high).length;
    return { range, count };
  });

  // Top skills (fake but keep UI)
  const topSkillsData = [
    { skill: 'Python', count: 8420 },
    { skill: 'SQL', count: 7850 },
    { skill: 'Java', count: 6200 },
    { skill: 'AWS', count: 5980 },
    { skill: 'Docker', count: 4320 },
  ];

  const experienceBreakdown = [
    { name: '0-2 yrs', value: 15 },
    { name: '2-5 yrs', value: 30 },
    { name: '5-10 yrs', value: 38 },
    { name: '10+ yrs', value: 17 },
  ];

  const behavioralAvg = [
    { signal: 'Leadership', score: 6.8 },
    { signal: 'Collaboration', score: 7.9 },
    { signal: 'Learning', score: 7.8 },
    { signal: 'Consistency', score: 7.6 },
    { signal: 'Ownership', score: 7.7 },
  ];

  const PIE_COLORS = ['#3B82F6', '#8B5CF6', '#06B6D4', '#10B981'];

  return (
    <div className="animate-fade-in-up">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-th-text">Analytics</h2>
        <p className="text-th-text2 text-sm mt-1">Aggregate insights across your candidate pipeline</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution */}
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-1">Candidate Score Distribution</h3>
          <p className="text-xs text-th-text2 mb-5">Distribution of match scores across the pool</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {distribution.map((_, i) => (
                  <Cell key={i} fill={['#94A3B8', '#FCD34D', '#60A5FA', '#3B82F6', '#8B5CF6'][i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Top Skills */}
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-1">Top Skills Across Candidates</h3>
          <p className="text-xs text-th-text2 mb-5">Most common skills in the talent pool</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={topSkillsData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="skill" type="category" width={60} />
              <Tooltip />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {topSkillsData.map((_, i) => (
                  <Cell key={i} fill={['#3B82F6', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B'][i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Experience Breakdown */}
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-1">Experience Breakdown</h3>
          <p className="text-xs text-th-text2 mb-5">Years of experience distribution</p>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={experienceBreakdown} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} dataKey="value" stroke="none">
                {experienceBreakdown.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-4 mt-2">
            {experienceBreakdown.map((d, i) => (
              <div key={d.name} className="flex items-center gap-2 text-xs text-th-text2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: PIE_COLORS[i] }} />
                {d.name} ({d.value}%)
              </div>
            ))}
          </div>
        </Card>

        {/* Behavioral Radar */}
        <Card className="p-6">
          <h3 className="text-base font-semibold text-th-text mb-1">Average Behavioral Signals</h3>
          <p className="text-xs text-th-text2 mb-5">Aggregate behavioral assessment averages</p>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={behavioralAvg} cx="50%" cy="50%" outerRadius={90}>
              <PolarGrid />
              <PolarAngleAxis dataKey="signal" />
              <Radar name="Avg Score" dataKey="score" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.15} strokeWidth={2} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}

// ─── Compare Candidates Page ──────────────────────────────────────────────────

function ComparePage({ candidates }: { candidates: any[] }) {
  const [idA, setIdA] = useState(candidates.length > 0 ? candidates[0].id : null);
  const [idB, setIdB] = useState(candidates.length > 1 ? candidates[1].id : null);

  const a = candidates.find(c => c.id === idA) || candidates[0];
  const b = candidates.find(c => c.id === idB) || candidates[0];

  const metrics = [
    { label: 'Match Score', keyA: a.matchScore, keyB: b.matchScore },
    { label: 'Skill Score', keyA: a.skillScore, keyB: b.skillScore },
    { label: 'Behavior Score', keyA: a.behaviorScore, keyB: b.behaviorScore },
    { label: 'Experience Score', keyA: a.experienceScore, keyB: b.experienceScore },
  ];

  const getVerdict = () => {
    const totalA = a.matchScore + a.skillScore + a.behaviorScore + a.experienceScore;
    const totalB = b.matchScore + b.skillScore + b.behaviorScore + b.experienceScore;
    const winner = totalA >= totalB ? a : b;
    const loser = totalA >= totalB ? b : a;
    if (totalA === totalB) {
      return `Both ${a.name} and ${b.name} show remarkably similar profiles. The choice should be made based on cultural fit and team dynamics. We recommend interviewing both candidates to assess soft skills and alignment with team values.`;
    }
    return `Based on our AI analysis, ${winner.name} is the stronger candidate overall with a composite advantage of ${Math.abs(totalA - totalB)} points. ${winner.name}'s strengths in ${winner.strengths[0].toLowerCase()} and ${winner.strengths[1].toLowerCase()} give them an edge. However, ${loser.name} brings unique value through ${loser.strengths[0].toLowerCase()}, which could be strategically important depending on team needs.`;
  };

  const selectCls = "bg-th-surface border border-th-border rounded-lg px-4 py-2.5 text-sm text-th-text focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all duration-200 cursor-pointer w-full theme-transition";

  return (
    <div className="animate-fade-in-up">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-th-text">Compare Candidates</h2>
        <p className="text-th-text2 text-sm mt-1">Side-by-side AI-powered comparison</p>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
        <Card className="p-5">
          <label className="text-xs font-semibold text-th-textm uppercase tracking-wide mb-2 block">Candidate A</label>
          <select value={idA} onChange={(e) => setIdA(Number(e.target.value))} className={selectCls}>
            {candidates.map(c => <option key={c.id} value={c.id}>{c.name} — {c.role}</option>)}
          </select>
          <div className="flex items-center gap-3 mt-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
              {a.name.split(' ').map((n: string) => n[0]).join('')}
            </div>
            <div>
              <p className="text-sm font-semibold text-th-text">{a.name}</p>
              <p className="text-xs text-th-text2">{a.company}</p>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <label className="text-xs font-semibold text-th-textm uppercase tracking-wide mb-2 block">Candidate B</label>
          <select value={idB} onChange={(e) => setIdB(Number(e.target.value))} className={selectCls}>
            {candidates.map(c => <option key={c.id} value={c.id}>{c.name} — {c.role}</option>)}
          </select>
          <div className="flex items-center gap-3 mt-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-emerald-500 flex items-center justify-center text-white text-sm font-bold">
              {b.name.split(' ').map((n: string) => n[0]).join('')}
            </div>
            <div>
              <p className="text-sm font-semibold text-th-text">{b.name}</p>
              <p className="text-xs text-th-text2">{b.company}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Comparison Table */}
      <Card className="overflow-hidden mb-6">
        <table className="w-full">
          <thead>
            <tr className="bg-th-thead border-b border-th-border theme-transition">
              <th className="text-left text-xs font-semibold text-th-textm uppercase tracking-wider px-6 py-3">Metric</th>
              <th className="text-center text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider px-6 py-3">{a.name.split(' ')[0]}</th>
              <th className="text-center text-xs font-semibold text-th-textm uppercase tracking-wider px-6 py-3">VS</th>
              <th className="text-center text-xs font-semibold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider px-6 py-3">{b.name.split(' ')[0]}</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => {
              const aWins = m.keyA > m.keyB;
              const bWins = m.keyB > m.keyA;
              return (
                <tr key={m.label} className="border-b border-th-border theme-transition">
                  <td className="px-6 py-4 text-sm font-medium text-th-text">{m.label}</td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col items-center gap-2">
                      <span className={`text-lg font-bold ${aWins ? 'text-blue-600 dark:text-blue-400' : 'text-th-text2'}`}>{m.keyA}%</span>
                      <div className="w-full max-w-[120px]">
                        <div className="w-full bg-gray-100 dark:bg-white/5 rounded-full h-2 theme-transition">
                          <div className={`h-full rounded-full transition-all duration-700 ${aWins ? 'bg-blue-500' : 'bg-gray-300 dark:bg-white/20'}`} style={{ width: `${m.keyA}%` }} />
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center"><span className="text-xs text-th-textm font-medium">vs</span></td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col items-center gap-2">
                      <span className={`text-lg font-bold ${bWins ? 'text-cyan-600 dark:text-cyan-400' : 'text-th-text2'}`}>{m.keyB}%</span>
                      <div className="w-full max-w-[120px]">
                        <div className="w-full bg-gray-100 dark:bg-white/5 rounded-full h-2 theme-transition">
                          <div className={`h-full rounded-full transition-all duration-700 ${bWins ? 'bg-cyan-500' : 'bg-gray-300 dark:bg-white/20'}`} style={{ width: `${m.keyB}%` }} />
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>

      {/* AI Verdict */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-500/10 dark:to-blue-500/10 rounded-xl border border-purple-100 dark:border-purple-500/20 p-6 theme-transition">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg animate-pulse-soft">🧠</span>
          <h3 className="text-base font-semibold text-purple-800 dark:text-purple-300">AI Verdict</h3>
        </div>
        <p className="text-purple-900/80 dark:text-purple-200/80 text-sm leading-relaxed">{getVerdict()}</p>
      </div>
    </div>
  );
}

// ─── Profile Page (User Profile) ──────────────────────────────────────────────

function UserProfilePage() {
  return (
    <div className="animate-fade-in-up">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-th-text">Your Profile</h2>
        <p className="text-th-text2 text-sm mt-1">Account settings and preferences</p>
      </div>

      <Card className="p-8 mb-6">
        <div className="flex flex-wrap items-center gap-6 mb-8 pb-8 border-b border-th-border">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-purple-500/20">
            HR
          </div>
          <div>
            <h3 className="text-xl font-bold text-th-text">HR Manager</h3>
            <p className="text-th-text2 text-sm">admin@talentai.io</p>
            <p className="text-th-text2 text-xs mt-1">Member since January 2024</p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {[
            { label: 'Full Name', value: 'HR Manager' },
            { label: 'Email', value: 'admin@talentai.io' },
            { label: 'Organization', value: 'TalentAI Corp' },
            { label: 'Role', value: 'Hiring Manager' },
            { label: 'Department', value: 'Engineering Recruitment' },
            { label: 'Plan', value: 'Enterprise' },
          ].map((f) => (
            <div key={f.label}>
              <label className="text-xs font-semibold text-th-textm uppercase tracking-wide">{f.label}</label>
              <p className="text-sm text-th-text font-medium mt-1 bg-th-alt rounded-lg px-4 py-3 border border-th-border theme-transition">{f.value}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-base font-semibold text-th-text mb-4">Usage Statistics</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: 'Jobs Analyzed', value: '24', icon: '📄',
              light: 'bg-blue-50 text-blue-600 border-blue-100',
              dark: 'dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20' },
            { label: 'Candidates Reviewed', value: '1,247', icon: '👥',
              light: 'bg-purple-50 text-purple-600 border-purple-100',
              dark: 'dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/20' },
            { label: 'AI Reports Generated', value: '89', icon: '📊',
              light: 'bg-emerald-50 text-emerald-600 border-emerald-100',
              dark: 'dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20' },
          ].map((s) => (
            <div key={s.label} className={`rounded-xl p-5 border theme-transition ${s.light} ${s.dark}`}>
              <span className="text-2xl">{s.icon}</span>
              <p className="text-2xl font-bold mt-2">{s.value}</p>
              <p className="text-xs font-medium mt-1 opacity-70">{s.label}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('talentai-theme');
      if (saved) return saved === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [candidates, setCandidates] = useState<any[]>([]);

  // ─── Load data from JSON ──────────────────────────────────────────────────────
  useEffect(() => {
    let alive = true;
    async function loadData() {
      try {
        setLoading(true);
        const resp = await fetch('/ranked_candidates.json', { cache: 'no-store' });
        if (!resp.ok) throw new Error(`Failed to load /ranked_candidates.json (${resp.status})`);
        const json = await resp.json();
        if (!alive) return;

        // Transform JSON items into the full candidate shape expected by the UI
        const raw = json.candidates || json; // adapt to actual structure
        const list = Array.isArray(raw) ? raw : [];
        const transformed = list.map((item: any, index: number) => {
          const score = item.score || 0;
          // Derive sub-scores with slight variation to keep charts interesting
          const skillScore = Math.min(100, Math.max(0, score + (Math.random() * 6 - 3)));
          const behaviorScore = Math.min(100, Math.max(0, score + (Math.random() * 8 - 4)));
          const experienceScore = Math.min(100, Math.max(0, score + (Math.random() * 10 - 5)));

          // Generate mock behavioural scores (0-10) based on overall score
          const baseBehavior = (score / 100) * 10;
          const behavioral = {
            Leadership: Math.min(10, Math.max(0, baseBehavior + (Math.random() * 2 - 1))),
            Collaboration: Math.min(10, Math.max(0, baseBehavior + (Math.random() * 2 - 1))),
            'Learning Agility': Math.min(10, Math.max(0, baseBehavior + (Math.random() * 2 - 1))),
            Consistency: Math.min(10, Math.max(0, baseBehavior + (Math.random() * 2 - 1))),
            Ownership: Math.min(10, Math.max(0, baseBehavior + (Math.random() * 2 - 1))),
          };

          // Mock skills
          const skills = {
            Python: Math.min(100, Math.max(0, score + (Math.random() * 10 - 5))),
            AWS: Math.min(100, Math.max(0, score + (Math.random() * 10 - 5))),
            SQL: Math.min(100, Math.max(0, score + (Math.random() * 10 - 5))),
            Docker: Math.min(100, Math.max(0, score + (Math.random() * 10 - 5))),
            Spark: Math.min(100, Math.max(0, score + (Math.random() * 10 - 5))),
          };

          // Strengths / weaknesses – generated from reasoning if available
          const reasoning = item.reasoning || 'No reasoning provided.';
          const strengthPhrases = [
            'Strong technical foundation',
            'Excellent problem-solving skills',
            'Great team player',
            'Proven track record of delivery',
            'Adaptable and quick learner',
          ];
          const weaknessPhrases = [
            'Limited experience with cloud infrastructure',
            'Could improve communication skills',
            'Needs mentoring in leadership',
            'Less exposure to big data tools',
            'Tends to over-engineer solutions',
          ];
          // Pick two random each
          const strengths = strengthPhrases.sort(() => Math.random() - 0.5).slice(0, 2);
          const weaknesses = weaknessPhrases.sort(() => Math.random() - 0.5).slice(0, 2);

          return {
            id: index + 1, // fallback numeric id
            name: item.candidate_id || `Candidate ${index + 1}`,
            role: 'Data Engineer', // placeholder
            company: 'Tech Corp', // placeholder
            matchScore: Math.round(score),
            skillScore: Math.round(skillScore),
            behaviorScore: Math.round(behaviorScore),
            experienceScore: Math.round(experienceScore),
            status: score >= 80 ? 'Shortlisted' : 'Under Review',
            skills,
            behavioral,
            strengths,
            weaknesses,
            aiSummary: reasoning,
            // keep original fields for reference
            rank: item.rank,
            reasoning: item.reasoning,
          };
        });

        // Sort by rank if available, else by score descending
        transformed.sort((a, b) => (a.rank || 0) - (b.rank || 0) || b.matchScore - a.matchScore);
        setCandidates(transformed);
        setError('');
      } catch (err) {
        if (alive) {
          setError(err instanceof Error ? err.message : 'Unknown error loading data.');
        }
      } finally {
        if (alive) setLoading(false);
      }
    }
    loadData();
    return () => { alive = false; };
  }, []);

  // ─── Theme handling ──────────────────────────────────────────────────────────
  useEffect(() => {
    localStorage.setItem('talentai-theme', darkMode ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  useEffect(() => {
    const handleResize = () => setSidebarCollapsed(window.innerWidth < 768);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const viewCandidate = (id: number) => {
    setSelectedCandidateId(id);
    setPage('candidate');
  };

  const handleNav = (key: string) => {
    setPage(key);
    setSelectedCandidateId(null);
  };

  const selectedCandidate = candidates.find(c => c.id === selectedCandidateId);

  const renderPage = () => {
    if (page === 'candidate' && selectedCandidate) {
      return <CandidateProfilePage candidate={selectedCandidate} onBack={() => setPage('rankings')} />;
    }
    switch (page) {
      case 'dashboard': return <DashboardPage candidates={candidates} onViewCandidate={viewCandidate} />;
      case 'job': return <JobIntelligencePage />;
      case 'rankings': return <RankingsPage candidates={candidates} onViewCandidate={viewCandidate} />;
      case 'analytics': return <AnalyticsPage candidates={candidates} />;
      case 'compare': return <ComparePage candidates={candidates} />;
      case 'profile': return <UserProfilePage />;
      default: return <DashboardPage candidates={candidates} onViewCandidate={viewCandidate} />;
    }
  };

  return (
    <div className={`min-h-screen bg-th-bg flex transition-colors duration-300 ${darkMode ? 'dark' : ''}`}>
      <Sidebar
        active={page === 'candidate' ? 'rankings' : page}
        onNav={handleNav}
        collapsed={sidebarCollapsed}
        dark={darkMode}
        onToggleTheme={() => setDarkMode(!darkMode)}
      />
      <main className={`flex-1 sidebar-transition ${sidebarCollapsed ? 'ml-[68px]' : 'ml-[240px]'}`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-8">
          {loading ? (
            <div className="text-th-text2">Loading candidate data…</div>
          ) : error ? (
            <div className="rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700 dark:border-rose-800 dark:bg-rose-900/20 dark:text-rose-300">
              Error: {error}. Please ensure <code>/ranked_candidates.json</code> is present.
            </div>
          ) : (
            renderPage()
          )}
        </div>
      </main>
    </div>
  );
}