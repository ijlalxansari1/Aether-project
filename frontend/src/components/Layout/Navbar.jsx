import React from 'react'
import { Link } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Button, Box, IconButton } from '@mui/material'
import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined'
import LightModeOutlinedIcon from '@mui/icons-material/LightModeOutlined'

function Navbar({ mode = 'light', onToggleMode = () => {} }) {
  return (
    <AppBar position="sticky" elevation={0}
      sx={{
        background: mode === 'dark'
          ? 'linear-gradient(90deg, #1e293b 0%, #334155 50%, #1e293b 100%)'
          : 'linear-gradient(90deg, #2563eb 0%, #3b82f6 50%, #2563eb 100%)',
        borderBottom: mode === 'dark' ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.08)',
        backdropFilter: 'blur(10px)',
      }}
    >
      <Toolbar sx={{ gap: 2 }}>
        <Box component={Link} to="/" sx={{ display: 'flex', alignItems: 'center', color: 'inherit', textDecoration: 'none', gap: 1.5 }}>
          <Box
            component="img"
            src="/aether-logo.svg"
            alt="AETHER Insight Logo"
            sx={{
              width: 40,
              height: 40,
              filter: mode === 'dark' ? 'brightness(1.1)' : 'brightness(0.95)',
              transition: 'transform 0.2s ease',
              '&:hover': { transform: 'scale(1.05) rotate(5deg)' }
            }}
          />
          <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: 0.4, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
            AETHER Insight
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Button component={Link} to="/faq" color="inherit" sx={{ textTransform: 'none' }}>FAQ</Button>

        <IconButton color="inherit" onClick={onToggleMode} aria-label="toggle theme">
          {mode === 'dark' ? <LightModeOutlinedIcon /> : <DarkModeOutlinedIcon />}
        </IconButton>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar

