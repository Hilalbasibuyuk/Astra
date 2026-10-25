
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronDown,
  Clock3,
  RefreshCw,
  Search,
  ShieldAlert,
  X,
} from 'lucide-react'

const API = '/api/v1'

type EventSeverity = 'low' | 'medium' | 'high' | 'critical'
type EventStatus = 'open' | 'resolved'
type StatusFilter = 'all' | EventStatus
type SeverityFilter = 'all' | EventSeverity

type AstraEvent = {
  id: number
  source_type: string
  source_id: string
  event_type: string
  severity: EventSeverity
  status: EventStatus
  summary: string
  details: Record<string, unknown>
  first_seen: string
  last_seen: string
  occurrence_count: number
  resolved_at: string | null
  created_at: string
}

async function requestJSON<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const body = await response.text()
    throw new Error(`${response.status}: ${body || response.statusText}`)
  }

  return response.json() as Promise<T>
}

function formatDate(value?: string | null): string {
  if (!value) return '—'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function humanize(value: string): string {
  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

function SeverityBadge({ severity }: { severity: EventSeverity }) {
  return (
    <span className={`event-severity severity-${severity}`}>
      <span className="event-severity-dot" />
      {humanize(severity)}
    </span>
  )
}

function EventStatusBadge({ status }: { status: EventStatus }) {
  return (
    <span className={`event-status event-status-${status}`}>
      {status === 'open' ? (
        <AlertCircle size={12} />
      ) : (
        <CheckCircle2 size={12} />
      )}
      {humanize(status)}
    </span>
  )
}

function SummaryCard({
  label,
  value,
  description,
  icon: Icon,
  tone,
}: {
  label: string
  value: number
  description: string
  icon: typeof AlertCircle
  tone: 'blue' | 'red' | 'orange' | 'green'
}) {
  return (
    <article className="event-summary-card">
      <div className="event-summary-top">
        <span>{label}</span>
        <span className={`event-summary-icon tone-${tone}`}>
          <Icon size={18} />
        </span>
      </div>
      <strong className="event-summary-value">{value}</strong>
      <span className="event-summary-description">{description}</span>
    </article>
  )
}

export default function EventsPage() {
  const [events, setEvents] = useState<AstraEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('open')
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all')
  const [search, setSearch] = useState('')
  const [selectedEvent, setSelectedEvent] = useState<AstraEvent | null>(null)
  const [resolvingId, setResolvingId] = useState<number | null>(null)
  const [actionError, setActionError] = useState('')
  const [actionSuccess, setActionSuccess] = useState('')

  const loadEvents = useCallback(async (initial = false) => {
    if (initial) setLoading(true)
    else setRefreshing(true)

    setError('')

    try {
      // Load all statuses so the summary cards always reflect the
      // same dataset, regardless of the selected list filter.
      const result = await requestJSON<AstraEvent[]>('/events?limit=1000')
      setEvents(result)
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : 'Failed to load events.',
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    void loadEvents(true)
  }, [loadEvents])

  const summary = useMemo(() => ({
    open: events.filter((event) => event.status === 'open').length,
    critical: events.filter(
      (event) => event.status === 'open' && event.severity === 'critical',
    ).length,
    high: events.filter(
      (event) => event.status === 'open' && event.severity === 'high',
    ).length,
    resolved: events.filter((event) => event.status === 'resolved').length,
  }), [events])

  const filteredEvents = useMemo(() => {
    const query = search.trim().toLowerCase()

    return events.filter((event) => {
      if (statusFilter !== 'all' && event.status !== statusFilter) return false
      if (severityFilter !== 'all' && event.severity !== severityFilter) return false

      if (!query) return true

      return [
        event.summary,
        event.event_type,
        event.source_type,
        event.source_id,
        String(event.id),
      ].some((value) => value.toLowerCase().includes(query))
    })
  }, [events, statusFilter, severityFilter, search])

  const resolveEvent = async (event: AstraEvent) => {
    if (event.status === 'resolved') return

    const confirmed = window.confirm(
      `Resolve event #${event.id}?\n\n${event.summary}`,
    )

    if (!confirmed) return

    setResolvingId(event.id)
    setActionError('')
    setActionSuccess('')

    try {
      const updated = await requestJSON<AstraEvent>(
        `/events/${event.id}/resolve`,
        { method: 'POST' },
      )

      setEvents((current) =>
        current.map((item) => item.id === updated.id ? updated : item),
      )

      setSelectedEvent((current) =>
        current?.id === updated.id ? updated : current,
      )

      setActionSuccess(`Event #${updated.id} was resolved successfully.`)
    } catch (cause) {
      setActionError(
        cause instanceof Error ? cause.message : 'Failed to resolve event.',
      )
    } finally {
      setResolvingId(null)
    }
  }

  return (
    <div className="events-page">
      <div className="events-intro">
        <div>
          <div className="eyebrow">OBSERVATORY / INCIDENT MANAGEMENT</div>
          <h2>Event monitoring</h2>
          <p>
            Review detected anomalies, inspect event details, and manage
            operational incidents.
          </p>
        </div>

        <button
          className="icon-button"
          onClick={() => void loadEvents()}
          disabled={refreshing}
          title="Refresh events"
          aria-label="Refresh events"
        >
          <RefreshCw size={17} className={refreshing ? 'spin' : ''} />
        </button>
      </div>

      <div className="event-summary-grid">
        <SummaryCard
          label="Open events"
          value={summary.open}
          description="Awaiting resolution"
          icon={AlertCircle}
          tone="blue"
        />
        <SummaryCard
          label="Critical events"
          value={summary.critical}
          description="Open critical incidents"
          icon={ShieldAlert}
          tone="red"
        />
        <SummaryCard
          label="High severity"
          value={summary.high}
          description="Open high-priority incidents"
          icon={AlertTriangle}
          tone="orange"
        />
        <SummaryCard
          label="Resolved events"
          value={summary.resolved}
          description="Successfully resolved"
          icon={CheckCircle2}
          tone="green"
        />
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={18} />
          <div>
            <strong>Events could not be loaded</strong>
            <p>{error}</p>
            <button
              className="text-button"
              onClick={() => void loadEvents()}
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {actionError && (
        <div className="error-banner">
          <AlertCircle size={18} />
          <div>
            <strong>Event action failed</strong>
            <p>{actionError}</p>
          </div>
          <button
            className="event-dismiss-button"
            onClick={() => setActionError('')}
            aria-label="Dismiss error"
          >
            <X size={15} />
          </button>
        </div>
      )}

      {actionSuccess && (
        <div className="event-success-banner">
          <CheckCircle2 size={17} />
          <span>{actionSuccess}</span>
          <button
            className="event-dismiss-button"
            onClick={() => setActionSuccess('')}
            aria-label="Dismiss message"
          >
            <X size={15} />
          </button>
        </div>
      )}

      <section className="panel events-list-panel">
        <div className="panel-header events-list-heading">
          <div>
            <h3>Detected events</h3>
            <p>Events persisted by the ASTRA event management service.</p>
          </div>
          <span className="table-count">
            {filteredEvents.length} records
          </span>
        </div>

        <div className="event-filters">
          <label className="event-search">
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search summary, device or event ID..."
              aria-label="Search events"
            />
            {search && (
              <button
                type="button"
                className="event-search-clear"
                onClick={() => setSearch('')}
                aria-label="Clear search"
              >
                <X size={14} />
              </button>
            )}
          </label>

          <label className="event-select-wrap">
            <span>Status</span>
            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value as StatusFilter)
              }
            >
              <option value="open">Open</option>
              <option value="resolved">Resolved</option>
              <option value="all">All statuses</option>
            </select>
            <ChevronDown size={14} />
          </label>

          <label className="event-select-wrap">
            <span>Severity</span>
            <select
              value={severityFilter}
              onChange={(event) =>
                setSeverityFilter(event.target.value as SeverityFilter)
              }
            >
              <option value="all">All severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <ChevronDown size={14} />
          </label>
        </div>

        {loading ? (
          <div className="empty-state">
            <RefreshCw size={22} className="spin" />
            <span>Loading events...</span>
          </div>
        ) : error ? (
          <div className="empty-state">
            <AlertCircle size={22} />
            <span>Waiting for the event API to become available.</span>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="empty-state">
            <CheckCircle2 size={22} />
            <span>No events match the current filters.</span>
            <small>
              Try another status, severity, or search term.
            </small>
          </div>
        ) : (
          <div className="table-scroll events-table-scroll">
            <table className="events-table">
              <thead>
                <tr>
                  <th>Event</th>
                  <th>Source</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Occurrences</th>
                  <th>Last seen</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredEvents.map((event) => (
                  <tr key={event.id}>
                    <td className="event-description-cell">
                      <button
                        className="event-title-button"
                        onClick={() => setSelectedEvent(event)}
                      >
                        <strong>{event.summary}</strong>
                        <span>
                          #{event.id} · {humanize(event.event_type)}
                        </span>
                      </button>
                    </td>
                    <td>
                      <div className="event-source">
                        <strong>{event.source_id}</strong>
                        <span>{humanize(event.source_type)}</span>
                      </div>
                    </td>
                    <td><SeverityBadge severity={event.severity} /></td>
                    <td><EventStatusBadge status={event.status} /></td>
                    <td className="event-occurrences">
                      {event.occurrence_count}
                    </td>
                    <td className="event-time-cell">
                      <Clock3 size={13} />
                      {formatDate(event.last_seen)}
                    </td>
                    <td>
                      <div className="event-actions">
                        <button
                          className="event-detail-button"
                          onClick={() => setSelectedEvent(event)}
                        >
                          Details
                        </button>
                        {event.status === 'open' && (
                          <button
                            className="event-resolve-button"
                            onClick={() => void resolveEvent(event)}
                            disabled={resolvingId === event.id}
                          >
                            {resolvingId === event.id ? (
                              <RefreshCw size={13} className="spin" />
                            ) : (
                              <Check size={13} />
                            )}
                            Resolve
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedEvent && (
        <div
          className="event-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setSelectedEvent(null)
          }}
        >
          <section
            className="event-detail-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="event-detail-title"
          >
            <div className="event-modal-header">
              <div>
                <div className="eyebrow">EVENT #{selectedEvent.id}</div>
                <h3 id="event-detail-title">Event details</h3>
              </div>
              <button
                className="event-dismiss-button"
                onClick={() => setSelectedEvent(null)}
                aria-label="Close event details"
              >
                <X size={18} />
              </button>
            </div>

            <h4 className="event-modal-summary">{selectedEvent.summary}</h4>

            <div className="event-modal-badges">
              <SeverityBadge severity={selectedEvent.severity} />
              <EventStatusBadge status={selectedEvent.status} />
            </div>

            <div className="event-detail-grid">
              <div><span>Source type</span><strong>{selectedEvent.source_type}</strong></div>
              <div><span>Source ID</span><strong>{selectedEvent.source_id}</strong></div>
              <div><span>Event type</span><strong>{humanize(selectedEvent.event_type)}</strong></div>
              <div><span>Occurrences</span><strong>{selectedEvent.occurrence_count}</strong></div>
              <div><span>First seen</span><strong>{formatDate(selectedEvent.first_seen)}</strong></div>
              <div><span>Last seen</span><strong>{formatDate(selectedEvent.last_seen)}</strong></div>
              <div><span>Created at</span><strong>{formatDate(selectedEvent.created_at)}</strong></div>
              <div><span>Resolved at</span><strong>{formatDate(selectedEvent.resolved_at)}</strong></div>
            </div>

            <div className="event-details-json">
              <div className="event-json-heading">Event payload</div>
              <pre>{JSON.stringify(selectedEvent.details, null, 2)}</pre>
            </div>

            <div className="event-modal-footer">
              <button
                className="event-detail-button"
                onClick={() => setSelectedEvent(null)}
              >
                Close
              </button>
              {selectedEvent.status === 'open' && (
                <button
                  className="event-resolve-button"
                  onClick={() => void resolveEvent(selectedEvent)}
                  disabled={resolvingId === selectedEvent.id}
                >
                  <Check size={14} />
                  Resolve event
                </button>
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
