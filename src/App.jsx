import React, { useState, useEffect } from 'react';
import { 
  Pill, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  Plus, 
  Search, 
  LogOut, 
  FileSpreadsheet,
  Trash2,
  Edit2,
  User,
  ShieldCheck,
  Bell
} from 'lucide-react';

export default function App() {
  const [user, setUser] = useState({ name: 'Harshi Ranka', email: 'harshi@example.com' });
  const [activeTab, setActiveTab] = useState('overview'); // overview, medicines, schedule, history
  const [medicines, setMedicines] = useState([
    { id: 1, name: 'Paracetamol', dosage: '500mg', frequency: 'Daily', time: '08:00', startDate: '2026-07-01', instructions: 'Take after breakfast' },
    { id: 2, name: 'Amoxicillin', dosage: '250mg', frequency: 'Twice Daily', time: '14:00', startDate: '2026-07-15', instructions: 'Drink full glass of water' },
    { id: 3, name: 'Vitamin D3', dosage: '1000 IU', frequency: 'Daily', time: '20:00', startDate: '2026-06-01', instructions: 'Take with evening meal' }
  ]);
  
  const [logs, setLogs] = useState([
    { id: 101, medicineId: 1, name: 'Paracetamol', dosage: '500mg', date: '2026-07-29', time: '08:00', status: 'TAKEN', markedAt: '08:05 AM', notes: 'Taken on time' },
    { id: 102, medicineId: 2, name: 'Amoxicillin', dosage: '250mg', date: '2026-07-29', time: '14:00', status: 'PENDING', markedAt: null, notes: '' },
    { id: 103, medicineId: 3, name: 'Vitamin D3', dosage: '1000 IU', date: '2026-07-29', time: '20:00', status: 'PENDING', markedAt: null, notes: '' }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMed, setEditingMed] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    dosage: '',
    frequency: 'Daily',
    time: '08:00',
    startDate: new Date().toISOString().split('T')[0],
    instructions: ''
  });

  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  const totalTaken = logs.filter(l => l.status === 'TAKEN').length;
  const totalMissed = logs.filter(l => l.status === 'MISSED').length;
  const totalLogs = logs.length;
  const adherenceRate = totalLogs > 0 ? Math.round((totalTaken / totalLogs) * 100) : 100;

  const handleOpenModal = (med = null) => {
    if (med) {
      setEditingMed(med);
      setFormData(med);
    } else {
      setEditingMed(null);
      setFormData({
        name: '',
        dosage: '',
        frequency: 'Daily',
        time: '08:00',
        startDate: new Date().toISOString().split('T')[0],
        instructions: ''
      });
    }
    setIsModalOpen(true);
  };

  const handleSaveMedicine = (e) => {
    e.preventDefault();
    if (editingMed) {
      setMedicines(medicines.map(m => m.id === editingMed.id ? { ...formData, id: editingMed.id } : m));
    } else {
      const newMed = { ...formData, id: Date.now() };
      setMedicines([...medicines, newMed]);
      setLogs([...logs, {
        id: Date.now() + 1,
        medicineId: newMed.id,
        name: newMed.name,
        dosage: newMed.dosage,
        date: new Date().toISOString().split('T')[0],
        time: newMed.time,
        status: 'PENDING',
        markedAt: null,
        notes: ''
      }]);
    }
    setIsModalOpen(false);
  };

  const handleDeleteMedicine = (id) => {
    setMedicines(medicines.filter(m => m.id !== id));
    setLogs(logs.filter(l => l.medicineId !== id));
  };

  const handleUpdateLogStatus = (logId, status) => {
    setLogs(logs.map(l => l.id === logId ? {
      ...l,
      status,
      markedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } : l));
  };

  const filteredMedicines = medicines.filter(m => 
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    m.dosage.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800/80 flex flex-col p-6 space-y-8">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
            <Pill className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight bg-gradient-to-r from-blue-400 to-sky-300 bg-clip-text text-transparent">MediRemind</h1>
            <p className="text-xs text-slate-400">Health Tracker</p>
          </div>
        </div>

        <div className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-xl border border-slate-700/50">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-sky-400 flex items-center justify-center font-bold text-white shadow-md">
            {user.name.charAt(0)}
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold truncate">{user.name}</p>
            <p className="text-xs text-slate-400 flex items-center space-x-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400 inline" />
              <span>Active User</span>
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          {[
            { id: 'overview', label: 'Overview', icon: Calendar },
            { id: 'medicines', label: 'Medicines', icon: Pill },
            { id: 'schedule', label: 'Daily Schedule', icon: Clock },
            { id: 'history', label: 'History & Reports', icon: TrendingUp }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' 
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        <button className="flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium text-rose-400 bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 transition-all">
          <LogOut className="w-5 h-5" />
          <span>Log Out</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-y-auto">
        {/* Top Header */}
        <header className="sticky top-0 z-10 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/80 px-8 py-5 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-100 capitalize">{activeTab} Dashboard</h2>
            <p className="text-xs text-slate-400">Track and manage your daily medication regimen</p>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl text-xs font-semibold text-sky-400">
              <Clock className="w-4 h-4 text-sky-400" />
              <span>{currentTime}</span>
            </div>
            <button
              onClick={() => handleOpenModal()}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all shadow-lg shadow-blue-600/20"
            >
              <Plus className="w-4 h-4" />
              <span>Add Medicine</span>
            </button>
          </div>
        </header>

        {/* Dynamic Content Views */}
        <div className="p-8 max-w-7xl mx-auto w-full space-y-8">
          {/* Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div className="bg-slate-900/90 border border-slate-800/80 p-5 rounded-2xl flex items-center space-x-4 shadow-lg">
              <div className="p-3 bg-blue-500/15 text-blue-400 rounded-xl">
                <Pill className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Medicines</p>
                <p className="text-2xl font-extrabold text-slate-100 mt-1">{medicines.length}</p>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800/80 p-5 rounded-2xl flex items-center space-x-4 shadow-lg">
              <div className="p-3 bg-emerald-500/15 text-emerald-400 rounded-xl">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Taken Today</p>
                <p className="text-2xl font-extrabold text-slate-100 mt-1">{totalTaken}</p>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800/80 p-5 rounded-2xl flex items-center space-x-4 shadow-lg">
              <div className="p-3 bg-rose-500/15 text-rose-400 rounded-xl">
                <XCircle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Missed Today</p>
                <p className="text-2xl font-extrabold text-slate-100 mt-1">{totalMissed}</p>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800/80 p-5 rounded-2xl flex items-center space-x-4 shadow-lg">
              <div className="p-3 bg-amber-500/15 text-amber-400 rounded-xl">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Adherence Rate</p>
                <p className="text-2xl font-extrabold text-slate-100 mt-1">{adherenceRate}%</p>
              </div>
            </div>
          </div>

          {/* Overview View */}
          {activeTab === 'overview' && (
            <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 className="text-lg font-bold flex items-center space-x-2">
                  <Bell className="w-5 h-5 text-blue-400" />
                  <span>Today's Dose Reminders</span>
                </h3>
                <button onClick={() => setActiveTab('schedule')} className="text-xs text-blue-400 hover:text-blue-300 font-semibold">
                  View Full Schedule →
                </button>
              </div>

              <div className="space-y-4">
                {logs.map(log => (
                  <div key={log.id} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 flex items-center justify-between hover:border-slate-700 transition-all">
                    <div className="flex items-center space-x-4">
                      <div className="text-lg font-black text-sky-400 font-mono bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
                        {log.time}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-100 text-base">{log.name}</h4>
                        <p className="text-xs text-slate-400 mt-0.5">Dosage: {log.dosage}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${
                        log.status === 'TAKEN' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                        log.status === 'MISSED' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                        'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}>
                        {log.status}
                      </span>
                      <button 
                        onClick={() => handleUpdateLogStatus(log.id, 'TAKEN')}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition-all"
                      >
                        Taken
                      </button>
                      <button 
                        onClick={() => handleUpdateLogStatus(log.id, 'MISSED')}
                        className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition-all"
                      >
                        Missed
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Medicines View */}
          {activeTab === 'medicines' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between bg-slate-900/90 border border-slate-800/80 p-4 rounded-2xl">
                <div className="relative flex-1 max-w-md">
                  <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search medicines by name or dosage..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 pl-10 pr-4 py-2 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {filteredMedicines.map(med => (
                  <div key={med.id} className="bg-slate-900/90 border border-slate-800/80 p-6 rounded-2xl space-y-4 hover:border-blue-500/50 transition-all relative overflow-hidden shadow-lg">
                    <div className="w-1.5 h-full bg-blue-500 absolute left-0 top-0"></div>
                    <div className="flex justify-between items-start pl-2">
                      <div>
                        <h3 className="font-bold text-lg text-slate-100">{med.name}</h3>
                        <p className="text-xs text-sky-400 font-semibold mt-0.5">💊 {med.dosage}</p>
                      </div>
                      <span className="text-xs px-2.5 py-1 bg-slate-800 text-slate-300 rounded-lg font-semibold border border-slate-700">
                        {med.frequency}
                      </span>
                    </div>

                    <div className="pl-2 space-y-1.5 text-xs text-slate-400">
                      <p>⏰ Time: <span className="text-slate-200 font-medium">{med.time}</span></p>
                      <p>📅 Started: <span className="text-slate-200 font-medium">{med.startDate}</span></p>
                      {med.instructions && <p className="italic text-slate-400">"{med.instructions}"</p>}
                    </div>

                    <div className="pt-2 flex space-x-2 pl-2">
                      <button 
                        onClick={() => handleOpenModal(med)}
                        className="flex-1 flex items-center justify-center space-x-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                        <span>Edit</span>
                      </button>
                      <button 
                        onClick={() => handleDeleteMedicine(med.id)}
                        className="flex-1 flex items-center justify-center space-x-1 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold rounded-lg border border-rose-500/20 transition-all"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Schedule View */}
          {activeTab === 'schedule' && (
            <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
              <h3 className="text-lg font-bold">Daily Dose Schedule</h3>
              <div className="space-y-4">
                {logs.map(log => (
                  <div key={log.id} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-xl font-bold text-sky-400 font-mono bg-slate-900 px-3.5 py-2 rounded-xl border border-slate-800">
                        {log.time}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-100 text-base">{log.name}</h4>
                        <p className="text-xs text-slate-400 mt-0.5">Dosage: {log.dosage}</p>
                      </div>
                    </div>
                    <div className="flex space-x-3">
                      <button 
                        onClick={() => handleUpdateLogStatus(log.id, 'TAKEN')}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20"
                      >
                        Mark Taken
                      </button>
                      <button 
                        onClick={() => handleUpdateLogStatus(log.id, 'MISSED')}
                        className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold shadow-md shadow-rose-600/20"
                      >
                        Mark Missed
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* History View */}
          {activeTab === 'history' && (
            <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 className="text-lg font-bold">Dose Log History</h3>
                <button className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-lg shadow-emerald-600/20">
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Export CSV Report</span>
                </button>
              </div>

              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-slate-950/60 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Date & Time</th>
                    <th className="py-3 px-4">Medicine</th>
                    <th className="py-3 px-4">Dosage</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Marked At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {logs.map(log => (
                    <tr key={log.id} className="hover:bg-slate-850/50 transition-all">
                      <td className="py-3 px-4">{log.date} {log.time}</td>
                      <td className="py-3 px-4 font-bold text-slate-100">{log.name}</td>
                      <td className="py-3 px-4">{log.dosage}</td>
                      <td className="py-3 px-4">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-bold uppercase ${
                          log.status === 'TAKEN' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                        }`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">{log.markedAt || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Add / Edit Medicine Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-6 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-lg text-slate-100">{editingMed ? 'Edit Medicine' : 'Add New Medicine'}</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200 text-xl font-bold">&times;</button>
            </div>

            <form onSubmit={handleSaveMedicine} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Medicine Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Paracetamol"
                  className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Dosage *</label>
                  <input
                    type="text"
                    required
                    value={formData.dosage}
                    onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                    placeholder="e.g. 500mg"
                    className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Frequency *</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  >
                    <option value="Daily">Daily</option>
                    <option value="Twice Daily">Twice Daily</option>
                    <option value="Weekly">Weekly</option>
                    <option value="As Needed">As Needed</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Scheduled Time *</label>
                  <input
                    type="time"
                    required
                    value={formData.time}
                    onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Start Date *</label>
                  <input
                    type="date"
                    required
                    value={formData.startDate}
                    onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Special Instructions</label>
                <input
                  type="text"
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  placeholder="e.g. Take after meal"
                  className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-600/20"
                >
                  Save Medicine
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
