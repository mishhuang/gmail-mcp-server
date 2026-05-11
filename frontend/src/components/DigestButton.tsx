interface Props { onGenerate: () => void; active: boolean }
export default function DigestButton({ onGenerate, active }: Props) {
  return (
    <button
      onClick={onGenerate}
      style={{
        width: '100%',
        padding: '9px 12px',
        fontSize: '13px',
        fontWeight: 600,
        background: active ? 'var(--accent)' : 'var(--accent-light)',
        color: active ? '#fff' : 'var(--accent)',
        border: `1px solid ${active ? 'var(--accent)' : 'var(--border)'}`,
        borderRadius: '6px',
        transition: 'all 0.15s',
      }}
    >
      ✨ Generate Digest
    </button>
  )
}
