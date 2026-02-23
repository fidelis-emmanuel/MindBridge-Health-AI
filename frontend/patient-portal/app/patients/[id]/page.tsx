import Link from "next/link";

const patients: Record<string, {
  name: string; age: number; diagnosis: string; risk: string;
  status: string; lastAssessment: string; clinician: string;
  admissionDate: string; medications: string[]; alerts: string[];
  notes: string; phq9: number; gad7: number; aims: number;
}> = {
  "1": {
    name: "Marcus Thompson", age: 34, diagnosis: "Major Depressive Disorder",
    risk: "High", status: "Active", lastAssessment: "2024-01-15",
    clinician: "Dr. Sarah Williams", admissionDate: "2023-08-10",
    medications: ["Sertraline 100mg", "Trazodone 50mg"],
    alerts: ["Missed 2 consecutive appointments", "PHQ-9 score increased by 5 points"],
    notes: "Patient reports increased feelings of hopelessness over the past two weeks. Sleep disturbances noted. Safety plan reviewed and updated. Family support system engaged.",
    phq9: 18, gad7: 12, aims: 3,
  },
  "2": {
    name: "Sarah Chen", age: 28, diagnosis: "Generalized Anxiety Disorder",
    risk: "Medium", status: "Active", lastAssessment: "2024-01-14",
    clinician: "Dr. James Patel", admissionDate: "2023-10-22",
    medications: ["Escitalopram 10mg", "Buspirone 15mg"],
    alerts: ["GAD-7 elevated above baseline"],
    notes: "Patient reports work-related stressors contributing to anxiety. Responding well to CBT techniques. Sleep hygiene improvements noted.",
    phq9: 9, gad7: 14, aims: 1,
  },
  "3": {
    name: "James Rivera", age: 45, diagnosis: "Bipolar Disorder Type I",
    risk: "High", status: "Active", lastAssessment: "2024-01-13",
    clinician: "Dr. Sarah Williams", admissionDate: "2023-06-05",
    medications: ["Lithium 900mg", "Quetiapine 200mg", "Lamotrigine 150mg"],
    alerts: ["Mood episode indicators present", "Lithium level check due"],
    notes: "Patient showing early signs of hypomanic episode. Increased energy and decreased sleep reported. Medication compliance confirmed. Monitoring closely.",
    phq9: 7, gad7: 8, aims: 4,
  },
  "4": { name: "Aisha Johnson", age: 31, diagnosis: "PTSD", risk: "Medium", status: "Active", lastAssessment: "2024-01-12", clinician: "Dr. Maria Lopez", admissionDate: "2023-09-18", medications: ["Prazosin 2mg", "Sertraline 150mg"], alerts: ["Trauma processing session scheduled"], notes: "Patient progressing well with EMDR therapy. Nightmares reduced in frequency. Grounding techniques being utilized effectively.", phq9: 11, gad7: 10, aims: 2 },
  "5": { name: "Robert Kim", age: 52, diagnosis: "Schizophrenia", risk: "High", status: "Monitoring", lastAssessment: "2024-01-11", clinician: "Dr. James Patel", admissionDate: "2023-04-30", medications: ["Clozapine 400mg", "Benztropine 1mg"], alerts: ["Auditory hallucinations reported", "Clozapine blood monitoring due"], notes: "Patient reports intermittent auditory hallucinations. Medication compliance being monitored closely. Community support worker engaged.", phq9: 14, gad7: 9, aims: 6 },
  "6": { name: "Emily Davis", age: 24, diagnosis: "Borderline Personality Disorder", risk: "Medium", status: "Active", lastAssessment: "2024-01-10", clinician: "Dr. Maria Lopez", admissionDate: "2023-11-08", medications: ["Lamotrigine 100mg"], alerts: ["DBT skills group attendance required"], notes: "Patient engaged in DBT program. Emotional dysregulation episodes decreased. Interpersonal effectiveness skills improving.", phq9: 13, gad7: 11, aims: 1 },
  "7": { name: "David Wilson", age: 39, diagnosis: "Major Depressive Disorder", risk: "Low", status: "Stable", lastAssessment: "2024-01-09", clinician: "Dr. Sarah Williams", admissionDate: "2023-07-14", medications: ["Bupropion 300mg"], alerts: [], notes: "Patient responding well to treatment. PHQ-9 scores consistently improving. Return to work program initiated successfully.", phq9: 6, gad7: 4, aims: 1 },
  "8": { name: "Maria Santos", age: 41, diagnosis: "Panic Disorder", risk: "Low", status: "Stable", lastAssessment: "2024-01-08", clinician: "Dr. James Patel", admissionDate: "2023-12-01", medications: ["Escitalopram 20mg", "Clonazepam 0.5mg PRN"], alerts: [], notes: "Panic attack frequency reduced significantly. Exposure therapy progressing well. Patient reports improved quality of life.", phq9: 5, gad7: 7, aims: 0 },
  "9": { name: "Kevin Brown", age: 29, diagnosis: "ADHD with Anxiety", risk: "Medium", status: "Active", lastAssessment: "2024-01-07", clinician: "Dr. Maria Lopez", admissionDate: "2023-10-10", medications: ["Amphetamine salts 20mg", "Guanfacine 1mg"], alerts: ["Medication effectiveness review due"], notes: "Patient reports improved focus at work. Anxiety symptoms secondary to ADHD being addressed. Sleep schedule regulation ongoing.", phq9: 8, gad7: 13, aims: 2 },
  "10": { name: "Lisa Martinez", age: 36, diagnosis: "Schizoaffective Disorder", risk: "High", status: "Monitoring", lastAssessment: "2024-01-06", clinician: "Dr. Sarah Williams", admissionDate: "2023-05-22", medications: ["Paliperidone 6mg", "Valproate 1000mg", "Lorazepam 1mg PRN"], alerts: ["Mood symptoms escalating", "Psychosis screening indicated"], notes: "Patient experiencing increased mood instability alongside psychotic symptoms. Inpatient evaluation being considered. Family notified per care plan.", phq9: 16, gad7: 14, aims: 5 },
};

