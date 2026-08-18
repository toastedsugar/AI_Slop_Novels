import { useState } from 'react'
import './App.css'

const PAGES = {
  home: 'Home',
  novels: 'Novels',
  pipeline: 'Pipeline',
  settings: 'Settings',
} as const

type PageId = keyof typeof PAGES

function App() {
  const [count, setCount] = useState(0)
  const [page, setPage] = useState<PageId>('home')

  return (
    <div className="window" id="app-window">
      <div className="title-bar">
        <div className="title-bar-text">AI Slop Novels</div>
        <div className="title-bar-controls">
          <button aria-label="Minimize"></button>
          <button aria-label="Maximize"></button>
          <button aria-label="Close"></button>
        </div>
      </div>

      <div className="window-body app-body">
        <ul className="tree-view app-nav">
          {(Object.keys(PAGES) as PageId[]).map((id) => (
            <li key={id}>
              <a
                href={`#${id}`}
                className={id === page ? 'active' : undefined}
                onClick={(e) => {
                  e.preventDefault()
                  setPage(id)
                }}
              >
                {PAGES[id]}
              </a>
            </li>
          ))}
        </ul>

        <div className="app-content">
          {page === 'home' && (
            <>
              <p>Edit <code>src/App.tsx</code> and save to test HMR.</p>
              <button type="button" onClick={() => setCount((count) => count + 1)}>
                Count is {count}
              </button>
            </>
          )}

          {page === 'novels' && <p>Novel list goes here.</p>}
          {page === 'pipeline' && <p>Pipeline status goes here.</p>}
          {page === 'settings' && <p>Settings go here.</p>}
        </div>
      </div>

      <div className="status-bar">
        <p className="status-bar-field">Ready</p>
        <p className="status-bar-field">CPU Usage: 67%</p>
      </div>
    </div>
  )
}

export default App
