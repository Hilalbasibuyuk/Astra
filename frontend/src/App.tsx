
import { useCallback, useEffect, useState } from 'react'
import {
  Activity,
  AlertCircle,
  BrainCircuit,
  BookOpen,
  Camera,
  CheckCircle2,
  ChevronRight,
  CloudSun,
  Compass,
  Gauge,
  LayoutDashboard,
  LoaderCircle,
  RefreshCw,
  Telescope,
  Wind,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'
import EventsPage from './EventsPage'
import RAGPage from './RAGPage'

const API = '/api/v1'
const TELESCOPE_ID = 'TCS-01'
const CAMERA_ID = 'CCD-01'
const WEATHER_ID = 'WX-01'
const DOME_ID = 'DOME-01'

type TelescopeTelemetry = {
  timestamp: string
  telescope_id: string
  azimuth: number
  elevation: number
  right_ascension: number
  declination: number
  tracking_error: number
  motor_temperature: number
  motor_current: number
  vibration: number
  status: string
}

type CameraTelemetry = {
  timestamp: string
  camera_id: string
  sensor_temperature: number
  exposure_time: number
  gain: number
  frame_rate: number
  image_quality: number
  status: string
}

type WeatherTelemetry = {
  timestamp: string
  station_id: string
  temperature: number
  humidity: number
  pressure: number
  wind_speed: number
  seeing: number
  cloud_cover: number
  status: string
}

type DomeTelemetry = {
  timestamp: string
  dome_id: string
  azimuth: number
  rotation_speed: number
  shutter_open: boolean
  motor_temperature: number
  status: string
}

type HealthResponse = {
  status: string
  service: string
}

type DiagnosticResponse = Record<string, unknown>

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
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

function formatTime(value?: string) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatNumber(value: number | undefined, digits = 2) {
  if (value === undefined || value === null || !Number.isFinite(value)) {
    return '—'
  }
  return value.toFixed(digits)
}

function StatusBadge({ status }: { status?: string }) {
  const normalized = status?.toLowerCase()
  const healthy = normalized === 'ok' || normalized === 'normal' || normalized === 'healthy'
  const known = Boolean(status)

  return (
    <span className={`status-badge ${!known ? 'unknown' : healthy ? 'healthy' : 'warning'}`}>
      <span className="status-dot" />
      {known ? status : 'No data'}
    </span>
  )
}

function MetricCard({
  label,
  value,
  unit,
  icon: Icon,
  status,
  detail,
}: {
  label: string
  value: string
  unit?: string
  icon: typeof Activity
  status?: string
  detail?: string
}) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        <span className="metric-icon"><Icon size={18} /></span>
      </div>
      <div className="metric-value">
        {value}
        {unit && value !== '—' && <span className="metric-unit">{unit}</span>}
      </div>
      <div className="metric-bottom">
        {status ? <StatusBadge status={status} /> : <span className="muted">{detail}</span>}
      </div>
    </article>
  )
}

