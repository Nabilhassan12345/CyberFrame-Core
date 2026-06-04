import React, { useState, useEffect } from 'react';
import { Shield, Activity, Lock, AlertTriangle, Terminal, Settings, Globe, Database, Cpu, Plus } from 'lucide-react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [healthData, setHealthData] = useState({
    status: "Loading...",
    cpu_usage: 0,
    memory_usage: 0,
    active_endpoints: 0,
    network_health: 0,
    total_threats_blocked: 0
  });
  const [threatLogs, setThreatLogs] = useState([]);

  // Fetch real data from the Python FastAPI backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const healthRes = await fetch('http://localhost:8000/api/health');
        if (healthRes.ok) {
          setHealthData(await healthRes.json());
        }
        
        const threatsRes = await fetch('http://localhost:8000/api/threats');
        if (threatsRes.ok) {
          setThreatLogs(await threatsRes.json());
        }
      } catch (err) {
        console.error("Failed to fetch from backend:", err);
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const runManualScan = async () => {
    try {
      await fetch('http://localhost:8000/api/scan', { method: 'POST' });
      alert("Manual scan initiated across all active endpoints.");
    } catch (err) {
      alert("Failed to reach backend.");
    }
  };

  const quarantineIp = async (ip) => {
    try {
      const res = await fetch(`http://localhost:8000/api/firewall/block?ip=${ip}`, { method: 'POST' });
      if (res.ok) {
        alert(`Successfully quarantined IP: ${ip}`);
        fetchThreats();
      }
    } catch (e) {
      console.error("Failed to quarantine IP", e);
    }
  };

  const renderOverview = () => (
    <>
      {/* Top KPI Cards */}
      <div className="grid">
        <div className="glass-card">
          <div className="card-title"><Shield size={16} color="#00e5ff"/> Threats Blocked (Total)</div>
          <div className="card-value" style={{ color: '#00e5ff' }}>
            {healthData.total_threats_blocked.toLocaleString()}
          </div>
        </div>
        <div className="glass-card">
          <div className="card-title"><Cpu size={16} color="#ffb800"/> CPU Usage</div>
          <div className="card-value" style={{ color: healthData.cpu_usage > 80 ? '#ff3366' : 'white' }}>
            {healthData.cpu_usage}%
          </div>
        </div>
        <div className="glass-card">
          <div className="card-title"><Activity size={16} color="#00ff88"/> Memory Usage</div>
          <div className="card-value">{healthData.memory_usage}%</div>
        </div>
      </div>

      {/* Action Buttons & Threat Log */}
      <div className="grid">
        <div className="glass-card threat-log">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2>Live Active Threat Feed</h2>
            <button className="btn-primary" onClick={runManualScan}>Run Manual Scan</button>
          </div>
          
          {threatLogs.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#8b8b93' }}>
              Connecting to backend engine...
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Threat ID</th>
                  <th>Source IP / Origin</th>
                  <th>Detection Type</th>
                  <th>Severity</th>
                  <th>Action Taken</th>
                  <th>Time</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {threatLogs.map((threat) => (
                  <tr key={threat.id}>
                    <td style={{ fontFamily: 'monospace', color: '#00e5ff' }}>{threat.id}</td>
                    <td>{threat.ip}</td>
                    <td>{threat.type}</td>
                    <td className={`severity-${threat.severity.toLowerCase()}`}>{threat.severity}</td>
                    <td>
                      <span style={{
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '0.8rem',
                        backgroundColor: threat.status === 'Blocked' || threat.status === 'Quarantined' ? 'rgba(0,255,136,0.1)' : 'rgba(255,184,0,0.1)',
                        color: threat.status === 'Blocked' || threat.status === 'Quarantined' ? '#00ff88' : '#ffb800'
                      }}>
                        {threat.status}
                      </span>
                    </td>
                    <td style={{ color: '#8b8b93' }}>{new Date(threat.time).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );

  const renderFirewall = () => (
    <div className="grid">
      <div className="glass-card threat-log">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2>Active Firewall Rules</h2>
          <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Plus size={16} /> Add New Rule
          </button>
        </div>
        <table>
          <thead>
            <tr>
              <th>Rule ID</th>
              <th>Direction</th>
              <th>Action</th>
              <th>Protocol</th>
              <th>Source / Destination</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ fontFamily: 'monospace', color: '#00e5ff' }}>FW-101</td>
              <td>Inbound</td>
              <td style={{ color: '#ff3366' }}>BLOCK</td>
              <td>TCP/UDP</td>
              <td>45.33.12.98 (Malicious)</td>
              <td><span style={{ color: '#00ff88' }}>Active</span></td>
            </tr>
            <tr>
              <td style={{ fontFamily: 'monospace', color: '#00e5ff' }}>FW-102</td>
              <td>Inbound</td>
              <td style={{ color: '#00ff88' }}>ALLOW</td>
              <td>TCP: 443</td>
              <td>Any (0.0.0.0/0)</td>
              <td><span style={{ color: '#00ff88' }}>Active</span></td>
            </tr>
            <tr>
              <td style={{ fontFamily: 'monospace', color: '#00e5ff' }}>FW-103</td>
              <td>Outbound</td>
              <td style={{ color: '#ff3366' }}>BLOCK</td>
              <td>All</td>
              <td>Known Botnet IPs</td>
              <td><span style={{ color: '#00ff88' }}>Active</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderLogs = () => (
    <div className="grid">
      <div className="glass-card threat-log" style={{ backgroundColor: '#050505' }}>
        <h2 style={{ marginBottom: '16px', color: '#00ff88', fontFamily: 'monospace' }}>&gt; System Terminal Logs</h2>
        <div style={{ fontFamily: 'monospace', color: '#a0a0a0', lineHeight: '1.6', height: '400px', overflowY: 'auto' }}>
          <div>[INFO] {new Date().toLocaleTimeString()} - Security Engine Initialized on port 8000</div>
          <div>[INFO] {new Date().toLocaleTimeString()} - Connected to SQLite Database successfully</div>
          {threatLogs.map(log => (
            <div key={log.id} style={{ color: log.severity === 'High' ? '#ff3366' : '#a0a0a0' }}>
              [WARN] {new Date(log.time).toLocaleTimeString()} - {log.type} detected from {log.ip}. Action: {log.status}
            </div>
          ))}
          <div className="status-dot" style={{ display: 'inline-block', width: '10px', height: '15px', borderRadius: 0, marginTop: '8px' }}></div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="dashboard-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand">
          <Shield color="#00e5ff" size={28} />
          <span>CyberFrame Core</span>
        </div>
        
        <nav>
          <a className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
            <Activity className="nav-icon" /> Overview
          </a>
          <a className={`nav-item ${activeTab === 'firewall' ? 'active' : ''}`} onClick={() => setActiveTab('firewall')}>
            <Lock className="nav-icon" /> Firewall Rules
          </a>
          <a className={`nav-item ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>
            <Terminal className="nav-icon" /> System Logs
          </a>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="header">
          <h1>
            {activeTab === 'overview' && 'Security Command Center'}
            {activeTab === 'firewall' && 'Firewall & Traffic Rules'}
            {activeTab === 'logs' && 'System Event Logs'}
          </h1>
          <div className="status-badge">
            <div className="status-dot"></div>
            {healthData.status}
          </div>
        </header>

        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'firewall' && renderFirewall()}
        {activeTab === 'logs' && renderLogs()}

      </main>
    </div>
  );
}

export default App;
