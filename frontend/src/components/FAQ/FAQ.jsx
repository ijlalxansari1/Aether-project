import React, { useEffect, useState } from 'react'
import { Container, Paper, Typography, Box, Accordion, AccordionSummary, AccordionDetails, Chip, Tooltip } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import axios from 'axios'

function FAQ() {
  const [faq, setFaq] = useState([])
  const [glossary, setGlossary] = useState([])

  useEffect(() => {
    const load = async () => {
      const f = await axios.get('/api/info/faq')
      const g = await axios.get('/api/info/glossary')
      setFaq(f.data.items || [])
      setGlossary(g.data.items || [])
    }
    load()
  }, [])

  const Glossary = () => (
    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
      {glossary.map((g, i) => (
        <Tooltip key={i} title={`${g.definition} — ${g.why}`} arrow>
          <Chip label={g.term} variant="outlined" />
        </Tooltip>
      ))}
    </Box>
  )

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 6 }}>
      <Typography variant="h4" fontWeight={800} gutterBottom>
        FAQ & Glossary
      </Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Glossary</Typography>
        <Glossary />
      </Paper>
      {faq.map((item, idx) => (
        <Accordion key={idx} defaultExpanded={idx === 0}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography fontWeight={700}>{item.q}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography sx={{ mb: 1 }}>{item.a}</Typography>
            {item.ethical && <Chip label={`Ethical: ${item.ethical}`} color="warning" variant="outlined" />}
          </AccordionDetails>
        </Accordion>
      ))}
    </Container>
  )
}

export default FAQ
