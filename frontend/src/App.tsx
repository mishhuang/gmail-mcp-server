import { useState, useEffect } from 'react'
import type { View } from './types'
import Layout from './components/Layout'
import Sidebar from './components/Sidebar'
import EmailListPane from './components/EmailListPane'
import ReaderPane from './components/ReaderPane'
import ErrorBanner from './components/ErrorBanner'

function getInitialTheme(): 'light' | 'dark' {
  return (localStorage.getItem('theme') as 'light' | 'dark') ?? 'light'
}

function getInitialWriteMode(): boolean {
  return localStorage.getItem('writeMode') === 'true'
}

export default function App() {
  const [view, setView] = useState<View>('inbox')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showDigest, setShowDigest] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme)
  const [writeMode, setWriteMode] = useState(getInitialWriteMode)
  const [hoursBack, setHoursBack] = useState(24)
  const [digestGenerating, setDigestGenerating] = useState(false)
  const [serverOnline, setServerOnline] = useState<boolean | null>(null)
  const [authError, setAuthError] = useState(false)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    localStorage.setItem('writeMode', String(writeMode))
  }, [writeMode])

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(r => r.json())
      .then(() => setServerOnline(true))
      .catch(() => setServerOnline(false))
  }, [])

  function handleSelectEmail(id: string) {
    setSelectedId(id)
    setShowDigest(false)
  }

  function handleViewChange(v: View) {
    setView(v)
    setSelectedId(null)
    setShowDigest(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {serverOnline === false && <ErrorBanner type="server-offline" />}
      {authError ? (
        <ErrorBanner type="auth-error" />
      ) : (
        <Layout
          sidebar={
            <Sidebar
              view={view}
              onViewChange={handleViewChange}
              theme={theme}
              onThemeToggle={() => setTheme(t => t === 'light' ? 'dark' : 'light')}
              writeMode={writeMode}
              onWriteModeToggle={() => setWriteMode(w => !w)}
              hoursBack={hoursBack}
              onHoursBackChange={setHoursBack}
            />
          }
          list={
            <EmailListPane
              view={view}
              selectedId={selectedId}
              onSelect={handleSelectEmail}
              writeMode={writeMode}
              hoursBack={hoursBack}
              onShowDigest={() => { setShowDigest(true); setDigestGenerating(true) }}
              showDigest={showDigest}
              digestGenerating={digestGenerating}
              onAuthError={() => setAuthError(true)}
            />
          }
          reader={
            <ReaderPane
              selectedId={selectedId}
              showDigest={showDigest}
              writeMode={writeMode}
              hoursBack={hoursBack}
              onDeleted={() => setSelectedId(null)}
              onArchived={() => setSelectedId(null)}
              onDigestDone={() => setDigestGenerating(false)}
            />
          }
        />
      )}
    </div>
  )
}
