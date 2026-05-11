import type { EmailSummary } from '../types'

function relativeDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffH = diffMs / 3600000
    if (diffH < 1) return `${Math.round(diffMs / 60000)}m ago`
    if (diffH < 24) return `${Math.round(diffH)}h ago`
    if (diffH < 48) return 'Yesterday'
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function senderName(from: string): string {
  const match = from.match(/^([^<]+)</)
  return match ? match[1].trim() : from.split('@')[0]
}

interface Props {
  email: EmailSummary
  selected: boolean
  unread: boolean
  onClick: () => void
  writeMode: boolean
  onArchive?: (id: string) => void
  onDelete?: (id: string) => void
}

export default function EmailRow({ email, selected, unread, onClick, writeMode, onArchive, onDelete }: Props) {
  return (
    <div
      onClick={onClick}
      className="email-row"
      data-selected={selected}
      data-unread={unread}
      style={{
        padding: '12px 16px',
        cursor: 'pointer',
        borderBottom: '1px solid var(--border)',
        background: selected ? 'var(--accent-light)' : 'transparent',
        borderLeft: unread ? '3px solid var(--unread-bar)' : '3px solid transparent',
        position: 'relative',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '2px' }}>
        <span style={{ fontWeight: unread ? 600 : 400, fontSize: '13px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '180px' }}>
          {senderName(email.from)}
        </span>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)', flexShrink: 0, marginLeft: '8px' }}>
          {relativeDate(email.date)}
        </span>
      </div>
      <div style={{ fontSize: '13px', fontWeight: unread ? 500 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginBottom: '2px' }}>
        {email.subject}
      </div>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {email.snippet}
      </div>

      {writeMode && (
        <div className="row-actions" style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', display: 'none', gap: '4px' }}>
          {onArchive && (
            <button
              title="Archive"
              onClick={e => { e.stopPropagation(); onArchive(email.id) }}
              style={{ padding: '4px 6px', fontSize: '12px', background: 'var(--bg-hover)', borderRadius: '4px' }}
            >
              ⬇
            </button>
          )}
          {onDelete && (
            <button
              title="Delete"
              onClick={e => { e.stopPropagation(); onDelete(email.id) }}
              style={{ padding: '4px 6px', fontSize: '12px', background: 'var(--bg-hover)', borderRadius: '4px', color: 'var(--danger)' }}
            >
              🗑
            </button>
          )}
        </div>
      )}
    </div>
  )
}
