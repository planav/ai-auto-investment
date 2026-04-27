import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const value = payload[0]?.value
  const invested = payload[1]?.value
  return (
    <div className="glass-card p-3 border border-primary/30 text-sm">
      <p className="text-gray-400 mb-1">{label}</p>
      <p className="text-primary font-bold">
        ${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
      </p>
      {invested != null && (
        <p className="text-gray-500 text-xs">
          Invested: ${Number(invested).toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </p>
      )}
    </div>
  )
}

/**
 * PortfolioChart
 *
 * Props:
 *   chartData   — array of { date, value } from /portfolios/{id}/chart
 *   invested    — number — amount originally invested (used as baseline)
 */
export default function PortfolioChart({ chartData = [], invested = 0 }) {
  // Build display data from real snapshots
  let data = []

  if (chartData && chartData.length > 0) {
    data = chartData.map(point => ({
      label: formatLabel(point.date),
      value: Number(point.value),
      invested: Number(invested),
    }))
  } else if (invested > 0) {
    // No snapshots yet — show a flat line at invested amount
    const now = new Date()
    data = [
      { label: 'Invested', value: invested, invested },
      { label: 'Now',      value: invested, invested },
    ]
  } else {
    // No data at all — placeholder
    return (
      <div className="h-64 flex flex-col items-center justify-center text-gray-500 text-sm">
        <p>No portfolio value history yet.</p>
        <p className="text-xs mt-1">Create your first portfolio to see performance here.</p>
      </div>
    )
  }

  const allValues = data.map(d => d.value)
  const minVal = Math.min(...allValues, invested) * 0.98
  const maxVal = Math.max(...allValues, invested) * 1.02

  const latest = data[data.length - 1]?.value || invested
  const gainLoss = latest - invested
  const isPositive = gainLoss >= 0

  return (
    <div>
      {/* Summary row */}
      {invested > 0 && (
        <div className="flex items-center gap-6 mb-4 text-sm">
          <div>
            <span className="text-gray-500">Current Value </span>
            <span className="font-bold text-white">
              ${Number(latest).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Return </span>
            <span className={`font-semibold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
              {isPositive ? '+' : ''}${Number(gainLoss).toLocaleString(undefined, { maximumFractionDigits: 0 })}
              {' '}({isPositive ? '+' : ''}{((gainLoss / invested) * 100).toFixed(2)}%)
            </span>
          </div>
        </div>
      )}

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={isPositive ? '#00D4AA' : '#ef4444'} stopOpacity={0.3} />
                <stop offset="95%" stopColor={isPositive ? '#00D4AA' : '#ef4444'} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorInvested" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#7B61FF" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#7B61FF" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A1A2E" />
            <XAxis
              dataKey="label"
              stroke="#6B7280"
              tick={{ fill: '#6B7280', fontSize: 11 }}
              axisLine={{ stroke: '#374151' }}
              interval="preserveStartEnd"
            />
            <YAxis
              stroke="#6B7280"
              tick={{ fill: '#6B7280', fontSize: 11 }}
              axisLine={{ stroke: '#374151' }}
              tickFormatter={v => `$${(v / 1000).toFixed(1)}k`}
              domain={[minVal, maxVal]}
            />
            <Tooltip content={<CustomTooltip />} />
            {invested > 0 && (
              <ReferenceLine
                y={invested}
                stroke="#7B61FF"
                strokeDasharray="4 3"
                strokeWidth={1.5}
                label={{ value: 'Invested', fill: '#7B61FF', fontSize: 10, position: 'right' }}
              />
            )}
            <Area
              type="monotone"
              dataKey="value"
              stroke={isPositive ? '#00D4AA' : '#ef4444'}
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorValue)"
              name="Portfolio Value"
              dot={data.length <= 10}
              activeDot={{ r: 5 }}
            />
            <Area
              type="monotone"
              dataKey="invested"
              stroke="#7B61FF"
              strokeWidth={0}
              fillOpacity={0}
              fill="url(#colorInvested)"
              name="Invested"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function formatLabel(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr.replace(' ', 'T'))
    // If within last 24h show time, otherwise show date
    const now = new Date()
    const diffMs = now - d
    if (diffMs < 86400000) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}
