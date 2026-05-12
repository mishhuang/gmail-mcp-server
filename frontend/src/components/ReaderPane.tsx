import { useState } from 'react'
import EmailView from './EmailView'
import DigestView from './DigestView'
import Toast from './Toast'

interface Props {
  selectedId: string | null
  showDigest: boolean
  writeMode: boolean
  hoursBack: number
  onDeleted: () => void
  onArchived: () => void
}

export default function ReaderPane({ selectedId, showDigest, writeMode, hoursBack, onDeleted, onArchived }: Props) {
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <div style={{ height: '100%', position: 'relative' }}>
      {showDigest ? (
        <DigestView hoursBack={hoursBack} />
      ) : selectedId ? (
        <EmailView
          messageId={selectedId}
          writeMode={writeMode}
          onDeleted={onDeleted}
          onArchived={onArchived}
          onToast={showToast}
        />
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', flexDirection: 'column', gap: '8px' }}>
          <span style={{ fontSize: '32px' }}>✉️</span>
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Select an email to read</span>
        </div>
      )}

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  )
}
