import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

const data = [
  { name: 'Technology', value: 35, color: '#00D4AA' },
  { name: 'Healthcare', value: 20, color: '#7B61FF' },
  { name: 'Finance', value: 15, color: '#FFD700' },
  { name: 'Consumer', value: 12, color: '#00F0FF' },
  { name: 'Energy', value: 10, color: '#FF61DC' },
  { name: 'Other', value: 8, color: '#6B7280' },
]

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card p-3 border border-primary/30">
        <p className="font-medium">{payload[0].name}</p>
        <p className="text-primary font-bold">{payload[0].value}%</p>
      </div>
    )
  }
  return null
}

export default function AssetAllocation() {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="grid grid-cols-2 gap-2 mt-4">
        {data.map((item) => (
          <div key={item.name} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-gray-400">{item.name}</span>
            <span className="text-sm font-medium ml-auto">{item.value}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
