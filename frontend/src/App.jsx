import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Box from '@mui/material/Box'
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import UploadForm from './components/Upload/UploadForm'
import Dashboard from './components/Dashboard/Dashboard'
import ModelResults from './components/ML/ModelResults'
import FairnessReport from './components/Fairness/FairnessReport'
import Workflow from './components/Workflow/Workflow'
import Navbar from './components/Layout/Navbar'
import FAQ from './components/FAQ/FAQ'
import Home from './components/Landing/Home'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './App.css'

const buildTheme = (mode) => createTheme({
  palette: {
    mode,
    primary: { 
      main: '#2563eb', // Professional blue
      light: '#3b82f6',
      dark: '#1e40af',
      contrastText: '#ffffff'
    },
    secondary: { 
      main: '#10b981', // Success green
      light: '#34d399',
      dark: '#059669'
    },
    success: { main: '#10b981', light: '#34d399', dark: '#059669' },
    warning: { main: '#f59e0b', light: '#fbbf24', dark: '#d97706' },
    error: { main: '#ef4444', light: '#f87171', dark: '#dc2626' },
    info: { main: '#3b82f6', light: '#60a5fa', dark: '#2563eb' },
    background: {
      default: mode === 'dark' ? '#0f172a' : '#f8fafc',
      paper: mode === 'dark' ? '#1e293b' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#f1f5f9' : '#0f172a',
      secondary: mode === 'dark' ? '#94a3b8' : '#64748b',
    },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"Inter", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    h5: { fontWeight: 700, letterSpacing: '-0.01em' },
    h6: { fontWeight: 600 },
    button: { fontWeight: 600, textTransform: 'none' },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { 
          textTransform: 'none', 
          borderRadius: 10, 
          paddingInline: 20, 
          paddingBlock: 10,
          fontWeight: 600,
          transition: 'all 0.2s ease',
          '&:hover': { transform: 'translateY(-1px)', boxShadow: 4 }
        },
        containedPrimary: { 
          background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
          '&:hover': { 
            background: 'linear-gradient(135deg, #1e40af 0%, #2563eb 100%)',
          }
        },
      },
    },
    MuiPaper: {
      styleOverrides: { 
        root: { 
          borderRadius: 12, 
          transition: 'all 0.2s ease',
          boxShadow: mode === 'dark' 
            ? '0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.24)'
            : '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'
        } 
      },
    },
    MuiCard: { 
      styleOverrides: { 
        root: { 
          borderRadius: 12,
          boxShadow: mode === 'dark'
            ? '0 2px 8px rgba(0,0,0,0.3)'
            : '0 2px 8px rgba(0,0,0,0.1)'
        } 
      } 
    },
    MuiTextField: { 
      defaultProps: { size: 'medium' },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
          }
        }
      }
    },
    MuiChip: { 
      styleOverrides: { 
        root: { 
          fontWeight: 600,
          borderRadius: 8
        } 
      } 
    },
  },
})

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }
  
  return user ? children : <Navigate to="/" />
}

function AppRoutes() {
  const { user } = useAuth()
  
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <Workflow />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard/:datasetId"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/models/:modelRunId"
        element={
          <ProtectedRoute>
            <ModelResults />
          </ProtectedRoute>
        }
      />
      <Route
        path="/fairness/:fairnessReportId"
        element={
          <ProtectedRoute>
            <FairnessReport />
          </ProtectedRoute>
        }
      />
      <Route path="/faq" element={<FAQ />} />
    </Routes>
  )
}

function App() {
  const [mode, setMode] = useState('light')
  const theme = buildTheme(mode)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Box sx={{ 
            minHeight: '100vh',
            background: mode === 'dark'
              ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)'
              : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f8fafc 100%)',
            backgroundAttachment: 'fixed'
          }}>
            <Navbar mode={mode} onToggleMode={() => setMode(mode === 'light' ? 'dark' : 'light')} />
            <Box sx={{ maxWidth: 1280, mx: 'auto', px: { xs: 2, md: 3 }, py: 3 }}>
              <AppRoutes />
            </Box>
          </Box>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

