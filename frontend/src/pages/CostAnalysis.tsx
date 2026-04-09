import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const monthlyData = [
  { month: 'Oct', aws: 1100, mongodb: 380, datadog: 340, confluent: 190, singlestore: 75, harness: 55 },
  { month: 'Nov', aws: 1150, mongodb: 395, datadog: 355, confluent: 195, singlestore: 78, harness: 57 },
  { month: 'Dec', aws: 1180, mongodb: 400, datadog: 360, confluent: 200, singlestore: 80, harness: 58 },
  { month: 'Jan', aws: 1200, mongodb: 410, datadog: 365, confluent: 205, singlestore: 82, harness: 58 },
  { month: 'Feb', aws: 1220, mongodb: 415, datadog: 370, confluent: 208, singlestore: 83, harness: 59 },
  { month: 'Mar', aws: 1245, mongodb: 420, datadog: 380, confluent: 210, singlestore: 85, harness: 60 },
]

const pieData = [
  { name: 'AWS', value: 1245, color: '#F97316' },
  { name: 'MongoDB', value: 420, color: '#22C55E' },
  { name: 'Datadog', value: 380, color: '#8B5CF6' },
  { name: 'Confluent', value: 210, color: '#3B82F6' },
  { name: 'SingleStore', value: 85, color: '#06B6D4' },
  { name: 'Harness', value: 60, color: '#6B7280' },
]

export default function CostAnalysis() {
  const [period, setPeriod] = useState('2026-03')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-driven-navy">Cost Analysis</h2>
        <input
          type="month"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border border-driven-gray-300 rounded-lg text-sm"
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Trend chart */}
        <div className="col-span-2 bg-white rounded-xl p-6 shadow-sm border border-driven-gray-200">
          <h3 className="text-lg font-semibold text-driven-navy mb-4">Monthly Cost Trend (in $K)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(val: number) => `$${val}K`} />
              <Legend />
              <Bar dataKey="aws" fill="#F97316" name="AWS" stackId="a" />
              <Bar dataKey="mongodb" fill="#22C55E" name="MongoDB" stackId="a" />
              <Bar dataKey="datadog" fill="#8B5CF6" name="Datadog" stackId="a" />
              <Bar dataKey="confluent" fill="#3B82F6" name="Confluent" stackId="a" />
              <Bar dataKey="singlestore" fill="#06B6D4" name="SingleStore" stackId="a" />
              <Bar dataKey="harness" fill="#6B7280" name="Harness" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-driven-gray-200">
          <h3 className="text-lg font-semibold text-driven-navy mb-4">Platform Split</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(val: number) => `$${val}K`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
