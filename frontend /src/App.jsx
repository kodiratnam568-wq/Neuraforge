import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function handleAnalyze() {
    if (!url.trim()) return
    setError('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_url: url.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Analysis failed')
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="hero">
        <div className="hero-logo">⚡ NeuraForge</div>
        <div className="hero-tagline">AI-Powered Developer Onboarding Assistant</div>
      </div>

      <div className="input-card">
        <div className="input-row">
          <input
            className="url-input"
            type="text"
            placeholder="https://github.com/owner/repository"
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && handleAnalyze()}
            disabled={loading}
          />
          <button className="analyze-btn" onClick={handleAnalyze} disabled={loading || !url.trim()}>
            {loading ? 'Analyzing…' : 'Analyze'}
          </button>
        </div>
        {error && <div className="error-msg">⚠ {error}</div>}
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <div>Scanning repository and generating analysis…</div>
          <div style={{ fontSize: '0.85rem', marginTop: 8 }}>This takes 15–30 seconds</div>
        </div>
      )}

      {result && <Report data={result} />}
    </div>
  )
}

function Report({ data }) {
  const a = data.analysis

  return (
    <div className="report">
      <div className="report-header">
        <div className="repo-name">📦 {data.repo}</div>
        <div className="stats-pills">
          <span className="pill">{data.stats.total_files} files</span>
          <span className="pill">{data.stats.code_files_count} code</span>
          <span className="pill">{data.stats.config_files_count} config</span>
        </div>
      </div>

      {/* Project Overview */}
      <div className="section">
        <div className="section-title">Project Overview</div>
        <p>{a.project_overview}</p>
      </div>

      {/* Tech Stack */}
      <div className="section">
        <div className="section-title">Tech Stack</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {a.tech_stack.languages?.length > 0 && (
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: 6 }}>Languages</div>
              <div className="badges">
                {a.tech_stack.languages.map(l => <span key={l} className="badge">{l}</span>)}
              </div>
            </div>
          )}
          {a.tech_stack.frameworks?.length > 0 && (
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: 6 }}>Frameworks & Libraries</div>
              <div className="badges">
                {a.tech_stack.frameworks.map(f => <span key={f} className="badge">{f}</span>)}
              </div>
            </div>
          )}
          {a.tech_stack.databases?.length > 0 && (
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: 6 }}>Databases</div>
              <div className="badges">
                {a.tech_stack.databases.map(d => <span key={d} className="badge db">{d}</span>)}
              </div>
            </div>
          )}
          {a.tech_stack.tools?.length > 0 && (
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: 6 }}>Tools</div>
              <div className="badges">
                {a.tech_stack.tools.map(t => <span key={t} className="badge tool">{t}</span>)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Important Files */}
      {a.important_files?.length > 0 && (
        <div className="section">
          <div className="section-title">Important Files</div>
          <table className="file-table">
            <tbody>
              {a.important_files.map((f, i) => (
                <tr key={i}>
                  <td className="file-path">📄 {f.path}</td>
                  <td className="file-role">{f.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Architecture */}
      {a.architecture && (
        <div className="section">
          <div className="section-title">Architecture</div>
          <p className="arch-desc">{a.architecture.description}</p>
          {a.architecture.layers?.length > 0 && (
            <div className="arch-layers">
              {a.architecture.layers.map((layer, i) => (
                <div key={i}>
                  <div className="arch-layer">{layer}</div>
                  {i < a.architecture.layers.length - 1 && <div className="arch-arrow">↓</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Setup Guide */}
      {a.setup_guide?.length > 0 && (
        <div className="section">
          <div className="section-title">Setup Guide</div>
          <ol className="steps">
            {a.setup_guide.map((step, i) => (
              <li key={i}>{step.replace(/^Step \d+:\s*/i, '')}</li>
            ))}
          </ol>
        </div>
      )}

      {/* Starter Tasks */}
      {a.starter_tasks?.length > 0 && (
        <div className="section">
          <div className="section-title">Starter Tasks</div>
          {a.starter_tasks.map((task, i) => (
            <div key={i} className="task-card">
              <div className="task-title">Task {i + 1}: {task.title}</div>
              <div className="task-desc">{task.description}</div>
              {task.file_hint && <div className="task-hint">→ {task.file_hint}</div>}
            </div>
          ))}
        </div>
      )}

      {a.error && (
        <div className="section" style={{ borderColor: '#f85149' }}>
          <div className="section-title" style={{ color: '#f85149' }}>AI Error</div>
          <p style={{ color: 'var(--muted)' }}>{a.error}</p>
          {a.raw_response && <pre style={{ marginTop: 8, fontSize: '0.8rem', color: 'var(--muted)' }}>{a.raw_response}</pre>}
        </div>
      )}
    </div>
  )
}
