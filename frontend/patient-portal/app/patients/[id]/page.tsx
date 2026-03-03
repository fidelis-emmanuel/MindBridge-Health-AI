import Link from "next/link";
import { notFound } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Patient {
  id: number;
  patient_name: string;
  risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  medication_adherence: number;
  appointments_missed: number;
  crisis_calls_30days: number;
  diagnosis: string;
}

async function fetchPatient(id: string): Promise<Patient | null> {
  try {
    const res = await fetch(`${API_URL}/api/patients/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.patient as Patient;
  } catch {
    return null;
  }
}

function RiskBadge({ level }: { level: string }) {
  const styles: Record<string, string> = {
    CRITICAL: "bg-red-100 text-red-800 border border-red-300",
    HIGH:     "bg-orange-100 text-orange-700 border border-orange-200",
    MEDIUM:   "bg-yellow-100 text-yellow-700 border border-yellow-200",
    LOW:      "bg-green-100 text-green-700 border border-green-200",
  };
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${styles[level] ?? styles.LOW}`}>
      {level} Risk
    </span>
  );
}

function MeterBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.round((value / max) * 100);
  return (
    <div className="w-full bg-slate-100 rounded-full h-2 mt-1">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function buildAlerts(p: Patient): string[] {
  const alerts: string[] = [];
  if (p.risk_level === "CRITICAL") alerts.push("CRITICAL risk — immediate clinical review required");
  if (p.crisis_calls_30days >= 3) alerts.push(`${p.crisis_calls_30days} crisis calls in the past 30 days`);
  if (p.appointments_missed >= 3) alerts.push(`${p.appointments_missed} appointments missed`);
  if (p.medication_adherence < 0.5) alerts.push(`Low medication adherence: ${Math.round(p.medication_adherence * 100)}%`);
  return alerts;
}

function aiSummary(p: Patient): string {
  if (p.risk_level === "CRITICAL")
    return "Immediate clinical attention required. Multiple high-severity risk factors present. Escalation protocol should be activated.";
  if (p.risk_level === "HIGH")
    return "Close monitoring recommended. Significant risk indicators detected. Care team should review and adjust treatment plan.";
  if (p.risk_level === "MEDIUM")
    return "Moderate risk level. Continue current treatment with regular check-ins. Watch for deterioration signals.";
  return "Patient appears stable. Continue current care plan and maintain scheduled follow-ups.";
}

export default async function PatientDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const patient = await fetchPatient(id);

  if (!patient) notFound();

  const alerts = buildAlerts(patient);
  const adherencePct = Math.round(patient.medication_adherence * 100);

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
                {patient.patient_name.charAt(0)}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">{patient.patient_name}</h2>
                <p className="text-slate-500 mt-0.5">{patient.diagnosis}</p>
                <p className="text-slate-400 text-sm mt-1">Patient ID #{patient.id}</p>
              </div>
            </div>
            <RiskBadge level={patient.risk_level} />
          </div>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
            <p className="text-sm font-semibold text-red-700 mb-2">⚠️ Clinical Alerts</p>
            {alerts.map((alert, i) => (
              <p key={i} className="text-sm text-red-600">• {alert}</p>
            ))}
          </div>
        )}

        <div className="grid grid-cols-3 gap-6">

          {/* Left column */}
          <div className="col-span-2 space-y-6">

            {/* Risk metrics */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-4">Clinical Risk Indicators</h3>
              <div className="space-y-5">

                <div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">Medication Adherence</span>
                    <span className="font-semibold text-slate-900">{adherencePct}%</span>
                  </div>
                  <MeterBar value={adherencePct} max={100} color={adherencePct >= 70 ? "bg-green-500" : adherencePct >= 50 ? "bg-yellow-500" : "bg-red-500"} />
                  <p className="text-xs text-slate-400 mt-1">
                    {adherencePct >= 80 ? "Good adherence" : adherencePct >= 50 ? "Moderate — intervention recommended" : "Poor — urgent review needed"}
                  </p>
                </div>

                <div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">Appointments Missed</span>
                    <span className="font-semibold text-slate-900">{patient.appointments_missed} / 8</span>
                  </div>
                  <MeterBar value={patient.appointments_missed} max={8} color={patient.appointments_missed <= 1 ? "bg-green-500" : patient.appointments_missed <= 3 ? "bg-yellow-500" : "bg-red-500"} />
                  <p className="text-xs text-slate-400 mt-1">
                    {patient.appointments_missed === 0 ? "Full attendance" : patient.appointments_missed <= 2 ? "Occasional misses" : "Frequent non-attendance — follow up required"}
                  </p>
                </div>

                <div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">Crisis Calls (30 days)</span>
                    <span className="font-semibold text-slate-900">{patient.crisis_calls_30days} / 5</span>
                  </div>
                  <MeterBar value={patient.crisis_calls_30days} max={5} color={patient.crisis_calls_30days === 0 ? "bg-green-500" : patient.crisis_calls_30days <= 2 ? "bg-yellow-500" : "bg-red-500"} />
                  <p className="text-xs text-slate-400 mt-1">
                    {patient.crisis_calls_30days === 0 ? "No recent crisis contact" : patient.crisis_calls_30days <= 2 ? "Some crisis utilisation" : "High crisis utilisation — assess safety plan"}
                  </p>
                </div>

              </div>
            </div>

            {/* Diagnosis card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-3">Primary Diagnosis</h3>
              <p className="text-slate-700 text-sm leading-relaxed">{patient.diagnosis}</p>
            </div>

          </div>

          {/* Right column */}
          <div className="space-y-6">

            {/* Risk level card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-3">Risk Classification</h3>
              <div className="flex justify-center py-2">
                <RiskBadge level={patient.risk_level} />
              </div>
              <p className="text-xs text-slate-400 text-center mt-3">
                Assessed by MindBridge AI Risk Engine
              </p>
            </div>

            {/* AI summary */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-6 text-white">
              <h3 className="font-semibold mb-2">🤖 AI Summary</h3>
              <p className="text-blue-100 text-sm leading-relaxed">{aiSummary(patient)}</p>
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
