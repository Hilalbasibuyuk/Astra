
import { useState, type FormEvent } from 'react'
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  FileText,
  LoaderCircle,
  Send,
  Sparkles,
} from 'lucide-react'

type RAGSource = {
  source_id: string
  score: number
  chunk_id: string
  doc_id: string
  source_path: string
  category: string
  document_title: string
  section_title: string
  chunk_index: number
  content: string
}

type RAGAnswerResponse = {
  query: string
  answer: string
  result_count: number
  sources: RAGSource[]
}

const CATEGORIES = [
  { value: '', label: 'All categories' },
  { value: 'telescope', label: 'Telescope' },
  { value: 'camera', label: 'Camera' },
  { value: 'dome', label: 'Dome' },
  { value: 'weather', label: 'Weather' },
]

const SUGGESTED_QUESTIONS = [
  'What can cause an increase in telescope motor temperature?',
  'How can cloud cover affect image quality?',
  'What should be checked when dome azimuth does not match its target?',
]

function formatScore(score: number) {
  return `${(score * 100).toFixed(1)}%`
}

async function requestAnswer(
  query: string,
  category: string,
): Promise<RAGAnswerResponse> {
  const response = await fetch('/rag/answer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      limit: 5,
      category: category || null,
    }),
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`

    try {
      const body = await response.json()
      const detail = body.detail

      if (typeof detail === 'string') {
        message = detail
      } else if (detail) {
        message = JSON.stringify(detail)
      }
    } catch {
      // Keep the status-based message if the response isn't JSON.
    }

    throw new Error(message)
  }

  return response.json() as Promise<RAGAnswerResponse>
}

export default function RAGPage() {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [result, setResult] = useState<RAGAnswerResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [expandedSources, setExpandedSources] = useState<string[]>([])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedQuery = query.trim()
    if (!trimmedQuery || loading) return

    setLoading(true)
    setError('')
    setResult(null)
    setExpandedSources([])

    try {
      const answer = await requestAnswer(trimmedQuery, category)
      setResult(answer)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'An unexpected error occurred.',
      )
    } finally {
      setLoading(false)
    }
  }

  function useSuggestedQuestion(question: string) {
    setQuery(question)
    setError('')
  }

  function toggleSource(sourceId: string) {
    setExpandedSources((current) =>
      current.includes(sourceId)
        ? current.filter((id) => id !== sourceId)
        : [...current, sourceId],
    )
  }

  return (
    <div className="rag-page">
      <section className="rag-hero">
        <div className="rag-hero-icon">
          <Sparkles size={24} />
        </div>
        <div>
          <div className="eyebrow">KNOWLEDGE &amp; REASONING</div>
          <h2>Ask the observatory knowledge base</h2>
          <p>
            Ask questions about telescope operations, imaging, dome systems,
            and observing conditions. Answers are generated using retrieved
            ASTRA knowledge-base documents.
          </p>
        </div>
      </section>

      <section className="panel rag-query-panel">
        <form onSubmit={handleSubmit}>
          <label className="rag-label" htmlFor="rag-query">
            Your question
          </label>

          <textarea
            id="rag-query"
            className="rag-textarea"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="e.g. What should I investigate if motor temperature and tracking error both increase?"
            rows={4}
            maxLength={2000}
            required
            disabled={loading}
          />

          <div className="rag-form-footer">
            <label className="rag-category-control">
              <span>Knowledge category</span>
              <span className="rag-select-wrap">
                <select
                  value={category}
                  onChange={(event) => setCategory(event.target.value)}
                  disabled={loading}
                  aria-label="Knowledge category"
                >
                  {CATEGORIES.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
                <ChevronDown size={15} />
              </span>
            </label>

            <span className="rag-character-count">
              {query.length}/2000
            </span>

            <button
              className="primary-button rag-submit"
              type="submit"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <LoaderCircle size={17} className="spin" />
              ) : (
                <Send size={16} />
              )}
              {loading ? 'Generating answer...' : 'Ask ASTRA'}
            </button>
          </div>
        </form>
      </section>

      {!result && !error && !loading && (
        <section className="rag-suggestions">
          <div className="rag-subheading">
            <BookOpen size={17} />
            <h3>Try a question</h3>
          </div>
          <div className="rag-suggestion-list">
            {SUGGESTED_QUESTIONS.map((question) => (
              <button
                key={question}
                className="rag-suggestion"
                type="button"
                onClick={() => useSuggestedQuestion(question)}
              >
                <span>{question}</span>
                <Send size={15} />
              </button>
            ))}
          </div>
          <p className="rag-hint">
            Select a suggestion, then submit it to generate an answer.
          </p>
        </section>
      )}

      {loading && (
        <section className="panel rag-loading" role="status" aria-live="polite">
          <LoaderCircle size={22} className="spin" />
          <div>
            <strong>Searching and generating an answer</strong>
            <p>Retrieving relevant documents and consulting the configured LLM.</p>
          </div>
        </section>
      )}

      {error && (
        <section className="error-banner rag-error" role="alert">
          <AlertCircle size={19} />
          <div>
            <strong>Could not generate an answer</strong>
            <p>{error}</p>
            <p className="rag-error-hint">
              Check that the API, Qdrant, and configured Ollama model are
              available, then try again.
            </p>
          </div>
        </section>
      )}

      {result && (
        <div className="rag-results" aria-live="polite">
          <section className="panel rag-answer-panel">
            <div className="rag-result-heading">
              <div className="rag-result-icon">
                <CheckCircle2 size={19} />
              </div>
              <div>
                <div className="eyebrow">GENERATED RESPONSE</div>
                <h3>ASTRA's answer</h3>
              </div>
              <span className="rag-result-count">
                {result.result_count} retrieved
              </span>
            </div>

            <div className="rag-question-summary">
              <span>Your question</span>
              <p>{result.query}</p>
            </div>

            <div className="rag-answer-text">{result.answer}</div>

            <p className="rag-grounding-note">
              <BookOpen size={14} />
              Review the cited source IDs against the source cards below.
              Retrieved context does not by itself establish an operational
              root cause or confirm that an action is safe.
            </p>
          </section>

          <section className="rag-sources-section">
            <div className="rag-sources-heading">
              <div>
                <div className="eyebrow">RETRIEVED KNOWLEDGE</div>
                <h3>Source documents</h3>
                <p>
                  {result.sources.length} source
                  {result.sources.length === 1 ? '' : 's'} returned by retrieval.
                </p>
              </div>
              <BookOpen size={20} />
            </div>

            {result.sources.length === 0 ? (
              <div className="panel rag-no-sources">
                No source documents were returned for this question.
              </div>
            ) : (
              <div className="rag-source-list">
                {result.sources.map((source) => {
                  const expanded = expandedSources.includes(source.source_id)

                  return (
                    <article
                      className="panel rag-source-card"
                      key={`${source.source_id}-${source.chunk_id}`}
                    >
                      <button
                        type="button"
                        className="rag-source-toggle"
                        onClick={() => toggleSource(source.source_id)}
                        aria-expanded={expanded}
                      >
                        <span className="rag-source-file-icon">
                          <FileText size={18} />
                        </span>

                        <span className="rag-source-main">
                          <strong>{source.document_title}</strong>
                          <span>{source.section_title}</span>
                          <span className="rag-source-path">
                            {source.source_path}
                          </span>
                        </span>

                        <span className="rag-source-meta">
                          <span className="rag-category-tag">
                            {source.category}
                          </span>
                          <span className="rag-score">
                            Score {formatScore(source.score)}
                          </span>
                          <ChevronDown
                            size={17}
                            className={expanded ? 'rag-chevron expanded' : 'rag-chevron'}
                          />
                        </span>
                      </button>

                      {expanded && (
                        <div className="rag-source-details">
                          <div className="rag-source-id">
                            <span>Reference</span>
                            <strong>[{source.source_id}]</strong>
                          </div>
                          <p>{source.content}</p>
                          <div className="rag-source-footer">
                            <span>Document ID: {source.doc_id}</span>
                            <span>Chunk: {source.chunk_index}</span>
                          </div>
                        </div>
                      )}
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  )
}
