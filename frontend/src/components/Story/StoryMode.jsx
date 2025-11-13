import React, { useState } from 'react'
import { Paper, Typography, Box, Button, TextField, MenuItem, Alert } from '@mui/material'
import axios from 'axios'

const intents = [
  { value: 'explain', label: 'Explain' },
  { value: 'explore', label: 'Explore' },
  { value: 'predict', label: 'Predict' },
]
const audiences = [
  { value: 'exec', label: 'Executives' },
  { value: 'tech', label: 'Technical' },
  { value: 'general', label: 'General' },
]
const directions = [
  { value: 'trends', label: 'Trends' },
  { value: 'risks', label: 'Risks' },
  { value: 'opportunities', label: 'Opportunities' },
]

function StoryMode({ datasetId, onComplete }) {
  const [intent, setIntent] = useState('explain')
  const [audience, setAudience] = useState('general')
  const [direction, setDirection] = useState('trends')
  const [story, setStory] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await axios.post('/api/story/generate', {
        dataset_id: datasetId,
        intent,
        audience,
        direction
      })
      setStory(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to generate story')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
      <Typography variant="h5" fontWeight={800} gutterBottom sx={{ mb: 1 }}>
        Data Story Generation
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Create a narrative based on the EDA insights you just reviewed. Tailor it to your intent, audience, and focus direction. This story will be included in your final report.
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 2, mb: 3 }}>
        <TextField 
          select 
          label="Intent" 
          value={intent} 
          onChange={(e) => setIntent(e.target.value)}
          fullWidth
        >
          {intents.map((o) => <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>)}
        </TextField>
        <TextField 
          select 
          label="Audience" 
          value={audience} 
          onChange={(e) => setAudience(e.target.value)}
          fullWidth
        >
          {audiences.map((o) => <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>)}
        </TextField>
        <TextField 
          select 
          label="Direction" 
          value={direction} 
          onChange={(e) => setDirection(e.target.value)}
          fullWidth
        >
          {directions.map((o) => <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>)}
        </TextField>
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button 
          variant="outlined" 
          onClick={generate} 
          disabled={loading}
          size="large"
          sx={{ px: 3 }}
        >
          {loading ? 'Generating...' : 'Generate Story'}
        </Button>
        <Button 
          variant="contained" 
          onClick={() => onComplete(story)} 
          disabled={!story || loading}
          size="large"
          sx={{
            px: 4,
            background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
              transform: 'translateY(-2px)',
              boxShadow: 6
            },
            transition: 'all 0.3s ease'
          }}
        >
          Continue to Decision Point
        </Button>
      </Box>
      
      {story && (
        <Box sx={{ 
          mt: 3, 
          p: 3, 
          borderRadius: 2, 
          background: 'linear-gradient(135deg, rgba(99,102,241,0.05), rgba(34,211,238,0.05))',
          border: '1px solid rgba(99,102,241,0.1)'
        }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Generated Story
          </Typography>
          {story.sections?.map((s, idx) => (
            <Box key={idx} sx={{ mb: 3 }}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 1, color: 'primary.main' }}>
                {s.title}
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                {s.body}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  )
}

export default StoryMode
