import { describe, it, expect, vi, beforeEach } from 'vitest'
import { listEmails, readEmail, listNewsletters, markRead, ApiError } from './api'

const mockFetch = vi.fn()
global.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockReset()
})

describe('listEmails', () => {
  it('returns emails array on success', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ emails: [{ id: '1', subject: 'Test' }] }),
    })
    const result = await listEmails()
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('1')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/emails'),
      undefined
    )
  })

  it('throws ApiError on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 503,
      json: async () => ({ detail: 'Auth failed' }),
    })
    await expect(listEmails()).rejects.toBeInstanceOf(ApiError)
  })
})

describe('readEmail', () => {
  it('returns full email detail', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'abc', subject: 'S', plain_body: 'B' }),
    })
    const result = await readEmail('abc')
    expect(result.id).toBe('abc')
  })
})

describe('markRead', () => {
  it('calls PUT /emails/{id}/read', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    })
    await markRead('abc')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/emails/abc/read'),
      expect.objectContaining({ method: 'PUT' })
    )
  })
})
