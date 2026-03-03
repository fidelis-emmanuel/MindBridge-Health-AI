"use client";

import { useState, useEffect } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "https://mindbridge-health-ai-production.up.railway.app";

type Patient = { id: number; patient_name: string };
type RiskFlag = { flag: string; level: "high" | "moderate" | "low"; note: string };
type ICD10 = { code: string; description: string };
type Medication = { name: string; dose: string; frequency: string };

type SoapNote = {
  soap_note_id: number;
  encounter_date: string;
  subjective: string | null;
  objective: string | null;
  assessment: string | null;
  plan: string | null;
  icd10_codes: ICD10[] | null;
  medications: Medication[] | null;
  risk_flags: RiskFlag[] | null;
  follow_up: string | null;
};

function RiskBadge({ flag }: { flag: RiskFlag }) {
  const styles: Record<string, string> = {
    high: "bg-red-100 text-red-700 border border-red-300",
    moderate: "bg-yellow-100 text-yellow-700 border border-yellow-300",
    low: "bg-blue-100 text-blue-700 border border-blue-300",
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${styles[flag.level] ?? styles.low}`}>
      ⚠ {flag.flag.replace(/_/g, " ")} · {flag.level}
      {flag.note && <span className="font-normal opacity-75"> — {flag.note}</span>}
    </span>
  );
}

export default function ScribePage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientId, setPatientId] = useState<string>("");
  const [provider, setProvider] = useState("");
  const [rawInput, setRawInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState<SoapNote | null>(null);

  useEffect(() => {
    fetch(`${API}/api/patients`)
      .then((r) => r.json())
      .then((d) => setPatients(d.patients ?? []));
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setNote(null);

    try {
      const res = await fetch(`${API}/scribe/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: Number(patientId),
          raw_input: rawInput,
          provider_name: provider,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? "Generation failed");
      }

      const data: SoapNote = await res.json();
      setNote(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center gap-3">
        <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center text-lg">📋</div>
        <div>
          <h1 className="font-bold text-lg leading-none">ClinicalScribe AI</h1>
          <p className="text-slate-400 text-xs">AI-powered SOAP note generation · MindBridge Health AI</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Demo banner */}
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-xl px-5 py-3 text-sm text-amber-700">
          <span className="font-semibold">Demo Environment</span> — All patient data is fictional. No real PHI is stored.
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* LEFT — Input panel */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Clinical Input</h2>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Patient</label>
                <select
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  required
                  className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a patient…</option>
                  {patients.map((p) => (
                    <option key={p.id} value={p.id}>{p.patient_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Provider Name</label>
                <input
                  type="text"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  placeholder="Dr. Sarah Chen"
                  required
                  className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Raw Clinical Notes / Voice Transcript
                </label>
                <textarea
                  value={rawInput}
                  onChange={(e) => setRawInput(e.target.value)}
                  placeholder="Paste voice transcript or typed notes here…&#10;&#10;Example: Patient reports feeling hopeless for the past 2 weeks, difficulty sleeping, decreased appetite. Denies SI. Currently on Sertraline 100mg but admits missing doses this week. Affect flat, speech slow. PHQ-9 score 16. Plan to increase Sertraline to 150mg and refer to therapy."
                  required
                  rows={12}
                  className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono"
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-xl transition-colors"
              >
                {loading ? "Generating SOAP Note…" : "Generate SOAP Note"}
              </button>
            </form>
          </div>

          {/* RIGHT — Output panel */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Generated SOAP Note</h2>

            {!note && !loading && (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm py-20">
                SOAP note will appear here after generation.
              </div>
            )}

            {loading && (
              <div className="h-full flex items-center justify-center text-blue-600 text-sm py-20 animate-pulse">
                ClinicalScribe AI is generating your note…
              </div>
            )}

            {note && (
              <div className="space-y-4">
                {/* Saved confirmation */}
                <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-2 text-sm text-green-700 font-medium">
                  ✓ Note saved to patient record · ID #{note.soap_note_id}
                </div>

                {/* Risk flags — show first if any */}
                {note.risk_flags && note.risk_flags.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                    <p className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-2">Risk Flags</p>
                    <div className="flex flex-wrap gap-2">
                      {note.risk_flags.map((f, i) => <RiskBadge key={i} flag={f} />)}
                    </div>
                  </div>
                )}

                {/* SOAP sections */}
                {(["subjective", "objective", "assessment", "plan"] as const).map((section) => (
                  <div key={section} className="border border-slate-200 rounded-xl p-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                      {section.charAt(0).toUpperCase()} — {section}
                    </p>
                    <p className="text-sm text-slate-800">{note[section] ?? <span className="text-slate-400 italic">Not documented</span>}</p>
                  </div>
                ))}

                {/* ICD-10 codes */}
                {note.icd10_codes && note.icd10_codes.length > 0 && (
                  <div className="border border-slate-200 rounded-xl p-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">ICD-10 Codes</p>
                    <div className="flex flex-wrap gap-2">
                      {note.icd10_codes.map((c, i) => (
                        <span key={i} className="bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full text-xs font-semibold">
                          {c.code} · {c.description}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Medications */}
                {note.medications && note.medications.length > 0 && (
                  <div className="border border-slate-200 rounded-xl p-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Medications</p>
                    <ul className="space-y-1">
                      {note.medications.map((m, i) => (
                        <li key={i} className="text-sm text-slate-700">
                          <span className="font-medium">{m.name}</span> {m.dose} · {m.frequency}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Follow-up */}
                {note.follow_up && (
                  <div className="border border-slate-200 rounded-xl p-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Follow-Up</p>
                    <p className="text-sm text-slate-800">{note.follow_up}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
