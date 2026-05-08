interface Props {
  selectedId: string | null
  showDigest: boolean
  writeMode: boolean
  hoursBack: number
  onDeleted: () => void
  onArchived: () => void
}

export default function ReaderPane({ selectedId, showDigest }: Props) {
  if (!selectedId && !showDigest) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '14px' }}>
        Select an email to read
      </div>
    )
  }
  return <div style={{ padding: '24px' }}>Loading…</div>
}
