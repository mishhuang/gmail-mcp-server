import type { ReactNode } from 'react'

interface Props {
  sidebar: ReactNode
  list: ReactNode
  reader: ReactNode
}

export default function Layout({ sidebar, list, reader }: Props) {
  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      overflow: 'hidden',
    }}>
      <div style={{
        width: 'var(--sidebar-width)',
        flexShrink: 0,
        borderRight: '1px solid var(--border)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}>
        {sidebar}
      </div>
      <div style={{
        width: 'var(--list-width)',
        flexShrink: 0,
        borderRight: '1px solid var(--border)',
        background: 'var(--bg-primary)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}>
        {list}
      </div>
      <div style={{
        flex: 1,
        background: 'var(--bg-card)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {reader}
      </div>
    </div>
  )
}
