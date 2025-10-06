import React from 'react'
import { useQuery } from 'react-query'
import axios from 'axios'
import { ProjectGrid } from './components/dashboard/ProjectGrid'
import { ImageUpload } from './components/upload/ImageUpload'
import { StatCard, SpeciesBreakdownChart, ProcessingTimelineChart } from './components/charts/Charts'

async function fetchProjects() {
  const { data } = await axios.get('/api/projects')
  return data
}

export default function App() {
  const { data: projects, isLoading } = useQuery(['projects'], fetchProjects, { retry: false })

  // Mock data for charts
  const mockSpeciesData = {
    "leopard": 15,
    "tiger": 8,
    "elephant": 12,
    "deer": 25,
    "bird": 18
  }

  const mockTimelineData = [
    { date: "2024-01-01", processed: 120, animals: 45 },
    { date: "2024-01-02", processed: 98, animals: 32 },
    { date: "2024-01-03", processed: 156, animals: 67 },
    { date: "2024-01-04", processed: 134, animals: 52 },
    { date: "2024-01-05", processed: 189, animals: 78 }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">TrailGuard AI</h1>
          <div className="text-sm text-gray-600">
            Wildlife Detection & Analysis Platform
          </div>
        </div>

        {/* Statistics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard 
            title="Total Images Processed"
            value="12,458"
            trend={{ value: 23, isPositive: true }}
          />
          <StatCard 
            title="Animals Detected"
            value="1,247"
            trend={{ value: 15, isPositive: true }}
          />
          <StatCard 
            title="Species Identified"
            value="42"
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard 
            title="Time Saved"
            value="3.2 weeks"
            trend={{ value: 65, isPositive: true }}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SpeciesBreakdownChart speciesCount={mockSpeciesData} />
          <ProcessingTimelineChart data={mockTimelineData} />
        </div>

        {/* Upload Section */}
        <ImageUpload />

        {/* Projects */}
        {isLoading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading projects...</p>
          </div>
        ) : (
          <ProjectGrid projects={projects || []} />
        )}
      </div>
    </div>
  )
}

