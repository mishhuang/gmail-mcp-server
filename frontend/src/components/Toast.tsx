import { useEffect, useState } from 'react'

interface Props {
  message: string
  type: 'success' | 'error'
}

export default function Toast({ message, type }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true))
  }, [])

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '24px',
        left: '50%',
        transform: `translateX(-50%) translateY(${visible ? '0' : '8px'})`,
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.2s, transform 0.2s',
        padding: '10px 20px',
        background: type === 'error' ? '#c0392b' : '#2d6a4f',
        color: '#fff',
        borderRadius: '8px',
        fontSize: '13px',
        fontWeight: 500,
        boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
        whiteSpace: 'nowrap',
        zIndex: 100,
        pointerEvents: 'none',
      }}
    >
      {message}
    </div>
  )
}
