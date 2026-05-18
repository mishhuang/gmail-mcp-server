import { useState, useEffect } from 'react'
import type { EmailSummary, View } from '../types'
import { listEmails, listNewsletters, ApiError } from '../api'

interface UseEmailsResult {
  emails: EmailSummary[]
  loading: boolean
  error: string | null
  reload: () => void
}

export function useEmails(view: View, hoursBack: number, onAuthError?: () => void): UseEmailsResult {
  const [emails, setEmails] = useState<EmailSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const fetch = view === 'inbox'
      ? listEmails()
      : listNewsletters(hoursBack)

    fetch
      .then(data => { if (!cancelled) { setEmails(data); setLoading(false) } })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 503) onAuthError?.()
        setError(err instanceof ApiError ? err.detail : 'Failed to load emails')
        setLoading(false)
      })

    return () => { cancelled = true }
  }, [view, hoursBack, tick])

  return { emails, loading, error, reload: () => setTick(t => t + 1) }
}
