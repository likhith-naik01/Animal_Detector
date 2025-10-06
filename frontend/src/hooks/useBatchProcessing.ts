import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'

export const useBatchProcessing = (projectId: string, taskId?: string) => {
  const queryClient = useQueryClient()
  
  const { data: status, isLoading, error } = useQuery(
    ['batch-status', projectId, taskId], 
    async () => {
      if (!taskId) return null
      const { data } = await axios.get(`/api/projects/${projectId}/status`, { 
        params: { task_id: taskId } 
      })
      return data
    }, 
    { 
      refetchInterval: 2000, 
      enabled: !!taskId,
      onSuccess: (data) => {
        // Invalidate project results when batch completes
        if (data?.status === 'completed' || data?.status === 'failed') {
          queryClient.invalidateQueries(['projects', projectId, 'results'])
        }
      }
    }
  )

  const startBatch = useMutation(
    async (imagePaths: string[]) => {
      const { data } = await axios.post(`/api/projects/${projectId}/batch`, imagePaths)
      return data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['batch-status', projectId])
      }
    }
  )

  return { 
    status, 
    isLoading, 
    error, 
    startBatch: startBatch.mutateAsync,
    isStartingBatch: startBatch.isLoading
  }
}
