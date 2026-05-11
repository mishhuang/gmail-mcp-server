import { useState } from 'react'
import type { View } from '../types'
import { useEmails } from '../hooks/useEmails'
import { archiveEmail, deleteEmail } from '../api'
import EmailRow from './EmailRow'
import DigestButton from './DigestButton'
import Toast from './Toast'

interface Props {
  view: View
  selectedId: string | null
  onSelect: (id: string) => void
  writeMode: boolean
  hoursBack: number
  onShowDigest: () => void
  showDigest: boolean
}

function SkeletonRow() {
  return (
    <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <div className="skeleton" style={{ width: '120px', height: '12px' }} />
        <div className="skeleton" style={{ width: '40px', height: '12px' }} />
      </div>
      <div className="skeleton" style={{ width: '80%', height: '12px', marginBottom: '6px' }} />
      <div className="skeleton" style={{ width: '60%', height: '11px' }} />
    </div>
  )
}

export default function EmailListPane({ view, selectedId, onSelect, writeMode, hoursBack, onShowDigest, showDigest }: Props) {
  const { emails, loading, error, reload } = useEmails(view, hoursBack)
  const [query, setQuery] = useState('')
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  async function handleArchive(id: string) {
    try {
      await archiveEmail(id)
      showToast('Archived', 'success')
      reload()
    } catch (e: unknown) {
      showToast((e as Error).message, 'error')
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteEmail(id)
      showToast('Moved to trash', 'success')
      reload()
    } catch (e: unknown) {
      showToast((e as Error).message, 'error')
    }
  }

  const filtered = query
    ? emails.filter(e =>
        e.subject.toLowerCase().includes(query.toLowerCase()) ||
        e.from.toLowerCase().includes(query.toLowerCase())
      )
    : emails

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      {view === 'newsletters' && (
        <div style={{ padding: '12px', borderBottom: '1px solid var(--border)' }}>
          <DigestButton onGenerate={onShowDigest} active={showDigest} />
        </div>
      )}

      {view === 'inbox' && (
        <div style={{ padding: '12px', borderBottom: '1px solid var(--border)' }}>
          <input
            type="search"
            placeholder="Search emails…"
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '7px 10px',
              fontSize: '13px',
              background: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              outline: 'none',
            }}
          />
        </div>
      )}

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {loading && Array.from({ length: 8 }).map((_, i) => <SkeletonRow key={i} />)}

        {!loading && error && (
          <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--danger)' }}>
            <p style={{ marginBottom: '8px' }}>{error}</p>
            <button onClick={reload} style={{ color: 'var(--accent)', textDecoration: 'underline', fontSize: '13px' }}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div style={{ padding: '40px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <p style={{ marginBottom: '4px' }}>No emails found</p>
            {view === 'newsletters' && (
              <p style={{ fontSize: '12px' }}>Try expanding the time window in Settings</p>
            )}
          </div>
        )}

        {!loading && filtered.map(email => (
          <EmailRow
            key={email.id}
            email={email}
            selected={email.id === selectedId}
            unread={email.labels?.includes('UNREAD') ?? false}
            onClick={() => onSelect(email.id)}
            writeMode={writeMode}
            onArchive={writeMode ? handleArchive : undefined}
            onDelete={writeMode ? handleDelete : undefined}
          />
        ))}
      </div>

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  )
}
