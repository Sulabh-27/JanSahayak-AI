import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import ApplicationList from './components/ApplicationList';
import ApplicationDetail from './components/ApplicationDetail';
import AuditHistoryPage from './components/AuditHistoryPage';
import HelpPage from './components/HelpPage';
import LoginModal from './components/LoginModal';
import { LayoutDashboard, ListOrdered, History, HelpCircle, CheckCircle, AlertCircle } from 'lucide-react';

export default function App() {
  const [officer, setOfficer] = useState(() => {
    const saved = localStorage.getItem('jansahayak_officer');
    return saved ? JSON.parse(saved) : null;
  });

  const [currentTab, setCurrentTab] = useState('dashboard'); // dashboard, applications, review, history, help
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [selectedAppId, setSelectedAppId] = useState(null);
  const [selectedAppDetail, setSelectedAppDetail] = useState(null);
  const [listFilters, setListFilters] = useState({});

  // AI & Decision States
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [decisionLoading, setDecisionLoading] = useState(false);
  const [isReseeding, setIsReseeding] = useState(false);

  // Toast notification
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Fetch Stats and Applications
  const refreshData = async () => {
    try {
      const [statsRes, appsRes] = await Promise.all([
        fetch('/api/dashboard/stats'),
        fetch('/api/applications')
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
      if (appsRes.ok) {
        const appsData = await appsRes.json();
        setApplications(appsData.applications || []);
      }
    } catch (err) {
      console.error('Error fetching data from API:', err);
    }
  };

  useEffect(() => {
    if (officer) {
      refreshData();
    }
  }, [officer]);

  // Load single application detail
  const handleSelectApplication = async (appId) => {
    try {
      setSelectedAppId(appId);
      setAiResult(null);
      const res = await fetch(`/api/applications/${appId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedAppDetail(data);
        setCurrentTab('review');
      } else {
        showToast('आवेदन विवरण लोड करने में त्रुटि', 'error');
      }
    } catch (err) {
      console.error('Failed to load application detail', err);
      showToast('सर्वर से कनेक्ट करने में त्रुटि', 'error');
    }
  };

  // Run AI Review
  const handleRunAiReview = async (appId) => {
    setAiLoading(true);
    try {
      const res = await fetch(`/api/applications/${appId}/ai-review`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setAiResult(data);
        showToast('AI समीक्षा सफलतापूर्वक पूर्ण हुई', 'success');
      } else {
        showToast('AI समीक्षा निष्पादित करने में त्रुटि', 'error');
      }
    } catch (err) {
      console.error('AI Review error', err);
      showToast('AI सेवा कनेक्ट नहीं हो सकी', 'error');
    } finally {
      setAiLoading(false);
    }
  };

  // Submit Officer Decision
  const handleSubmitDecision = async ({ action, reason, ai_recommendation }) => {
    if (!selectedAppId) return;
    setDecisionLoading(true);
    try {
      const res = await fetch(`/api/applications/${selectedAppId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          reason,
          ai_recommendation,
          officer_id: officer?.officer_id,
          officer_name: officer?.officer_name
        })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        showToast(data.message_hi || 'निर्णय सफलतापूर्वक दर्ज किया गया', 'success');
        // Refresh application detail & overall list
        await refreshData();
        const updatedRes = await fetch(`/api/applications/${selectedAppId}`);
        if (updatedRes.ok) {
          setSelectedAppDetail(await updatedRes.json());
        }
      } else {
        showToast(data.detail || 'निर्णय दर्ज करने में त्रुटि', 'error');
      }
    } catch (err) {
      console.error('Submit decision error', err);
      showToast('निर्णय सुरक्षित करने में तकनीकी त्रुटि', 'error');
    } finally {
      setDecisionLoading(false);
    }
  };

  // Reseed Database
  const handleReseed = async () => {
    if (!window.confirm('क्या आप वाकई सभी 26 काल्पनिक आवेदनों के साथ डेटाबेस को रीसेट करना चाहते हैं?')) {
      return;
    }
    setIsReseeding(true);
    try {
      const res = await fetch('/api/system/reseed', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        showToast(data.message || 'डेटाबेस रीसेट हो गया', 'success');
        await refreshData();
        if (currentTab === 'review') {
          setCurrentTab('applications');
        }
      } else {
        showToast('रीसेट विफल', 'error');
      }
    } catch (err) {
      console.error('Reseed error', err);
      showToast('रीसेट में त्रुटि', 'error');
    } finally {
      setIsReseeding(false);
    }
  };

  // Authentication Handlers
  const handleLogin = async (username, password) => {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (res.ok) {
        const data = await res.json();
        setOfficer(data.officer);
        localStorage.setItem('jansahayak_officer', JSON.stringify(data.officer));
        showToast(`स्वागत है, ${data.officer.officer_name}`, 'success');
      } else {
        throw new Error('अमान्य उपयोगकर्ता नाम अथवा पासवर्ड');
      }
    } catch (err) {
      throw err;
    }
  };

  const handleLogout = () => {
    setOfficer(null);
    localStorage.removeItem('jansahayak_officer');
    showToast('लॉगआउट संपन्न', 'success');
  };

  // If not logged in, show Login Screen
  if (!officer) {
    return <LoginModal onLogin={handleLogin} />;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <Navbar 
        officer={officer} 
        onLogout={handleLogout} 
        onReseed={handleReseed} 
        isReseeding={isReseeding} 
      />

      {/* Sub Navigation Tabs */}
      <nav className="sub-nav">
        <button
          onClick={() => setCurrentTab('dashboard')}
          className={`nav-tab ${currentTab === 'dashboard' ? 'active' : ''}`}
        >
          <LayoutDashboard size={17} />
          <span>डैशबोर्ड (Overview)</span>
        </button>

        <button
          onClick={() => setCurrentTab('applications')}
          className={`nav-tab ${currentTab === 'applications' ? 'active' : ''}`}
        >
          <ListOrdered size={17} />
          <span>लंबित आवेदन सूची (Applications)</span>
          {stats?.pending > 0 && <span className="tab-badge">{stats.pending}</span>}
        </button>

        {currentTab === 'review' && selectedAppDetail && (
          <button
            onClick={() => setCurrentTab('review')}
            className="nav-tab active"
            style={{ color: 'var(--gov-navy-700)', fontWeight: 800 }}
          >
            <span>📂 समीक्षा: {selectedAppDetail.application?.application_id}</span>
          </button>
        )}

        <button
          onClick={() => setCurrentTab('history')}
          className={`nav-tab ${currentTab === 'history' ? 'active' : ''}`}
        >
          <History size={17} />
          <span>निर्णय इतिहास (Audit Log)</span>
        </button>

        <button
          onClick={() => setCurrentTab('help')}
          className={`nav-tab ${currentTab === 'help' ? 'active' : ''}`}
        >
          <HelpCircle size={17} />
          <span>सहायता एवं निर्देश (SOP Guide)</span>
        </button>
      </nav>

      {/* Toast Notification Banner */}
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          background: toast.type === 'success' ? '#14532d' : '#991b1b',
          color: '#ffffff',
          padding: '0.85rem 1.25rem',
          borderRadius: '10px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.25)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          fontSize: '0.88rem',
          fontWeight: 600,
          animation: 'modalEnter 0.2s ease'
        }}>
          {toast.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{toast.message}</span>
        </div>
      )}

      {/* Main Tab Content Routing */}
      <main className="main-wrapper" style={{ flex: 1 }}>
        {currentTab === 'dashboard' && (
          <Dashboard
            stats={stats}
            onNavigateToApplications={() => setCurrentTab('applications')}
            onSelectFilter={(filters) => {
              setListFilters(filters);
              setCurrentTab('applications');
            }}
          />
        )}

        {currentTab === 'applications' && (
          <ApplicationList
            applications={applications}
            initialFilters={listFilters}
            onSelectApplication={handleSelectApplication}
          />
        )}

        {currentTab === 'review' && selectedAppDetail && (
          <ApplicationDetail
            detail={selectedAppDetail}
            onBack={() => setCurrentTab('applications')}
            onRunAiReview={handleRunAiReview}
            aiLoading={aiLoading}
            aiResult={aiResult}
            onSubmitDecision={handleSubmitDecision}
            decisionLoading={decisionLoading}
          />
        )}

        {currentTab === 'history' && (
          <AuditHistoryPage />
        )}

        {currentTab === 'help' && (
          <HelpPage />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        background: '#ffffff',
        borderTop: '1px solid var(--border-light)',
        padding: '1.25rem 0',
        textAlign: 'center',
        fontSize: '0.78rem',
        color: 'var(--text-muted)'
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <strong>जनसहायक AI (JanSahayak AI) v2.0.0</strong> • Full Stack AI Engineer Production MVP
          </div>
          <div>
            निर्मित: React 19 + FastAPI + Groq AI • केवल प्रदर्शन एवं मूल्यांकन हेतु
          </div>
        </div>
      </footer>
    </div>
  );
}
