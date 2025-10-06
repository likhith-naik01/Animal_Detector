import { useMutation } from 'react-query'
import axios from 'axios'

export const useImageAnalysis = () => {
  const mutation = useMutation(async (image: File) => {
    const formData = new FormData()
    formData.append('file', image)
    const { data } = await axios.post('/api/analyze/single', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  })
  
  return { 
    analyzeImage: mutation.mutateAsync, 
    isLoading: mutation.isLoading,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset
  }
}
