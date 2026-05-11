interface Props { message: string; type: 'success' | 'error' }
export default function Toast({ message, type }: Props) {
  return (
    <div style={{
      position: 'absolute',
      bottom: '16px',
      left: '50%',
      transform: 'translateX(-50%)',
      padding: '8px 16px',
      background: type === 'error' ? 'var(--danger)' : '#2d6a4f',
      color: '#fff',
      borderRadius: '6px',
      fontSize: '13px',
      fontWeight: 500,
      whiteSpace: 'nowrap',
      zIndex: 10,
    }}>
      {message}
    </div>
  )
}
