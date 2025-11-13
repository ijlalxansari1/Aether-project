import React, { useState } from 'react'
import {
  Paper,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import axios from 'axios'

function DecisionPoint({ datasetId, story, onGenerateReport, onContinueAnalysis }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerateReport = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`/api/report/${datasetId}`)
      const blob = new Blob([response.data.html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `aether_report_${datasetId}_${new Date().toISOString().split('T')[0]}.html`
      a.click()
      URL.revokeObjectURL(url)
      
      if (onGenerateReport) {
        onGenerateReport(response.data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  const handleContinueAnalysis = () => {
    if (onContinueAnalysis) {
      onContinueAnalysis()
    }
  }

  return (
    <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
      <Typography variant="h5" fontWeight={800} gutterBottom sx={{ mb: 1 }}>
        Analysis Decision Point
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        You've completed the initial analysis. Choose your next step:
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Option 1: Generate Report */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              height: '100%',
              border: '2px solid',
              borderColor: 'primary.main',
              borderRadius: 3,
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 8,
                borderColor: 'primary.dark'
              }
            }}
            onClick={handleGenerateReport}
          >
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2
                }}
              >
                <DescriptionIcon sx={{ fontSize: 40, color: 'white' }} />
              </Box>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Generate Report
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Create a comprehensive report with EDA visualizations, insights, and your data story.
                Perfect for sharing with stakeholders or documentation.
              </Typography>
              <Button
                variant="contained"
                size="large"
                fullWidth
                disabled={loading}
                sx={{
                  py: 1.5,
                  background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)'
                  }
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Download Report'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Option 2: Continue with ML Analysis */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              height: '100%',
              border: '2px solid',
              borderColor: 'secondary.main',
              borderRadius: 3,
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 8,
                borderColor: 'secondary.dark'
              }
            }}
            onClick={handleContinueAnalysis}
          >
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #22d3ee 0%, #60a5fa 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2
                }}
              >
                <AnalyticsIcon sx={{ fontSize: 40, color: 'white' }} />
              </Box>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Deep ML Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Continue with exploratory data analysis, model training, and advanced insights.
                Build predictive models and evaluate fairness metrics.
              </Typography>
              <Button
                variant="contained"
                size="large"
                fullWidth
                color="secondary"
                sx={{
                  py: 1.5,
                  background: 'linear-gradient(135deg, #22d3ee 0%, #60a5fa 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)'
                  }
                }}
              >
                Continue to EDA & Modeling
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Story Preview */}
      {story && story.sections && (
        <Box sx={{ mt: 4, p: 3, borderRadius: 2, background: 'linear-gradient(135deg, rgba(99,102,241,0.05), rgba(34,211,238,0.05))' }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Your Data Story Preview
          </Typography>
          {story.sections.slice(0, 2).map((section, idx) => (
            <Box key={idx} sx={{ mb: 2 }}>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 0.5 }}>
                {section.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {section.body.length > 200 ? `${section.body.substring(0, 200)}...` : section.body}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  )
}

export default DecisionPoint