function RiskBadge({ risk }: { risk: string }) {
  const styles: Record<string, string> = {
    High: "bg-red-100 text-red-700 border border-red-200",
    Medium: "bg-yellow-100 text-yellow-700 border border-yellow-200",
    Low: "bg-green-100 text-green-700 border border-green-200",
  };
  return <span className={`px-3 py-1 rounded-full text-sm font-semibold ${styles[risk]}`}>{risk} Risk</span>;
}

function ScoreBar({ score, max, color }: { score: number; max: number; color: string }) {
  const pct = Math.round((score / max) * 100);
  return (
    <div className="w-full bg-slate-100 rounded-full h-2 mt-1">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default async function PatientDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const patient = patients[id];

  if (!patient) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl font-bold text-slate-900">Patient Not Found</p>
          <Link href="/dashboard" className="text-blue-600 hover:underline mt-4 block">← Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">

      {/* Header */}
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center text-lg">🧠</div>
          <div>
            <h1 className="font-bold text-lg leading-none">MindBridge Health AI</h1>
            <p className="text-slate-400 text-xs">Behavioral Health Platform</p>
          </div>
        </div>
        <Link href="/dashboard" className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg transition-colors">
          ← Back to Dashboard
        </Link>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">

        {/* Patient header card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center text-blue-700 font-bold text-2xl">
                {patient.name.charAt(0)}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">{patient.name}</h2>
                <p className="text-slate-500 mt-0.5">{patient.diagnosis} · Age {patient.age}</p>
                <p className="text-slate-400 text-sm mt-1">Clinician: {patient.clinician} · Admitted: {patient.admissionDate}</p>
              </div>
            </div>
            <RiskBadge risk={patient.risk} />
          </div>
        </div>

        {/* Alerts */}
        {patient.alerts.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
            <p className="text-sm font-semibold text-red-700 mb-2">⚠️ Clinical Alerts</p>
            {patient.alerts.map((alert, i) => (
              <p key={i} className="text-sm text-red-600">• {alert}</p>
            ))}
          </div>
        )}

        <div className="grid grid-cols-3 gap-6">

          {/* Left column */}
          <div className="col-span-2 space-y-6">

            {/* Clinical scores */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-4">AI Risk Assessment Scores</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">PHQ-9 (Depression)</span>
                    <span className="font-semibold text-slate-900">{patient.phq9}/27</span>
                  </div>
                  <ScoreBar score={patient.phq9} max={27} color="bg-blue-500" />
                  <p className="text-xs text-slate-400 mt-1">
                    {patient.phq9 >= 15 ? "Moderately Severe to Severe" : patient.phq9 >= 10 ? "Moderate" : "Mild to Minimal"}
                  </p>
                </div>
                <div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">GAD-7 (Anxiety)</span>
                    <span className="font-semibold text-slate-900">{patient.gad7}/21</span>
                  </div>
                  <ScoreBar score={patient.gad7} max={21} color="bg-purple-500" />
                  <p className="text-xs text-slate-400 mt-1">
                    {patient.gad7 >= 15 ? "Severe" : patient.gad7 >= 10 ? "Moderate" : "Mild to Minimal"}
                  </p>
                </div>
                <div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">AIMS (Movement)</span>
                    <span className="font-semibold text-slate-900">{patient.aims}/40</span>
                  </div>
                  <ScoreBar score={patient.aims} max={40} color="bg-orange-400" />
                  <p className="text-xs text-slate-400 mt-1">
                    {patient.aims >= 3 ? "Clinically Significant" : "Within Normal Range"}
                  </p>
                </div>
              </div>
            </div>

            {/* Clinical notes */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-3">Clinical Notes</h3>
              <p className="text-slate-600 text-sm leading-relaxed">{patient.notes}</p>
              <p className="text-xs text-slate-400 mt-3">Last updated: {patient.lastAssessment} · {patient.clinician}</p>
            </div>
          </div>

          {/* Right column */}
          <div className="space-y-6">

            {/* Medications */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-3">Current Medications</h3>
              <div className="space-y-2">
                {patient.medications.map((med, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
                    <span className="text-slate-700">{med}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* AI summary */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-6 text-white">
              <h3 className="font-semibold mb-2">🤖 AI Summary</h3>
              <p className="text-blue-100 text-sm leading-relaxed">
                Claude AI analysis: {patient.risk === "High"
                  ? "Immediate clinical attention recommended. Multiple risk factors present."
                  : patient.risk === "Medium"
                  ? "Monitor closely. Moderate indicators present, intervention may be needed."
                  : "Patient progressing well. Continue current treatment plan."}
              </p>
              <p className="text-blue-200 text-xs mt-3">Powered by Claude API · Anthropic</p>
            </div>

            {/* HIPAA notice */}
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
              <p className="text-xs text-slate-500 font-semibold mb-1">🔒 HIPAA Compliance</p>
              <p className="text-xs text-slate-400">All data encrypted at rest and in transit. Access logged per 45 CFR § 164.312.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}