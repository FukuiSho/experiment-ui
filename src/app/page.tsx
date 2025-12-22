"use client";

import React, { useState, useEffect } from 'react';
import { ExperimentFlow } from '@/components/ExperimentFlow';
import { ExperimentPhase, Condition, ExperimentData, EXPERIMENT_PHASES } from '@/lib/experiment-state';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [phase, setPhase] = useState<ExperimentPhase>('CONSENT');
  const [data, setData] = useState<ExperimentData>({
    condition: 'G', // Default, will be randomized
    startTime: Date.now(),
    sessions: {}
  });

  useEffect(() => {
    setMounted(true);
    // Randomize condition on client-side mount
    const condition: Condition = Math.random() > 0.5 ? 'P' : 'G';
    setData(prev => ({ ...prev, condition }));
    console.log(`Experiment Condition Assigned: ${condition}`);
  }, []);

  const handlePhaseComplete = (phaseData?: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
    const currentPhaseIndex = EXPERIMENT_PHASES.indexOf(phase);

    // Save data from current phase
    if (phase.startsWith('SESSION_') && phaseData?.messages) {
      setData(prev => ({
        ...prev,
        sessions: {
          ...prev.sessions,
          [phase]: {
            messages: phaseData.messages,
            duration: 0 // TODO: Calculate duration
          }
        }
      }));
    } else if (phase === 'EVALUATION' && phaseData) {
      setData(prev => ({
        ...prev,
        evaluation: phaseData
      }));
    } else if (phase === 'DEBRIEFING') {
      handleDownload();
      return;
    }

    // Move to next phase
    if (currentPhaseIndex < EXPERIMENT_PHASES.length - 1) {
      setPhase(EXPERIMENT_PHASES[currentPhaseIndex + 1]);
    }
  };

  const handleDownload = () => {
    const finalData = {
      ...data,
      endTime: Date.now()
    };
    const blob = new Blob([JSON.stringify(finalData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `experiment_data_${finalData.condition}_${finalData.startTime}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!mounted) return null;

  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-blue-50">
      <div className="w-full max-w-5xl">
        <ExperimentFlow
          phase={phase}
          condition={data.condition}
          onPhaseComplete={handlePhaseComplete}
        />
      </div>

      {/* Debug Info (Hidden in production or remove) */}
      <div className="fixed bottom-2 right-2 text-xs text-gray-300 pointer-events-none">
        Condition: {data.condition} | Phase: {phase}
      </div>
    </main>
  );
}
