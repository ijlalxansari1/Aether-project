import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    const init = async () => {
      try {
        if (!token) {
          // auto-guest
          const res = await axios.post('/api/auth/guest')
          const t = res.data.access_token
          localStorage.setItem('token', t)
          setToken(t)
          axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
        } else {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        }
        await fetchUser()
      } catch (e) {
        setLoading(false)
      }
    }
    init()
  }, [])

  const fetchUser = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      setToken(null)
      delete axios.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await axios.post('/api/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    const newToken = response.data.access_token
    setToken(newToken)
    localStorage.setItem('token', newToken)
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    await fetchUser()
    return response.data
  }

  const register = async (username, email, password, role = 'analyst') => {
    const response = await axios.post('/api/auth/register', { username, email, password, role })
    await login(username, password)
    return response.data
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const value = { user, login, register, logout, loading }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

