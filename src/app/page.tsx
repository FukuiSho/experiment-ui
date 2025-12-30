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

  const sessionStartRef = React.useRef<{ phase: ExperimentPhase; startTime: number } | null>(null);
  const dataRef = React.useRef<ExperimentData>(data);

  useEffect(() => {
    setMounted(true);
    // Randomize condition on client-side mount
    const condition: Condition = Math.random() > 0.5 ? 'P' : 'G';
    setData(prev => ({ ...prev, condition }));
    console.log(`Experiment Condition Assigned: ${condition}`);
  }, []);

  useEffect(() => {
    dataRef.current = data;
  }, [data]);

  useEffect(() => {
    if (phase.startsWith('SESSION_')) {
      // Track the first time we enter this session phase.
      if (!sessionStartRef.current || sessionStartRef.current.phase !== phase) {
        sessionStartRef.current = { phase, startTime: Date.now() };
      }
    } else {
      sessionStartRef.current = null;
    }
  }, [phase]);

  const handlePhaseComplete = (phaseData?: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
    const currentPhaseIndex = EXPERIMENT_PHASES.indexOf(phase);

    // Save data from current phase
    if (phase.startsWith('SESSION_') && phaseData?.messages) {
      const endTime = Date.now();
      const startTimeFromRef = sessionStartRef.current?.phase === phase ? sessionStartRef.current.startTime : undefined;
      const startTimeFromMessages = Array.isArray(phaseData.messages) && phaseData.messages.length > 0
        ? Math.min(...phaseData.messages.map((m: any) => (typeof m?.timestamp === 'number' ? m.timestamp : endTime)))
        : undefined;
      const startTime = startTimeFromRef ?? startTimeFromMessages ?? endTime;
      const duration = Math.max(0, endTime - startTime);

      setData(prev => ({
        ...prev,
        sessions: {
          ...prev.sessions,
          [phase]: {
            messages: phaseData.messages,
            startTime,
            endTime,
            duration
          }
        }
      }));

      // Clear timing for safety; next session will re-init.
      sessionStartRef.current = null;
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
      const nextPhase = EXPERIMENT_PHASES[currentPhaseIndex + 1];

      // Pre-seed timing for the next session phase synchronously.
      if (nextPhase.startsWith('SESSION_')) {
        sessionStartRef.current = { phase: nextPhase, startTime: Date.now() };
      }

      setPhase(nextPhase);
    }
  };

  const handleDownload = () => {
    const finalData = {
      ...dataRef.current,
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
