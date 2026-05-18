interface Props {
  type: 'server-offline' | 'auth-error'
}

export default function ErrorBanner({ type }: Props) {
  if (type === 'server-offline') {
    return (
      <div style={{
        padding: '8px 16px',
        background: '#fef3c7',
        borderBottom: '1px solid #fcd34d',
        fontSize: '13px',
        color: '#92400e',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexShrink: 0,
      }}>
        ⚠️ API server is not running.
        <code style={{ background: '#fde68a', padding: '1px 6px', borderRadius: '3px' }}>
          python api_server.py
        </code>
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '12px',
      color: 'var(--text-secondary)',
    }}>
      <span style={{ fontSize: '40px' }}>🔐</span>
      <p style={{ fontSize: '15px', fontWeight: 500 }}>Gmail authentication required</p>
      <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Run this command, then refresh:</p>
      <code style={{ background: 'var(--bg-secondary)', padding: '8px 16px', borderRadius: '6px', fontSize: '13px' }}>
        python authenticate.py
      </code>
    </div>
  )
}
