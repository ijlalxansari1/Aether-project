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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid
} from '@mui/material'

function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('analyst')
  const [error, setError] = useState('')
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    // Validate password length (bcrypt limit is 72 bytes)
    if (password.length > 72) {
      setError('Password is too long. Maximum length is 72 characters.')
      return
    }
    
    try {
      await register(username, email, password, role)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <Container maxWidth="md" sx={{ mt: { xs: 6, md: 10 } }}>
      <Paper elevation={6} sx={{ overflow: 'hidden', borderRadius: 4 }}>
        <Grid container>
          <Grid item xs={12} md={6} sx={{ p: { xs: 3, md: 5 } }}>
            <Typography variant="h4" component="h1" gutterBottom fontWeight={800}>
              Create your account
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Join AETHER to build explainable models and fair insights.
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                fullWidth
                label="Username"
                variant="outlined"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Email"
                type="email"
                variant="outlined"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                variant="outlined"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                inputProps={{ maxLength: 72 }}
                helperText={password.length > 70 ? "Password is too long (max 72 characters)" : ""}
                error={password.length > 72}
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Role</InputLabel>
                <Select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  label="Role"
                >
                  <MenuItem value="analyst">Analyst</MenuItem>
                  <MenuItem value="viewer">Viewer</MenuItem>
                </Select>
              </FormControl>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={password.length > 72}
              >
                Register
              </Button>
              <Typography align="center" sx={{ mt: 2 }}>
                Already have an account? <Link to="/login">Login</Link>
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
                Welcome to AETHER
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Experience a visual-first workflow with automated narratives and fairness insights. Your data journey starts here.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  )
}

export default Register

