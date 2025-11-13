import React, { useState } from 'react'
import { Container, Stepper, Step, StepLabel, Box, Button, Paper, Typography } from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import UploadForm from '../Upload/UploadForm'
import DataProfile from '../DataProfile/DataProfile'
import EthicsScan from '../Ethics/EthicsScan'
import StoryMode from '../Story/StoryMode'
import DecisionPoint from './DecisionPoint'
import EDAView from '../EDA/EDAView'
import ModelSelection from '../ML/ModelSelection'
import Dashboard from '../Dashboard/Dashboard'

// Updated workflow: EDA before Story (story needs EDA insights), then decision point
const steps = ['Upload Data', 'Data Profile', 'Ethics', 'EDA', 'Story', 'Decision Point', 'Model Selection', 'Dashboard']

function Workflow() {
  const [activeStep, setActiveStep] = useState(0)
  const [datasetId, setDatasetId] = useState(null)
  const [profileData, setProfileData] = useState(null)
  const [edaData, setEdaData] = useState(null)
  const [story, setStory] = useState(null)
  const [modelRunId, setModelRunId] = useState(null)

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1)
    }
  }

  const canGoBack = activeStep > 0

  const handleUploadSuccess = (data) => {
    setDatasetId(data.dataset_id)
    setActiveStep(1)
  }

  const handleProfileComplete = (data) => {
    setProfileData(data)
    setActiveStep(2)
  }

  const handleEthicsComplete = () => {
    setActiveStep(3)  // Go to EDA
  }

  const handleEdaComplete = (edaData) => {
    setEdaData(edaData)  // Store EDA data for story generation
    setActiveStep(4)  // Go to Story (EDA provides insights for story)
  }

  const handleStoryComplete = (storyPayload) => {
    setStory(storyPayload)
    setActiveStep(5)  // Go to Decision Point
  }

  const handleGenerateReport = (reportData) => {
    // Report generated and downloaded, user can stay here or go back
    // Could add a success message or redirect
  }

  const handleContinueAnalysis = () => {
    setActiveStep(6)  // Go to Model Selection (skip decision point in stepper)
  }

  const handleModelTrainingComplete = (data) => {
    setModelRunId(data.model_run_id)
    setActiveStep(7)  // Go to Dashboard
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          {canGoBack && (
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={handleBack}
              variant="outlined"
              sx={{ minWidth: 120 }}
            >
              Previous Step
            </Button>
          )}
          <Box sx={{ flex: 1 }} />
          <Box sx={{ 
            px: 2, 
            py: 0.5, 
            borderRadius: 2, 
            background: 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(34,211,238,0.1))',
            border: '1px solid rgba(99,102,241,0.2)'
          }}>
            <Typography variant="caption" color="text.secondary">
              {activeStep <= 5 
                ? `Step ${activeStep + 1} of ${steps.length}`
                : `Step ${activeStep - 4} of ${steps.length - 5} (ML Analysis)`}
            </Typography>
          </Box>
        </Box>
        <Stepper activeStep={activeStep <= 5 ? activeStep : activeStep - 1} alternativeLabel>
          {steps
            .filter((label) => {
              // Hide "Decision Point" from stepper if we're past it (in ML analysis path)
              if (label === 'Decision Point' && activeStep > 5) {
                return false
              }
              return true
            })
            .map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
        </Stepper>
      </Paper>

      <Box>
        {activeStep === 0 && (<UploadForm onUploadSuccess={handleUploadSuccess} />)}
        {activeStep === 1 && datasetId && (<DataProfile datasetId={datasetId} onComplete={handleProfileComplete} />)}
        {activeStep === 2 && datasetId && (<EthicsScan datasetId={datasetId} onComplete={handleEthicsComplete} />)}
        {activeStep === 3 && datasetId && (<EDAView datasetId={datasetId} onComplete={handleEdaComplete} />)}
        {activeStep === 4 && datasetId && (<StoryMode datasetId={datasetId} edaData={edaData} onComplete={handleStoryComplete} />)}
        {activeStep === 5 && datasetId && (
          <DecisionPoint 
            datasetId={datasetId} 
            story={story}
            onGenerateReport={handleGenerateReport}
            onContinueAnalysis={handleContinueAnalysis}
          />
        )}
        {activeStep === 6 && datasetId && (<ModelSelection datasetId={datasetId} onTrainingComplete={handleModelTrainingComplete} />)}
        {activeStep === 7 && datasetId && (<Dashboard datasetId={datasetId} />)}
      </Box>
    </Container>
  )
}

export default Workflow

