import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Grid
} from '@mui/material'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <Container maxWidth="md" sx={{ mt: { xs: 6, md: 10 } }}>
      <Paper elevation={6} sx={{ overflow: 'hidden', borderRadius: 4 }}>
        <Grid container>
          <Grid item xs={12} md={6} sx={{ p: { xs: 3, md: 5 } }}>
            <Typography variant="h4" component="h1" gutterBottom fontWeight={800}>
              Welcome back
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Sign in to continue exploring data, building models, and generating insights.
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username"
                variant="outlined"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                sx={{ mb: 2.2 }}
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                variant="outlined"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                sx={{ mb: 2.5 }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
              >
                Login
              </Button>
              <Typography align="center" sx={{ mt: 2 }}>
                Don't have an account? <Link to="/register">Register</Link>
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}
            sx={{
              display: { xs: 'none', md: 'block' },
              background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
              color: 'white',
              p: 5,
            }}
          >
            <Box sx={{ maxWidth: 360 }}>
              <Typography variant="h5" fontWeight={800} gutterBottom>
                AETHER Insight Platform
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Ethical, explainable, and human-centered analytics. Upload data, profile quality, train recommended models, and evaluate fairness — all in one place.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  )
}

export default Login

