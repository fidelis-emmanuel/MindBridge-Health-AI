"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "https://mindbridge-health-ai-production.up.railway.app";

type RiskLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

interface NewPatientForm {
  patient_name: string;
  diagnosis: string;
  risk_level: RiskLevel;
  medication_adherence: number;
  appointments_missed: number;
  crisis_calls_30days: number;
}

export default function NewPatientPage() {
  const router = useRouter();
  const [form, setForm] = useState<NewPatientForm>({
    patient_name: "",
    diagnosis: "",
    risk_level: "MEDIUM",
    medication_adherence: 1.0,
    appointments_missed: 0,
    crisis_calls_30days: 0,
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    if (!form.patient_name.trim() || !form.diagnosis.trim()) {
      setError("Patient name and diagnosis must not be blank.");
      setSubmitting(false);
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/patients`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(String(data.detail ?? "Failed to admit patient."));
        return;
      }
      router.push("/dashboard");
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
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
        <Link
          href="/dashboard"
          className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg transition-colors"
        >
          ← Back to Dashboard
        </Link>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-10">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Admit New Patient</h2>
          <p className="text-slate-500 text-sm mt-1">
            Enter clinical details to register a new patient in the system.
          </p>
        </div>

        {error && (
          <div role="alert" className="mb-5 bg-red-50 border border-red-200 rounded-xl px-5 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-5">
          <div>
            <label htmlFor="patient_name" className="block text-sm font-medium text-slate-700 mb-1">
              Patient Name <span aria-hidden="true" className="text-red-500">*</span>
            </label>
            <input
              id="patient_name"
              type="text"
              required
              value={form.patient_name}
              onChange={e => setForm(f => ({ ...f, patient_name: e.target.value }))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Full name"
            />
          </div>

          <div>
            <label htmlFor="diagnosis" className="block text-sm font-medium text-slate-700 mb-1">
              Diagnosis <span aria-hidden="true" className="text-red-500">*</span>
            </label>
            <input
              id="diagnosis"
              type="text"
              required
              value={form.diagnosis}
              onChange={e => setForm(f => ({ ...f, diagnosis: e.target.value }))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Primary diagnosis"
            />
          </div>

          <div>
            <label htmlFor="risk_level" className="block text-sm font-medium text-slate-700 mb-1">
              Risk Level <span aria-hidden="true" className="text-red-500">*</span>
            </label>
            <select
              id="risk_level"
              value={form.risk_level}
              onChange={e => setForm(f => ({ ...f, risk_level: e.target.value as RiskLevel }))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div>
            <label htmlFor="medication_adherence" className="block text-sm font-medium text-slate-700 mb-1">
              Medication Adherence — {(form.medication_adherence * 100).toFixed(0)}%
            </label>
            <input
              id="medication_adherence"
              type="range"
              min={0}
              max={100}
              step={1}
              value={Math.round(form.medication_adherence * 100)}
              onChange={e =>
                setForm(f => ({ ...f, medication_adherence: Number(e.target.value) / 100 }))
              }
              aria-label="Medication adherence percentage"
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="appointments_missed" className="block text-sm font-medium text-slate-700 mb-1">
                Missed Appointments
              </label>
              <input
                id="appointments_missed"
                type="number"
                min={0}
                value={form.appointments_missed}
                onChange={e =>
                  setForm(f => ({ ...f, appointments_missed: Number(e.target.value) }))
                }
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="crisis_calls_30days" className="block text-sm font-medium text-slate-700 mb-1">
                Crisis Calls (30 days)
              </label>
              <input
                id="crisis_calls_30days"
                type="number"
                min={0}
                value={form.crisis_calls_30days}
                onChange={e =>
                  setForm(f => ({ ...f, crisis_calls_30days: Number(e.target.value) }))
                }
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
          >
            {submitting ? "Admitting..." : "Admit Patient"}
          </button>
        </form>
      </main>
    </div>
  );
}
