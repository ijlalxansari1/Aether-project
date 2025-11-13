import React, { useEffect, useState } from 'react'
import { Paper, Typography, Box, Button, Chip, Alert, List, ListItem, ListItemText } from '@mui/material'
import axios from 'axios'

function EthicsScan({ datasetId, onComplete }) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  const runScan = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await axios.get(`/api/ethics/scan/${datasetId}`)
      setData(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Ethical scan failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runScan()
  }, [datasetId])

  return (
    <Paper elevation={3} sx={{ p: 4 }}>
      <Typography variant="h5" fontWeight={800} gutterBottom>
        Ethical Analysis
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {data && (
        <>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            {data.sensitive_attributes?.length ? data.sensitive_attributes.map((s) => (
              <Chip key={s} label={s} color="warning" />
            )) : <Chip label="No sensitive attributes detected" variant="outlined" />}
          </Box>
          <Typography variant="subtitle1" gutterBottom>Notes</Typography>
          <List>
            {(data.notes || []).map((n, i) => (
              <ListItem key={i}><ListItemText primary={n} /></ListItem>
            ))}
          </List>
        </>
      )}
      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
        <Button variant="outlined" onClick={runScan} disabled={loading}>Re-run</Button>
        <Button variant="contained" onClick={onComplete} disabled={loading}>Continue</Button>
      </Box>
    </Paper>
  )
}

export default EthicsScan
