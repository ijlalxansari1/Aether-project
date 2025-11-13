import React from 'react'
import { Container, Grid, Paper, Typography, Box, Button } from '@mui/material'
import { Link } from 'react-router-dom'

const cards = [
  { title: 'Upload Dataset', body: 'CSV, Excel, JSON, Parquet — or connect via API with parameters.', to: '/app' },
  { title: 'Ethical Analysis', body: 'Sensitive attributes, imbalance alerts, and transparent notes.' },
  { title: 'EDA', body: 'Statistics, missingness, histograms, correlations, and plain-language insights.' },
  { title: 'Story Mode', body: 'Set intent, audience, and direction to generate a narrative.' },
  { title: 'Modeling', body: 'Classic ML with ROC, confusion matrix, and fairness metrics.' },
  { title: 'Reports', body: 'Export HTML/PDF/DOCX with overview, ethics, EDA, story, and results.' },
]

function Home() {
  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }} className="fade-up">
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
          <Box
            component="img"
            src="/aether-logo.svg"
            alt="AETHER Insight Logo"
            sx={{
              width: 120,
              height: 120,
              filter: 'drop-shadow(0 4px 12px rgba(99,102,241,0.3))',
              animation: 'float 3s ease-in-out infinite',
              '@keyframes float': {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: 'translateY(-10px)' }
              }
            }}
          />
        </Box>
        <Typography variant="h2" fontWeight={900} gutterBottom sx={{
          background: 'linear-gradient(90deg,#6366f1 0%, #22d3ee 60%, #60a5fa 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontSize: { xs: '2rem', md: '3rem' },
          mb: 2
        }}>
          AETHER Insight Platform
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 840, mx: 'auto', mb: 1, fontWeight: 400 }}>
          Transform data into actionable insights with ethical AI
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 840, mx: 'auto', mb: 4 }}>
          Unified analytics, EDA, ethical AI, storytelling, and ML — in one calm workflow.
          Upload data, understand it with transparent profiling, explore with visuals, then ship a
          narrative and a polished report. No clutter. No panic. Just possibility.
        </Typography>
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button 
            component={Link} 
            to="/app" 
            variant="contained" 
            size="large"
            sx={{ 
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
                transform: 'translateY(-2px)',
                boxShadow: 6
              },
              transition: 'all 0.3s ease'
            }}
          >
            Start Analyzing
          </Button>
          <Button 
            component={Link} 
            to="/faq" 
            variant="outlined" 
            size="large"
            sx={{ 
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              borderWidth: 2,
              '&:hover': {
                borderWidth: 2,
                transform: 'translateY(-2px)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            Learn More
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {cards.map((c, i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Paper 
              elevation={2} 
              sx={{ 
                p: 3.5, 
                height: '100%', 
                border: '1px solid', 
                borderColor: 'divider',
                borderRadius: 3,
                background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: 4,
                  background: `linear-gradient(90deg, ${
                    i % 3 === 0 ? '#6366f1' : i % 3 === 1 ? '#22d3ee' : '#60a5fa'
                  }, transparent)`,
                  opacity: 0.8
                },
                '&:hover': { 
                  transform: 'translateY(-6px)', 
                  boxShadow: 8,
                  borderColor: 'primary.main'
                } 
              }}
            >
              <Typography variant="h6" fontWeight={800} gutterBottom sx={{ mb: 1.5 }}>
                {c.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                {c.body}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}

export default Home
