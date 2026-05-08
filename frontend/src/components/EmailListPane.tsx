import type { View } from '../types'

interface Props {
  view: View
  selectedId: string | null
  onSelect: (id: string) => void
  writeMode: boolean
  hoursBack: number
  onShowDigest: () => void
  showDigest: boolean
}

export default function EmailListPane(_props: Props) {
  return (
    <div style={{ padding: '24px 16px', color: 'var(--text-muted)', fontSize: '14px' }}>
      Loading…
    </div>
  )
}
