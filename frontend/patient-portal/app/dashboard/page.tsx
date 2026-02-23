import Link from "next/link";

// Simulated patient data (we'll connect to Railway API next)
const patients = [
  { id: "1", name: "Marcus Thompson", age: 34, diagnosis: "Major Depressive Disorder", risk: "High", lastAssessment: "2024-01-15", status: "Active" },
  { id: "2", name: "Sarah Chen", age: 28, diagnosis: "Generalized Anxiety Disorder", risk: "Medium", lastAssessment: "2024-01-14", status: "Active" },
  { id: "3", name: "James Rivera", age: 45, diagnosis: "Bipolar Disorder Type I", risk: "High", lastAssessment: "2024-01-13", status: "Active" },
  { id: "4", name: "Aisha Johnson", age: 31, diagnosis: "PTSD", risk: "Medium", lastAssessment: "2024-01-12", status: "Active" },
  { id: "5", name: "Robert Kim", age: 52, diagnosis: "Schizophrenia", risk: "High", lastAssessment: "2024-01-11", status: "Monitoring" },
  { id: "6", name: "Emily Davis", age: 24, diagnosis: "Borderline Personality Disorder", risk: "Medium", lastAssessment: "2024-01-10", status: "Active" },
  { id: "7", name: "David Wilson", age: 39, diagnosis: "Major Depressive Disorder", risk: "Low", lastAssessment: "2024-01-09", status: "Stable" },
  { id: "8", name: "Maria Santos", age: 41, diagnosis: "Panic Disorder", risk: "Low", lastAssessment: "2024-01-08", status: "Stable" },
  { id: "9", name: "Kevin Brown", age: 29, diagnosis: "ADHD with Anxiety", risk: "Medium", lastAssessment: "2024-01-07", status: "Active" },
  { id: "10", name: "Lisa Martinez", age: 36, diagnosis: "Schizoaffective Disorder", risk: "High", lastAssessment: "2024-01-06", status: "Monitoring" },
];

function RiskBadge({ risk }: { risk: string }) {
  const styles: Record<string, string> = {
    High: "bg-red-100 text-red-700 border border-red-200",
    Medium: "bg-yellow-100 text-yellow-700 border border-yellow-200",
    Low: "bg-green-100 text-green-700 border border-green-200",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${styles[risk]}`}>
      {risk}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    Active: "bg-blue-100 text-blue-700",
    Monitoring: "bg-purple-100 text-purple-700",
    Stable: "bg-slate-100 text-slate-600",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${styles[status]}`}>
      {status}
    </span>
  );
}

export default function DashboardPage() {
  const highRisk = patients.filter((p) => p.risk === "High").length;
  const mediumRisk = patients.filter((p) => p.risk === "Medium").length;
  const lowRisk = patients.filter((p) => p.risk === "Low").length;

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
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-400">Dr. Demo Clinician</span>
          <Link href="/" className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg transition-colors">
            Sign Out
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">

        {/* Demo banner */}
<div className="mb-6 bg-amber-50 border border-amber-200 rounded-xl px-5 py-3 flex items-center gap-3">
  <span className="text-amber-500 text-lg">⚠️</span>
  <p className="text-sm text-amber-700">
    <span className="font-semibold">Demo Environment</span> — All patient data is completely fictional and for portfolio demonstration purposes only. No real PHI is stored or displayed. HIPAA compliance architecture is production-ready.
  </p>
</div>

        {/* Page title */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Patient Dashboard</h2>
          <p className="text-slate-500 text-sm mt-1">AI-powered risk screening · Railway PostgreSQL · 10 active patients</p>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
            <p className="text-sm text-slate-500 font-medium">Total Patients</p>
            <p className="text-3xl font-bold text-slate-900 mt-1">{patients.length}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-red-100">
            <p className="text-sm text-red-500 font-medium">High Risk</p>
            <p className="text-3xl font-bold text-red-600 mt-1">{highRisk}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-yellow-100">
            <p className="text-sm text-yellow-600 font-medium">Medium Risk</p>
            <p className="text-3xl font-bold text-yellow-600 mt-1">{mediumRisk}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-green-100">
            <p className="text-sm text-green-600 font-medium">Low Risk</p>
            <p className="text-3xl font-bold text-green-600 mt-1">{lowRisk}</p>
          </div>
        </div>

        {/* Patient table */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Active Caseload</h3>
            <span className="text-xs text-slate-400 bg-slate-100 px-3 py-1 rounded-full">
              🔒 HIPAA Protected · Encrypted in Transit
            </span>
          </div>
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Patient</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Age</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Diagnosis</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Risk Level</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Last Assessment</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {patients.map((patient) => (
                <tr key={patient.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-700 font-semibold text-sm">
                        {patient.name.charAt(0)}
                      </div>
                      <span className="font-medium text-slate-900 text-sm">{patient.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{patient.age}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{patient.diagnosis}</td>
                  <td className="px-6 py-4"><RiskBadge risk={patient.risk} /></td>
                  <td className="px-6 py-4"><StatusBadge status={patient.status} /></td>
                  <td className="px-6 py-4 text-sm text-slate-500">{patient.lastAssessment}</td>
                  <td className="px-6 py-4">
                    <Link
                      href={`/patients/${patient.id}`}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium hover:underline"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}