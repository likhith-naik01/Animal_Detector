import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'

export const useProjects = () => {
  const queryClient = useQueryClient()
  
  const { data: projects, isLoading, error } = useQuery(
    ['projects'],
    async () => {
      const { data } = await axios.get('/api/projects')
      return data
    }
  )

  const createProject = useMutation(
    async ({ name, description }: { name: string; description?: string }) => {
      const { data } = await axios.post('/api/projects', null, {
        params: { name, description }
      })
      return data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['projects'])
      }
    }
  )

  return { 
    projects, 
    isLoading, 
    error, 
    createProject: createProject.mutateAsync,
    isCreating: createProject.isLoading
  }
}

export const useProjectResults = (projectId: string, page: number = 1, limit: number = 50) => {
  return useQuery(
    ['projects', projectId, 'results', page, limit],
    async () => {
      const { data } = await axios.get(`/api/projects/${projectId}/results`, {
        params: { page, limit }
      })
      return data
    },
    {
      enabled: !!projectId
    }
  )
}
