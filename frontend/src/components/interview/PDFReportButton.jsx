import React, { useState } from 'react';
import { Download, CheckCircle, FileText, Loader2 } from 'lucide-react';
import { Button } from '../common/Button';
import { pdfService } from '../../utils/apiService';
import confetti from 'canvas-confetti';

export const PDFReportButton = ({ reportData, elementId = "interview-report-content" }) => {
  const [downloading, setDownloading] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const success = await pdfService.generateReportPDF(elementId, reportData);
      if (success) {
        setDownloaded(true);
        confetti({
          particleCount: 80,
          spread: 60,
          origin: { y: 0.8 },
          colors: ['#ff806b', '#38bdf8', '#34d399']
        });
        setTimeout(() => setDownloaded(false), 4000);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Button
      variant="primary"
      size="lg"
      onClick={handleDownload}
      disabled={downloading}
      className="shadow-glow-coral gap-2 w-full sm:w-auto"
    >
      {downloading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Generating Official PDF...</span>
        </>
      ) : downloaded ? (
        <>
          <CheckCircle className="w-5 h-5 text-navy-950" />
          <span>Report Downloaded!</span>
        </>
      ) : (
        <>
          <Download className="w-5 h-5" />
          <span>Download Interview Report PDF</span>
        </>
      )}
    </Button>
  );
};
