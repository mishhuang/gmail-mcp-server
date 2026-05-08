import type { View } from '../types'

interface Props {
  view: View
  onViewChange: (v: View) => void
  theme: 'light' | 'dark'
  onThemeToggle: () => void
  writeMode: boolean
  onWriteModeToggle: () => void
  hoursBack: number
  onHoursBackChange: (h: number) => void
}

export default function Sidebar({
  view,
  onViewChange,
  theme,
  onThemeToggle,
  writeMode,
  onWriteModeToggle,
  hoursBack,
  onHoursBackChange,
}: Props) {
  return (
    <nav style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '16px 0' }}>
      <div style={{ padding: '0 16px 16px', borderBottom: '1px solid var(--border)' }}>
        <h1 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
          Gmail Reader
        </h1>
      </div>

      <div style={{ flex: 1, padding: '8px 0' }}>
        {(['inbox', 'newsletters'] as View[]).map(v => (
          <button
            key={v}
            onClick={() => onViewChange(v)}
            style={{
              display: 'block',
              width: '100%',
              textAlign: 'left',
              padding: '8px 16px',
              fontSize: '14px',
              fontWeight: view === v ? 600 : 400,
              color: view === v ? 'var(--accent)' : 'var(--text-secondary)',
              background: 'none',
              borderLeft: view === v ? '2px solid var(--accent)' : '2px solid transparent',
              transition: 'color 0.15s, border-color 0.15s',
            }}
            onMouseEnter={e => { if (view !== v) (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)' }}
            onMouseLeave={e => { if (view !== v) (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)' }}
          >
            {v === 'inbox' ? '📥 Inbox' : '📰 Newsletters'}
          </button>
        ))}
      </div>

      <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
        <p style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '10px' }}>
          Settings
        </p>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', cursor: 'pointer' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Dark mode</span>
          <input type="checkbox" checked={theme === 'dark'} onChange={onThemeToggle} />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', cursor: 'pointer' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Write mode</span>
          <input type="checkbox" checked={writeMode} onChange={onWriteModeToggle} />
        </label>

        <div style={{ marginTop: '8px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
            Newsletter window
          </span>
          <select
            value={hoursBack}
            onChange={e => onHoursBackChange(Number(e.target.value))}
            style={{
              width: '100%',
              padding: '4px 8px',
              fontSize: '13px',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border)',
              borderRadius: '4px',
            }}
          >
            {[12, 24, 36, 48].map(h => (
              <option key={h} value={h}>{h}h</option>
            ))}
          </select>
        </div>
      </div>
    </nav>
  )
}
