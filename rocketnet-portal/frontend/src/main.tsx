import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'

import App from './App'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import './styles/globals.css'

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AuthProvider>
            <App />
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--toast-bg)',
                  color: 'var(--toast-color)',
                  border: '1px solid var(--border)',
                },
                success: {
                  iconTheme: {
                    primary: 'var(--success)',
                    secondary: 'white',
                  },
                },
                error: {
                  iconTheme: {
                    primary: 'var(--destructive)',
                    secondary: 'white',
                  },
                },
              }}
            />
          </AuthProvider>
        </ThemeProvider>
        {import.meta.env.DEV && <ReactQueryDevtools />}
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>,
)