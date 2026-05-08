import type { EmailSummary, EmailDetail } from './types'

const BASE = 'http://localhost:8000'

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail)
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, body.detail ?? res.statusText)
  }
  return res.json()
}

export async function listEmails(query = '', maxResults = 30): Promise<EmailSummary[]> {
  const params = new URLSearchParams()
  if (query) params.set('q', query)
  params.set('max_results', String(maxResults))
  const data = await request<{ emails: EmailSummary[] }>(`/emails?${params}`)
  return data.emails
}

export async function readEmail(id: string): Promise<EmailDetail> {
  return request<EmailDetail>(`/emails/${id}`)
}

export async function listNewsletters(hoursBack = 24): Promise<EmailSummary[]> {
  const data = await request<{ emails: EmailSummary[]; total: number }>(
    `/newsletters?hours_back=${hoursBack}`
  )
  return data.emails
}

export async function markRead(id: string): Promise<void> {
  await request(`/emails/${id}/read`, { method: 'PUT' })
}

export async function markUnread(id: string): Promise<void> {
  await request(`/emails/${id}/unread`, { method: 'PUT' })
}

export async function archiveEmail(id: string): Promise<void> {
  await request(`/emails/${id}/archive`, { method: 'POST' })
}

export async function deleteEmail(id: string): Promise<void> {
  await request(`/emails/${id}/delete`, { method: 'POST' })
}

export async function* streamDigest(hoursBack = 24): AsyncGenerator<string> {
  const res = await fetch(`${BASE}/newsletters/digest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hours_back: hoursBack }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, body.detail ?? res.statusText)
  }

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') return
        try {
          const parsed = JSON.parse(data)
          if (parsed.text) yield parsed.text
        } catch {
          // skip malformed SSE lines
        }
      }
    }
  }
}
