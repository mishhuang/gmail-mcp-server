import { useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { useDigest } from '../hooks/useDigest'

interface Props {
  hoursBack: number
  onDone?: () => void
}

export default function DigestView({ hoursBack, onDone }: Props) {
  const { text, generating, error, done } = useDigest(true, hoursBack)

  useEffect(() => {
    if (done) onDone?.()
  }, [done, onDone])

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '20px 32px 16px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
        <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Newsletter Digest</h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
          {generating
            ? `Generating from the last ${hoursBack}h of newsletters…`
            : done
            ? `Generated · last ${hoursBack}h`
            : ''}
        </p>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
        {error && (
          <div style={{
            padding: '16px',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            color: 'var(--danger)',
            marginBottom: '16px',
            fontSize: '13px',
          }}>
            {error}
          </div>
        )}

        {text && (
          <div className="reading-body">
            <ReactMarkdown>{text}</ReactMarkdown>
          </div>
        )}

        {generating && !text && (
          <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
            <span style={{ animation: 'blink 1s step-end infinite' }}>▋</span>
          </div>
        )}

        {generating && text && (
          <span style={{
            display: 'inline-block',
            width: '2px',
            height: '18px',
            background: 'var(--text-primary)',
            verticalAlign: 'text-bottom',
            marginLeft: '2px',
            animation: 'blink 1s step-end infinite',
          }} />
        )}
      </div>
    </div>
  )
}
