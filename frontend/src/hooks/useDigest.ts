import { useState, useEffect, useRef } from 'react'
import { streamDigest, ApiError } from '../api'

interface UseDigestResult {
  text: string
  generating: boolean
  error: string | null
  done: boolean
}

export function useDigest(active: boolean, hoursBack: number): UseDigestResult {
  const [text, setText] = useState('')
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [done, setDone] = useState(false)
  const abortRef = useRef(false)

  useEffect(() => {
    if (!active) return
    abortRef.current = false
    setText('')
    setDone(false)
    setError(null)
    setGenerating(true)

    ;(async () => {
      try {
        for await (const chunk of streamDigest(hoursBack)) {
          if (abortRef.current) break
          setText(prev => prev + chunk)
        }
        if (!abortRef.current) setDone(true)
      } catch (err) {
        if (!abortRef.current) {
          setError(err instanceof ApiError ? err.detail : 'Digest generation failed')
        }
      } finally {
        setGenerating(false)
      }
    })()

    return () => { abortRef.current = true }
  }, [active, hoursBack])

  return { text, generating, error, done }
}
