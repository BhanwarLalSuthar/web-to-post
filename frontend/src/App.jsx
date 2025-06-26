import React, { useState } from 'react';
import api from './api';

function App() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState('');
  const [drafts, setDrafts] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');

    try {
      const res = await api.post('/generate', { prompt });
      setSummary(res.data.summary);
      setDrafts(res.data.drafts);
    } catch (err) {
      console.error(err);
      setError('Failed to generate content.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Social Media Post Generator</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your topic or prompt"
          style={{ width: '100%', padding: '0.5rem', fontSize: '1rem' }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: '0.5rem', padding: '0.5rem 1rem' }}>
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {loading && <p>Loading...</p>}

      {summary && (
        <div>
          <h2>Summary</h2>
          <p>{summary}</p>
        </div>
      )}

      {drafts && (
        <div>
          <h2>Drafts</h2>
          <h3>LinkedIn</h3>
          <p>{drafts.LinkedIn}</p>
          <h3>Twitter</h3>
          <p>{drafts.Twitter}</p>
          <h3>Instagram</h3>
          <p>{drafts.Instagram}</p>
        </div>
      )}
    </div>
  );
}

export default App;