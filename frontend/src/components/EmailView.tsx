import { useState, useEffect } from 'react'
import DOMPurify from 'dompurify'
import type { EmailDetail } from '../types'
import { readEmail, markRead, markUnread, archiveEmail, deleteEmail, ApiError } from '../api'

function relativeDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit',
    })
  } catch { return dateStr }
}

interface Props {
  messageId: string
  writeMode: boolean
  onDeleted: () => void
  onArchived: () => void
  onToast: (msg: string, type: 'success' | 'error') => void
}

export default function EmailView({ messageId, writeMode, onDeleted, onArchived, onToast }: Props) {
  const [email, setEmail] = useState<EmailDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    readEmail(messageId)
      .then(data => { if (!cancelled) { setEmail(data); setLoading(false) } })
      .catch(err => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.detail : 'Failed to load email')
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [messageId])

  async function handleAction(action: 'read' | 'unread' | 'archive' | 'delete') {
    if (!email) return
    try {
      if (action === 'read') { await markRead(email.id); onToast('Marked as read', 'success') }
      if (action === 'unread') { await markUnread(email.id); onToast('Marked as unread', 'success') }
      if (action === 'archive') { await archiveEmail(email.id); onArchived(); onToast('Archived', 'success') }
      if (action === 'delete') { await deleteEmail(email.id); onDeleted(); onToast('Moved to trash', 'success') }
    } catch (err: unknown) {
      onToast((err as Error).message, 'error')
    }
  }

  if (loading) return (
    <div style={{ padding: '32px', maxWidth: '680px' }}>
      <div className="skeleton" style={{ width: '70%', height: '28px', marginBottom: '12px' }} />
      <div className="skeleton" style={{ width: '40%', height: '14px', marginBottom: '24px' }} />
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="skeleton" style={{ width: `${70 + (i % 3) * 10}%`, height: '14px', marginBottom: '10px' }} />
      ))}
    </div>
  )

  if (error) return (
    <div style={{ padding: '32px', color: 'var(--danger)' }}>{error}</div>
  )

  if (!email) return null

  const safeHtml = email.html_body
    ? DOMPurify.sanitize(email.html_body, { USE_PROFILES: { html: true } })
    : null

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '20px 32px 16px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 600, lineHeight: 1.3, flex: 1 }}>
            {email.subject}
          </h2>
          {writeMode && (
            <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
              <ActionBtn title="Mark read" onClick={() => handleAction('read')}>✓</ActionBtn>
              <ActionBtn title="Mark unread" onClick={() => handleAction('unread')}>●</ActionBtn>
              <ActionBtn title="Archive" onClick={() => handleAction('archive')}>⬇</ActionBtn>
              <ActionBtn title="Delete" onClick={() => handleAction('delete')} danger>🗑</ActionBtn>
            </div>
          )}
        </div>
        <div style={{ marginTop: '6px', fontSize: '13px', color: 'var(--text-secondary)' }}>
          <span style={{ fontWeight: 500 }}>{email.from}</span>
          <span style={{ color: 'var(--text-muted)', marginLeft: '12px' }}>{relativeDate(email.date)}</span>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
        {safeHtml ? (
          <div
            className="reading-body"
            dangerouslySetInnerHTML={{ __html: safeHtml }}
          />
        ) : (
          <div className="reading-body" style={{ whiteSpace: 'pre-wrap' }}>
            {email.plain_body}
          </div>
        )}
      </div>
    </div>
  )
}

function ActionBtn({ title, onClick, danger, children }: { title: string; onClick: () => void; danger?: boolean; children: React.ReactNode }) {
  return (
    <button
      title={title}
      onClick={onClick}
      style={{
        padding: '5px 8px',
        fontSize: '13px',
        background: 'var(--bg-secondary)',
        color: danger ? 'var(--danger)' : 'var(--text-secondary)',
        border: '1px solid var(--border)',
        borderRadius: '4px',
        transition: 'background 0.1s',
      }}
    >
      {children}
    </button>
  )
}
