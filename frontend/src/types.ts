export interface EmailSummary {
  id: string
  subject: string
  from: string
  date: string
  snippet: string
  labels?: string[]
}

export interface EmailDetail extends EmailSummary {
  thread_id: string
  to: string
  plain_body: string
  html_body: string
}

export type View = 'inbox' | 'newsletters'