function SectionTitle({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description: string
}) {
  return (
    <div className="section-title">
      <div className="eyebrow">{eyebrow}</div>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  )
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [telescope, setTelescope] = useState<TelescopeTelemetry | null>(null)
  const [camera, setCamera] = useState<CameraTelemetry | null>(null)
  const [weather, setWeather] = useState<WeatherTelemetry | null>(null)
  const [dome, setDome] = useState<DomeTelemetry | null>(null)
  const [history, setHistory] = useState<TelescopeTelemetry[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [lastRefresh, setLastRefresh] = useState<string>()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [activePage, setActivePage] = useState<
  'overview' | 'telemetry' | 'diagnostics' | 'events' | 'rag'
>('overview')
  const [diagnostic, setDiagnostic] = useState<DiagnosticResponse | null>(null)
  const [diagnosticError, setDiagnosticError] = useState('')
  const [diagnosticLoading, setDiagnosticLoading] = useState(false)

  const refreshData = useCallback(async (initial = false) => {
    if (initial) setLoading(true)
    else setRefreshing(true)

    const jobs = [
      {
        name: 'API health',
        run: () => fetchJSON<HealthResponse>('/health'),
        save: (value: HealthResponse) => setHealth(value),
      },
      {
        name: 'Telescope latest',
        run: () => fetchJSON<TelescopeTelemetry>(`/telemetry/telescope/${TELESCOPE_ID}/latest`),
        save: (value: TelescopeTelemetry) => setTelescope(value),
      },
      {
        name: 'Camera latest',
        run: () => fetchJSON<CameraTelemetry>(`/telemetry/camera/${CAMERA_ID}/latest`),
        save: (value: CameraTelemetry) => setCamera(value),
      },
      {
        name: 'Weather latest',
        run: () => fetchJSON<WeatherTelemetry>(`/telemetry/weather/${WEATHER_ID}/latest`),
        save: (value: WeatherTelemetry) => setWeather(value),
      },
      {
        name: 'Dome latest',
        run: () => fetchJSON<DomeTelemetry>(`/telemetry/dome/${DOME_ID}/latest`),
        save: (value: DomeTelemetry) => setDome(value),
      },
      {
        name: 'Telescope history',
        run: () => fetchJSON<TelescopeTelemetry[]>(
          `/telemetry/telescope/${TELESCOPE_ID}/history?limit=60`,
        ),
        save: (value: TelescopeTelemetry[]) => setHistory([...value].reverse()),
      },
    ] as const

    const results = await Promise.allSettled(
      jobs.map(async (job) => ({
        name: job.name,
        value: await job.run(),
        save: job.save,
      })),
    )

    const nextErrors: string[] = []

    for (let index = 0; index < results.length; index += 1) {
      const result = results[index]

      if (result.status === 'fulfilled') {
        result.value.save(result.value.value as never)
      } else {
        const name = jobs[index].name
        nextErrors.push(`${name}: ${result.reason instanceof Error ? result.reason.message : 'Request failed'}`)

        if (name === 'API health') setHealth(null)
        if (name === 'Telescope latest') setTelescope(null)
        if (name === 'Camera latest') setCamera(null)
        if (name === 'Weather latest') setWeather(null)
        if (name === 'Dome latest') setDome(null)
        if (name === 'Telescope history') setHistory([])
      }
    }

    setErrors(nextErrors)
    setLastRefresh(new Date().toISOString())
    setLoading(false)
    setRefreshing(false)
  }, [])

  useEffect(() => {
    void refreshData(true)
    const timer = window.setInterval(() => void refreshData(), 5000)
    return () => window.clearInterval(timer)
  }, [refreshData])

  const runDiagnostics = async () => {
    setDiagnosticLoading(true)
    setDiagnostic(null)
    setDiagnosticError('')

    try {
      const result = await fetchJSON<DiagnosticResponse>('/diagnostics/analyze', {
        method: 'POST',
        body: JSON.stringify({
          telescope_id: TELESCOPE_ID,
          history_limit: 100,
          rag_limit: 5,
        }),
      })
      setDiagnostic(result)
    } catch (error) {
      setDiagnosticError(error instanceof Error ? error.message : 'Diagnostic request failed')
    } finally {
      setDiagnosticLoading(false)
    }
  }

  const chartData = history.map((item) => ({
    time: formatTime(item.timestamp),
    trackingError: item.tracking_error,
    motorTemperature: item.motor_temperature,
  }))

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Telescope size={23} /></div>
          <div>
            <div className="brand-name">ASTRA</div>
            <div className="brand-caption">OBSERVATORY INTELLIGENCE</div>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav className="navigation">
          <button
            className={`nav-item ${activePage === 'overview' ? 'active' : ''}`}
            onClick={() => setActivePage('overview')}
          >
            <LayoutDashboard size={18} /> Overview
          </button>
          <button
            className={`nav-item ${activePage === 'telemetry' ? 'active' : ''}`}
            onClick={() => setActivePage('telemetry')}
          >
            <Activity size={18} /> Telemetry
          </button>
          <button
            className={`nav-item ${activePage === 'diagnostics' ? 'active' : ''}`}
            onClick={() => setActivePage('diagnostics')}
          >
            <BrainCircuit size={18} /> AI Diagnostics
          </button>
          <button
              className={`nav-item ${activePage === 'events' ? 'active' : ''}`}
              onClick={() => setActivePage('events')}
            >
              <AlertCircle size={18} /> Events
          </button>
          <button
            className={`nav-item ${activePage === 'rag' ? 'active' : ''}`}
            onClick={() => setActivePage('rag')}
          >
            <BookOpen size={18} /> Knowledge Assistant
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="environment-card">
            <span className="environment-indicator" />
            <div>
              <strong>Simulation environment</strong>
              <span>Local telemetry pipeline</span>
            </div>
          </div>
          <div className="sidebar-version">ASTRA PLATFORM · v0.1.0</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">ASTRA <ChevronRight size={14} /> CONTROL CENTER</div>
          <div className="topbar-right">
            <div className="live-indicator">
              <span className="live-dot" />
              {health?.status === 'ok' ? 'API CONNECTED' : 'API UNAVAILABLE'}
            </div>
            <button
              className="icon-button"
              onClick={() => void refreshData()}
              disabled={refreshing}
              title="Refresh telemetry"
              aria-label="Refresh telemetry"
            >
              <RefreshCw size={17} className={refreshing ? 'spin' : ''} />
            </button>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">OBSERVATORY / OPERATIONS</div>
              <h1>
                {activePage === 'overview' && 'Mission overview'}
                {activePage === 'telemetry' && 'Telemetry explorer'}
                {activePage === 'diagnostics' && 'AI diagnostics'}
                {activePage === 'events' && 'Event monitoring'}
                {activePage === 'rag' && 'Knowledge Assistant'}
              </h1>
              <p>
                {activePage === 'overview' && 'Real-time status of your observatory systems.'}
                {activePage === 'telemetry' && 'Live measurements and recent telescope telemetry.'}
                {activePage === 'diagnostics' && 'Run a source-grounded diagnostic analysis for the telescope.'}
                {activePage === 'events' && 'Review detected anomalies and manage operational incidents.'}
                {activePage === 'rag' &&'Ask questions and explore source-grounded observatory knowledge.'}
              </p>
            </div>
            <div className="updated-block">
              <span>LAST DATA REFRESH</span>
              <strong>{formatTime(lastRefresh)}</strong>
              <span className="auto-refresh"><span className="live-dot" /> AUTO-REFRESH · 5 SEC</span>
            </div>
          </div>

          {errors.length > 0 && (
            <div className="error-banner">
              <AlertCircle size={18} />
              <div>
                <strong>Some data could not be loaded</strong>
                <p>{errors.join(' · ')}</p>
              </div>
            </div>
          )}

          {(activePage === 'overview' || activePage === 'telemetry') && (
            <>
              <SectionTitle
                eyebrow="SYSTEM SNAPSHOT"
                title="Systems at a glance"
                description="Latest measurements returned by the ASTRA telemetry API."
              />

              <div className="system-grid">
                <article className="system-card">
                  <div className="system-card-header">
                    <div className="system-icon"><Telescope size={19} /></div>
                    <StatusBadge status={telescope?.status} />
                  </div>
                  <div className="system-name">Telescope</div>
                  <div className="system-id">{TELESCOPE_ID}</div>
                  <div className="system-reading">
                    <span>Tracking error</span>
                    <strong>{formatNumber(telescope?.tracking_error)}<small>°</small></strong>
                  </div>
                  <div className="system-reading">
                    <span>Motor temperature</span>
                    <strong>{formatNumber(telescope?.motor_temperature)}<small>°C</small></strong>
                  </div>
                  <div className="system-card-footer">
                    <span>Updated {formatTime(telescope?.timestamp)}</span>
                    <Compass size={15} />
                  </div>
                </article>

                <article className="system-card">
                  <div className="system-card-header">
                    <div className="system-icon"><Camera size={19} /></div>
                    <StatusBadge status={camera?.status} />
                  </div>
                  <div className="system-name">Imaging camera</div>
                  <div className="system-id">{CAMERA_ID}</div>
                  <div className="system-reading">
                    <span>Frame rate</span>
                    <strong>{formatNumber(camera?.frame_rate)}<small> FPS</small></strong>
                  </div>
                  <div className="system-reading">
                    <span>Sensor temperature</span>
                    <strong>{formatNumber(camera?.sensor_temperature)}<small>°C</small></strong>
                  </div>
                  <div className="system-card-footer">
                    <span>Updated {formatTime(camera?.timestamp)}</span>
                    <Camera size={15} />
                  </div>
                </article>

                <article className="system-card">
                  <div className="system-card-header">
                    <div className="system-icon"><CloudSun size={19} /></div>
                    <StatusBadge status={weather?.status} />
                  </div>
                  <div className="system-name">Weather station</div>
                  <div className="system-id">{WEATHER_ID}</div>
                  <div className="system-reading">
                    <span>Ambient temperature</span>
                    <strong>{formatNumber(weather?.temperature)}<small>°C</small></strong>
                  </div>
                  <div className="system-reading">
                    <span>Cloud cover</span>
                    <strong>{formatNumber(weather?.cloud_cover)}<small>%</small></strong>
                  </div>
                  <div className="system-card-footer">
                    <span>Updated {formatTime(weather?.timestamp)}</span>
                    <Wind size={15} />
                  </div>
                </article>

                <article className="system-card">
                  <div className="system-card-header">
                    <div className="system-icon"><Gauge size={19} /></div>
                    <StatusBadge status={dome?.status} />
                  </div>
                  <div className="system-name">Observatory dome</div>
                  <div className="system-id">{DOME_ID}</div>
                  <div className="system-reading">
                    <span>Dome azimuth</span>
                    <strong>{formatNumber(dome?.azimuth)}<small>°</small></strong>
                  </div>
                  <div className="system-reading">
                    <span>Shutter</span>
                    <strong className="text-reading">
                      {dome ? (dome.shutter_open ? 'Open' : 'Closed') : '—'}
                    </strong>
                  </div>
                  <div className="system-card-footer">
                    <span>Updated {formatTime(dome?.timestamp)}</span>
                    <Gauge size={15} />
                  </div>
                </article>
              </div>

              <div className="content-grid">
                <section className="panel chart-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Telescope tracking</h3>
                      <p>Tracking error over the latest returned observations</p>
                    </div>
                    <span className="chart-unit">DEGREES (°)</span>
                  </div>
                  {loading && history.length === 0 ? (
                    <div className="empty-state"><LoaderCircle className="spin" /> Loading telemetry…</div>
                  ) : chartData.length === 0 ? (
                    <div className="empty-state">
                      <Activity size={22} />
                      <span>No telescope history available.</span>
                      <small>Check that the worker is running and QuestDB contains data.</small>
                    </div>
                  ) : (
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}>
                          <defs>
                            <linearGradient id="trackingGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#78a9ff" stopOpacity={0.28} />
                              <stop offset="95%" stopColor="#78a9ff" stopOpacity={0.01} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid stroke="#263244" strokeDasharray="3 5" vertical={false} />
                          <XAxis
                            dataKey="time"
                            tick={{ fill: '#78869b', fontSize: 11 }}
                            tickLine={false}
                            axisLine={false}
                            minTickGap={28}
                          />
                          <YAxis
                            tick={{ fill: '#78869b', fontSize: 11 }}
                            tickLine={false}
                            axisLine={false}
                            width={48}
                          />
                          <Tooltip
                            contentStyle={{
                              background: '#111a28',
                              border: '1px solid #2a374b',
                              borderRadius: 10,
                              color: '#e5edf8',
                            }}
                            labelStyle={{ color: '#91a0b6' }}
                          />
                          <Area
                            type="monotone"
                            dataKey="trackingError"
                            name="Tracking error"
                            stroke="#78a9ff"
                            strokeWidth={2}
                            fill="url(#trackingGradient)"
                            dot={false}
                            activeDot={{ r: 4, fill: '#78a9ff', stroke: '#111a28', strokeWidth: 2 }}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                  <div className="chart-footer">
                    <span><span className="legend-dot blue" /> Tracking error</span>
                    <span>{history.length} observations</span>
                  </div>
                </section>

                <section className="panel position-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Telescope position</h3>
                      <p>Latest pointing coordinates</p>
                    </div>
                    <Compass size={18} className="panel-icon" />
                  </div>
                  <div className="position-visual">
                    <div className="compass-ring ring-outer" />
                    <div className="compass-ring ring-middle" />
                    <div className="compass-ring ring-inner" />
                    <div className="compass-cross cross-horizontal" />
                    <div className="compass-cross cross-vertical" />
                    <span className="compass-label north">N</span>
                    <span className="compass-label east">E</span>
                    <span className="compass-label south">S</span>
                    <span className="compass-label west">W</span>
                    <div className="compass-center"><Telescope size={22} /></div>
                  </div>
                  <div className="coordinate-list">
                    <div><span>Azimuth</span><strong>{formatNumber(telescope?.azimuth)}°</strong></div>
                    <div><span>Elevation</span><strong>{formatNumber(telescope?.elevation)}°</strong></div>
                    <div><span>Right ascension</span><strong>{formatNumber(telescope?.right_ascension)}°</strong></div>
                    <div><span>Declination</span><strong>{formatNumber(telescope?.declination)}°</strong></div>
                  </div>
                  <div className="panel-footnote">
                    <span>Pointing data</span>
                    <span>{formatTime(telescope?.timestamp)}</span>
                  </div>
                </section>
              </div>

              <section className="panel bottom-panel">
                <div className="panel-header">
                  <div>
                    <h3>Operational telemetry</h3>
                    <p>Additional measurements from the latest observations</p>
                  </div>
                  <button className="text-button" onClick={() => setActivePage('telemetry')}>
                    Explore telemetry <ChevronRight size={15} />
                  </button>
                </div>
                <div className="metric-grid">
                  <MetricCard
                    label="Motor current"
                    value={formatNumber(telescope?.motor_current)}
                    unit="A"
                    icon={Activity}
                    detail="Telescope"
                  />
                  <MetricCard
                    label="Vibration"
                    value={formatNumber(telescope?.vibration)}
                    unit="mm/s"
                    icon={Activity}
                    detail="Telescope"
                  />
                  <MetricCard
                    label="Humidity"
                    value={formatNumber(weather?.humidity, 1)}
                    unit="%"
                    icon={CloudSun}
                    detail="Weather station"
                  />
                  <MetricCard
                    label="Wind speed"
                    value={formatNumber(weather?.wind_speed, 1)}
                    unit="m/s"
                    icon={Wind}
                    detail="Weather station"
                  />
                  <MetricCard
                    label="Image quality"
                    value={formatNumber(camera?.image_quality)}
                    icon={Camera}
                    detail="Imaging camera"
                  />
                  <MetricCard
                    label="Dome motor temp."
                    value={formatNumber(dome?.motor_temperature, 1)}
                    unit="°C"
                    icon={Gauge}
                    detail="Observatory dome"
                  />
                </div>
              </section>
            </>
          )}

          {activePage === 'telemetry' && (
            <section className="panel table-panel">
              <div className="panel-header">
                <div>
                  <h3>Recent telescope observations</h3>
                  <p>History returned by the QuestDB-backed telemetry API</p>
                </div>
                <span className="table-count">{history.length} records</span>
              </div>
              {history.length === 0 ? (
                <div className="empty-state">No telescope history available.</div>
              ) : (
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Status</th>
                        <th>Azimuth</th>
                        <th>Elevation</th>
                        <th>Tracking error</th>
                        <th>Motor temp.</th>
                        <th>Current</th>
                        <th>Vibration</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...history].reverse().map((item, index) => (
                        <tr key={`${item.timestamp}-${index}`}>
                          <td>{formatTime(item.timestamp)}</td>
                          <td><StatusBadge status={item.status} /></td>
                          <td>{formatNumber(item.azimuth)}°</td>
                          <td>{formatNumber(item.elevation)}°</td>
                          <td>{formatNumber(item.tracking_error)}°</td>
                          <td>{formatNumber(item.motor_temperature)}°C</td>
                          <td>{formatNumber(item.motor_current)} A</td>
                          <td>{formatNumber(item.vibration)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {activePage === 'diagnostics' && (
            <section className="panel diagnostics-panel">
              <div className="diagnostic-hero-icon"><BrainCircuit size={28} /></div>
              <h3>Telescope diagnostic analysis</h3>
              <p>
                Request an analysis for {TELESCOPE_ID}. ASTRA will use the existing diagnostics
                endpoint to evaluate recent telemetry and its configured diagnostic pipeline.
              </p>
              <div className="diagnostic-context">
                <div><span>Target telescope</span><strong>{TELESCOPE_ID}</strong></div>
                <div><span>History limit</span><strong>100 observations</strong></div>
                <div><span>RAG retrieval limit</span><strong>5 documents</strong></div>
              </div>
              <button className="primary-button" onClick={() => void runDiagnostics()} disabled={diagnosticLoading}>
                {diagnosticLoading ? <LoaderCircle size={17} className="spin" /> : <BrainCircuit size={17} />}
                {diagnosticLoading ? 'Analyzing telemetry…' : 'Run diagnostic analysis'}
              </button>
              {diagnosticError && (
                <div className="error-banner diagnostic-error">
                  <AlertCircle size={18} />
                  <div><strong>Diagnostic request failed</strong><p>{diagnosticError}</p></div>
                </div>
              )}
              {diagnostic && (
                <div className="diagnostic-result">
                  <div className="result-heading">
                    <CheckCircle2 size={18} />
                    <strong>Diagnostic response received</strong>
                  </div>
                  <pre>{JSON.stringify(diagnostic, null, 2)}</pre>
                </div>
              )}
            </section>
          )}
          {activePage === 'events' && <EventsPage />}
          {activePage === 'rag' && <RAGPage />}

          <footer className="page-footer">
            <span>ASTRA · Observatory Data &amp; AI Platform</span>
            <span>
              {health?.status === 'ok' ? (
                <><CheckCircle2 size={13} /> API reachable</>
              ) : (
                <><AlertCircle size={13} /> API status unavailable</>
              )}
            </span>
          </footer>
        </div>
      </main>
    </div>
  )
}
