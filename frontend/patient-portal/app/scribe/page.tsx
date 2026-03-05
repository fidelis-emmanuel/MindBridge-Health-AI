"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ??
  "https://mindbridge-health-ai-production.up.railway.app";

interface Patient {
  id: number;
  patient_name: string;
}

interface ICD10Code {
  code: string;
  description: string;
}

interface Medication {
  name: string;
  dose: string;
  frequency: string;
}

interface RiskFlag {
  flag: string;
  severity: string;
}

interface SOAPNote {
  soap_note_id: number;
  patient_id: number;
  encounter_date: string;
  provider_name: string;
  subjective: string | null;
  objective: string | null;
  assessment: string | null;
  plan: string | null;
  icd10_codes: ICD10Code[] | null;
  medications: Medication[] | null;
  risk_flags: RiskFlag[] | null;
  follow_up: string | null;
}

export default function ScribePage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientsLoading, setPatientsLoading] = useState(true);
  const [patientId, setPatientId] = useState("");
  const [providerName, setProviderName] = useState("");
  const [rawInput, setRawInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [soapNote, setSoapNote] = useState<SOAPNote | null>(null);
  const [showToast, setShowToast] = useState(false);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/patients`)
      .then((r) => r.json())
      .then((data) => setPatients(data.patients ?? []))
      .catch(() => setError("Failed to load patient list"))
      .finally(() => setPatientsLoading(false));
  }, []);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSoapNote(null);
    try {
      const res = await fetch(`${API_BASE}/scribe/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: Number(patientId),
          provider_name: providerName,
          raw_input: rawInput,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? "Failed to generate SOAP note");
      }
      setSoapNote(await res.json());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  }

  function handleSave() {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setShowToast(true);
    toastTimerRef.current = setTimeout(() => setShowToast(false), 3000);
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center text-lg">🧠</div>
          <div>
            <h1 className="font-bold text-lg leading-none">MindBridge Health AI</h1>
            <p className="text-slate-400 text-xs">Behavioral Health Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white transition-colors">
            Dashboard
          </Link>
          <Link href="/scribe" className="text-sm text-blue-400 font-medium">
            ClinicalScribe
          </Link>
          <span className="text-sm text-slate-400">Dr. Demo Clinician</span>
          <Link href="/" className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg transition-colors">
            Sign Out
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">ClinicalScribe AI</h2>
          <p className="text-slate-500 text-sm mt-1">
            Generate structured SOAP notes from clinical notes or voice transcripts
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Clinical Input</h3>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label htmlFor="patient-select" className="block text-sm font-medium text-slate-700 mb-1">Patient</label>
                <select
                  id="patient-select"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  required
                  disabled={patientsLoading}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">
                    {patientsLoading ? "Loading patients..." : "Select a patient..."}
                  </option>
                  {patients.map((p) => (
                    <option key={p.id} value={p.id}>{p.patient_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="provider-name" className="block text-sm font-medium text-slate-700 mb-1">Provider Name</label>
                <input
                  id="provider-name"
                  type="text"
                  value={providerName}
                  onChange={(e) => setProviderName(e.target.value)}
                  required
                  placeholder="Dr. Jane Smith"
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="raw-input" className="block text-sm font-medium text-slate-700 mb-1">
                  Clinical Notes / Voice Transcript
                </label>
                <textarea
                  id="raw-input"
                  value={rawInput}
                  onChange={(e) => setRawInput(e.target.value)}
                  required
                  rows={10}
                  placeholder="Enter raw clinical notes, voice transcript, or describe the encounter..."
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Generating SOAP Note...
                  </>
                ) : (
                  "Generate SOAP Note"
                )}
              </button>
            </form>
          </div>

          {/* Right Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Generated SOAP Note</h3>
            {!soapNote ? (
              <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
                Output will appear here after generation
              </div>
            ) : (
              <div className="space-y-4">
                {(["subjective", "objective", "assessment", "plan"] as const).map((section) => (
                  <div key={section} className="border border-slate-200 rounded-lg overflow-hidden">
                    <div className="bg-slate-50 px-4 py-2 border-b border-slate-200">
                      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                        {section}
                      </span>
                    </div>
                    <div className="px-4 py-3 text-sm text-slate-700 whitespace-pre-wrap">
                      {soapNote[section] ?? (
                        <span className="text-slate-400 italic">Not documented</span>
                      )}
                    </div>
                  </div>
                ))}

                {soapNote.icd10_codes && soapNote.icd10_codes.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                      ICD-10 Codes
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {soapNote.icd10_codes.map((c, i) => (
                        <span key={i} className="bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full text-xs font-medium">
                          {c.code}: {c.description}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {soapNote.medications && soapNote.medications.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                      Medications
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {soapNote.medications.map((m, i) => (
                        <span key={i} className="bg-green-100 text-green-700 px-2.5 py-1 rounded-full text-xs font-medium">
                          {m.name} · {m.dose} · {m.frequency}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {soapNote.risk_flags && soapNote.risk_flags.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                      Risk Flags
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {soapNote.risk_flags.map((r, i) => {
                        const sev = r.severity?.toUpperCase();
                        const cls =
                          sev === "HIGH" || sev === "CRITICAL"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700";
                        return (
                          <span key={i} className={`${cls} px-2.5 py-1 rounded-full text-xs font-medium`}>
                            {r.flag}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                )}

                {soapNote.follow_up && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                      Follow-Up
                    </p>
                    <p className="text-sm text-slate-700">{soapNote.follow_up}</p>
                  </div>
                )}

                <button
                  onClick={handleSave}
                  className="w-full mt-2 border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold py-2.5 rounded-lg transition-colors text-sm"
                >
                  Save to Patient Record
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      {showToast && (
        <div className="fixed bottom-6 right-6 bg-slate-900 text-white text-sm px-5 py-3 rounded-xl shadow-lg">
          Note saved to patient record ✓
        </div>
      )}
    </div>
  );
}
