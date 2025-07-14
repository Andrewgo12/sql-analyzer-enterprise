import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export const usePageTransition = () => {
  const [isLoading, setIsLoading] = useState(false)
  const location = useLocation()

  useEffect(() => {
    // Show loading on route change
    setIsLoading(true)
    
    // Simulate loading time for smooth transitions
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 300)

    return () => clearTimeout(timer)
  }, [location.pathname])

  return { isLoading }
}
