// src/components/Upload/UploadForm.jsx
import React, { useState } from 'react'
import {
  Paper,
  Typography,
  Button,
  Box,
  TextField,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  MenuItem
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

// Utility function for API calls

const BASE_URL = import.meta.env.VITE_API_URL
console.log("BASE_URL:", BASE_URL); // debug



async function post(endpoint, data, isFormData = false) {
  const response = await fetch(`${BASE_URL}/${endpoint}`, {
    method: 'POST',
    body: isFormData ? data : JSON.stringify(data),
    headers: isFormData ? {} : { 'Content-Type': 'application/json' },
  })
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    throw new Error(errData.detail || 'Request failed')
  }
  return response.json()
}

function UploadForm({ onUploadSuccess }) {
  const [tab, setTab] = useState(0)
  const [file, setFile] = useState(null)
  const [apiUrl, setApiUrl] = useState('')
  const [authToken, setAuthToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [preview, setPreview] = useState(null)
  const [datasetId, setDatasetId] = useState(null)
  const [schema, setSchema] = useState([])

  const mapInferType = (d) => {
    if (!d) return 'string'
    const s = String(d).toLowerCase()
    if (s.includes('int')) return 'int'
    if (s.includes('float') || s.includes('double')) return 'float'
    if (s.includes('bool')) return 'boolean'
    if (s.includes('datetime') || s.includes('date') || s.includes('time')) return 'datetime'
    return 'string'
  }

  const initFromResponse = (data) => {
    setPreview(data.preview || null)
    setDatasetId(data.dataset_id)
    const types = data.data_types || {}
    const cols = data.columns || []
    setSchema(cols.map((c) => ({ column: c, dtype: mapInferType(types[c]) })))
  }

  const onDrop = (e) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const f = e.dataTransfer.files[0]
      if (!f.name.match(/\.(csv|xlsx|xls|json|parquet)$/i)) {
        setError('Supported: CSV, Excel, JSON, Parquet')
        return
      }
      setFile(f)
      setError('')
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!selectedFile.name.match(/\.(csv|xlsx|xls|json|parquet)$/i)) {
        setError('Supported: CSV, Excel, JSON, Parquet')
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const handleFileUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await post('ingestion/upload', formData, true)
      setSuccess('File uploaded successfully!')
      initFromResponse(response)
      if (onUploadSuccess) onUploadSuccess(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleApiConnection = async () => {
    if (!apiUrl) {
      setError('Please enter an API URL')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await post('ingestion/api-connection', {
        api_url: apiUrl,
        auth_token: authToken || null
      })
      setSuccess('API connected successfully!')
      initFromResponse(response)
      if (onUploadSuccess) onUploadSuccess(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const applySchema = async () => {
    if (!datasetId) return
    setLoading(true)
    setError('')
    try {
      const res = await post('ingestion/apply-schema', { dataset_id: datasetId, schema })
      setSuccess('Schema applied successfully!')
      setPreview(res.preview)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
      <Typography variant="h5" gutterBottom fontWeight={800} sx={{ mb: 3 }}>
        Data Ingestion
      </Typography>

      <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Upload File" />
        <Tab label="Connect API" />
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      {tab === 0 && (
        <Box>
          <Box
            sx={{ mb: 2, p: 4, border: '2px dashed #93c5fd', borderRadius: 2, textAlign: 'center', color: 'text.secondary', background: 'linear-gradient(180deg, rgba(14,165,233,0.05), transparent)' }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            <Typography variant="body1" sx={{ mb: 1 }}>Drag & drop your file here</Typography>
            <Typography variant="caption">Supported: CSV, Excel, JSON, Parquet</Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <input accept=".csv,.xlsx,.xls,.json,.parquet" style={{ display: 'none' }} id="file-upload" type="file" onChange={handleFileChange} />
            <label htmlFor="file-upload">
              <Button variant="outlined" component="span" startIcon={<CloudUploadIcon />} sx={{ mb: 2 }}>Select File</Button>
            </label>
            {file && <Typography variant="body2" sx={{ mt: 1 }}>Selected: {file.name}</Typography>}
          </Box>

          <Button
            variant="contained"
            onClick={handleFileUpload}
            disabled={loading || !file}
            fullWidth
            size="large"
            sx={{
              mt: 2,
              py: 1.5,
              background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
              '&:hover': { background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)', transform: 'translateY(-2px)', boxShadow: 6 },
              transition: 'all 0.3s ease'
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Upload File'}
          </Button>
        </Box>
      )}

      {tab === 1 && (
        <Box>
          <TextField
            fullWidth
            label="API URL"
            variant="outlined"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            placeholder="https://api.example.com/data"
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Auth Token (Optional)"
            variant="outlined"
            type="password"
            value={authToken}
            onChange={(e) => setAuthToken(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            onClick={handleApiConnection}
            disabled={loading || !apiUrl}
            fullWidth
            size="large"
            sx={{
              mt: 2,
              py: 1.5,
              background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
              '&:hover': { background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)', transform: 'translateY(-2px)', boxShadow: 6 },
              transition: 'all 0.3s ease'
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Connect to API'}
          </Button>
        </Box>
      )}

      {preview && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1" gutterBottom>Preview (first {preview.rows} rows)</Typography>
          <Box sx={{ maxHeight: 300, overflow: 'auto', border: '1px solid #e5e7eb', borderRadius: 1 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  {preview.columns.map((c) => <TableCell key={c}>{c}</TableCell>)}
                </TableRow>
              </TableHead>
              <TableBody>
                {preview.data.map((r, i) => (
                  <TableRow key={i}>
                    {r.map((cell, j) => <TableCell key={j}>{String(cell)}</TableCell>)}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Schema</Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 2 }}>
              {schema.map((s, idx) => (
                <Box key={idx} sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <TextField label="Column" value={s.column} size="small" disabled sx={{ flex: 2 }} />
                  <TextField
                    select
                    label="Type"
                    value={s.dtype}
                    size="small"
                    onChange={(e) => setSchema(prev => prev.map((p, i) => i === idx ? { ...p, dtype: e.target.value } : p))}
                    sx={{ flex: 1 }}
                  >
                    {['string', 'int', 'float', 'boolean', 'datetime'].map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                  </TextField>
                </Box>
              ))}
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button variant="contained" onClick={applySchema} disabled={loading || !datasetId}>Apply Schema</Button>
            </Box>
          </Box>
        </Box>
      )}
    </Paper>
  )
}

export default UploadForm