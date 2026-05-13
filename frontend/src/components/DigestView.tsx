interface Props { hoursBack: number; onDone?: () => void }
export default function DigestView({ hoursBack }: Props) {
  return <div style={{ padding: '32px', color: 'var(--text-muted)' }}>Digest for last {hoursBack}h — coming soon</div>
}
