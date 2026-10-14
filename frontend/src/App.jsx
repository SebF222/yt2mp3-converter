import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    if (!url.trim()) {
      setMessage('Please paste a video URL first.')
      return
    }

    setIsLoading(true)
    setMessage('Converting your audio... Please wait.')

    try {
      const response = await fetch('https://yt2mp3-converter-1.onrender.com/api/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Conversion failed.')
      }

      const audioBlob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(audioBlob)
      const link = document.createElement('a')

      link.href = downloadUrl
      link.download = 'converted-audio.mp3'
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(downloadUrl)

      setMessage('Success! Your MP3 download has started.')
    } catch (error) {
      setMessage(
        error.message ||
          'Could not connect to the converter. Make sure the Flask backend is running.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app">
      <nav className="navbar">
        <a className="brand" href="/">
          <span className="brand-icon">♫</span>
          YT2MP3
        </a>
        <span className="nav-label">Free Audio Converter</span>
      </nav>

      <section className="converter">
        <div className="music-icon">♫</div>
        <p className="eyebrow">SIMPLE. FAST. EASY.</p>

        <h1>
          Turn videos into <span>MP3 audio.</span>
        </h1>

        <p className="description">
          Paste a video URL below to convert supported videos into MP3 audio.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="video-url">Video URL</label>

          <div className="input-group">
            <input
              id="video-url"
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(event) => {
                setUrl(event.target.value)
                setMessage('')
              }}
              required
            />

            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Converting...' : 'Convert to MP3 →'}
            </button>
          </div>
        </form>

        {message && (
          <p className="status-message" role="status">
            {message}
          </p>
        )}

        <div className="features">
          <span>✓ Simple to use</span>
          <span>✓ MP3 audio</span>
          <span>✓ Free to try</span>
        </div>
      </section>

      <footer>
        <p>YT2MP3 Converter · Built with React and Flask</p>
      </footer>
    </main>
  )
}

export default App