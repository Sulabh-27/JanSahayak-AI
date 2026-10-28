import React from 'react';
import { 
  FileText, Clock, AlertCircle, FileX, CheckCircle, XCircle, 
  RotateCcw, ArrowRight, ShieldAlert, Award, TrendingUp, Calendar
} from 'lucide-react';

export default function Dashboard({ stats, onNavigateToApplications, onSelectFilter }) {
  if (!stats) return null;

  const total = stats.total_applications || 0;
  const pending = stats.pending || 0;
  const highPriority = stats.high_priority || 0;
  const incomplete = stats.incomplete_documents || 0;
  const agedBacklog = stats.aged_backlog_14_days || 0;
  const approved = stats.approved || 0;
  const rejected = stats.rejected || 0;
  const returned = stats.returned || 0;

  return (
    <div className="container">
      {/* Page Title & Status Banner */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span>📊 अधिकारी समीक्षा डैशबोर्ड (Executive Dashboard)</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
            मध्य प्रदेश लोक सेवा गारंटी अधिनियम अंतर्गत आय प्रमाण पत्र आवेदनों का रीयल-टाइम अवलोकन
          </p>
        </div>

        <button 
          onClick={() => onNavigateToApplications()}
          className="btn btn-primary"
        >
          <span>सभी आवेदन देखें (View All)</span>
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Critical Alert Banner if aged backlog or high priority */}
      {agedBacklog > 0 && (
        <div style={{
          background: 'linear-gradient(90deg, #fef2f2 0%, #fff7ed 100%)',
          border: '1.5px solid #fecaca',
          borderRadius: '12px',
          padding: '0.9rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span className="pulse-dot"></span>
            <ShieldAlert size={20} style={{ color: 'var(--gov-red-600)' }} />
            <div>
              <span style={{ fontWeight: 700, color: 'var(--gov-red-700)' }}>
                ध्यान दें (Priority Action): {agedBacklog} आवेदन 14 दिनों से अधिक समय से लंबित हैं!
              </span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                लोक सेवा गारंटी 15-दिवसीय समयसीमा उल्लंघन से बचने हेतु तत्काल निस्तारण अपेक्षित है।
              </span>
            </div>
          </div>
          <button 
            onClick={() => onSelectFilter({ priority: 'high', status: 'pending' })}
            className="btn btn-sm btn-danger"
          >
            तत्काल समीक्षा करें
          </button>
        </div>
      )}

      {/* 5 Primary KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card kpi-total card-hover" onClick={() => onSelectFilter({ status: 'all' })} style={{ cursor: 'pointer' }}>
          <div className="kpi-info">
            <span className="kpi-label">कुल प्राप्त आवेदन</span>
            <span className="kpi-number">{total}</span>
          </div>
          <div className="kpi-icon-wrap" style={{ background: '#e0e7ff', color: 'var(--gov-navy-700)' }}>
            <FileText size={22} />
          </div>
        </div>

        <div className="kpi-card kpi-pending card-hover" onClick={() => onSelectFilter({ status: 'pending' })} style={{ cursor: 'pointer' }}>
          <div className="kpi-info">
            <span className="kpi-label">समीक्षा हेतु लंबित</span>
            <span className="kpi-number" style={{ color: 'var(--gov-saffron-700)' }}>{pending}</span>
          </div>
          <div className="kpi-icon-wrap" style={{ background: 'var(--gov-saffron-100)', color: 'var(--gov-saffron-700)' }}>
            <Clock size={22} />
          </div>
        </div>

        <div className="kpi-card kpi-high card-hover" onClick={() => onSelectFilter({ priority: 'high' })} style={{ cursor: 'pointer' }}>
          <div className="kpi-info">
            <span className="kpi-label" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span className="pulse-dot"></span>
              उच्च प्राथमिकता
            </span>
            <span className="kpi-number" style={{ color: 'var(--gov-red-700)' }}>{highPriority}</span>
          </div>
          <div className="kpi-icon-wrap" style={{ background: 'var(--gov-red-100)', color: 'var(--gov-red-700)' }}>
            <AlertCircle size={22} />
          </div>
        </div>

        <div className="kpi-card kpi-incomplete card-hover" onClick={() => onSelectFilter({ doc_filter: 'incomplete' })} style={{ cursor: 'pointer' }}>
          <div className="kpi-info">
            <span className="kpi-label">दस्तावेज़ अधूरे</span>
            <span className="kpi-number" style={{ color: '#c2410c' }}>{incomplete}</span>
          </div>
          <div className="kpi-icon-wrap" style={{ background: '#ffedd5', color: '#c2410c' }}>
            <FileX size={22} />
          </div>
        </div>

        <div className="kpi-card kpi-approved card-hover" onClick={() => onSelectFilter({ status: 'approved' })} style={{ cursor: 'pointer' }}>
          <div className="kpi-info">
            <span className="kpi-label">स्वीकृत प्रमाण पत्र</span>
            <span className="kpi-number" style={{ color: 'var(--gov-green-700)' }}>{approved}</span>
          </div>
          <div className="kpi-icon-wrap" style={{ background: 'var(--gov-green-100)', color: 'var(--gov-green-700)' }}>
            <CheckCircle size={22} />
          </div>
        </div>
      </div>

      {/* Secondary Detailed Breakdown Row */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        {/* Status Breakdown Progress Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <TrendingUp size={18} style={{ color: 'var(--gov-navy-600)' }} />
              <span>प्रकरण निस्तारण स्थिति (Disposal Ratio)</span>
            </h3>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>
              कुल {total}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 600, color: 'var(--gov-saffron-700)' }}>⏳ लंबित (Pending)</span>
                <span style={{ fontWeight: 700 }}>{pending} ({total > 0 ? Math.round((pending/total)*100) : 0}%)</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${total > 0 ? (pending/total)*100 : 0}%`, backgroundColor: 'var(--gov-saffron-500)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 600, color: 'var(--gov-green-700)' }}>✅ स्वीकृत (Approved)</span>
                <span style={{ fontWeight: 700 }}>{approved} ({total > 0 ? Math.round((approved/total)*100) : 0}%)</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${total > 0 ? (approved/total)*100 : 0}%`, backgroundColor: 'var(--gov-green-600)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 600, color: '#c2410c' }}>🔄 सुधार हेतु वापस (Returned)</span>
                <span style={{ fontWeight: 700 }}>{returned} ({total > 0 ? Math.round((returned/total)*100) : 0}%)</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${total > 0 ? (returned/total)*100 : 0}%`, backgroundColor: '#f97316' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 600, color: 'var(--gov-red-700)' }}>❌ अस्वीकृत (Rejected)</span>
                <span style={{ fontWeight: 700 }}>{rejected} ({total > 0 ? Math.round((rejected/total)*100) : 0}%)</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${total > 0 ? (rejected/total)*100 : 0}%`, backgroundColor: 'var(--gov-red-600)' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Priority Distribution Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Award size={18} style={{ color: 'var(--gov-saffron-600)' }} />
              <span>प्राथमिकता विभाजन (Priority Matrix)</span>
            </h3>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>लंबित प्रकरण</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '8px', padding: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="pulse-dot"></span>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--gov-red-700)', fontSize: '0.88rem' }}>उच्च प्राथमिकता (High)</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>21+ दिन पुराने अथवा 3+ दस्तावेज़ गायब</div>
                </div>
              </div>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gov-red-700)' }}>{stats.high_priority || 0}</span>
            </div>

            <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderRadius: '8px', padding: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--gov-saffron-500)', display: 'inline-block' }}></span>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--gov-saffron-700)', fontSize: '0.88rem' }}>मध्यम प्राथमिकता (Medium)</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>7-14 दिन अथवा 1-2 कमियां</div>
                </div>
              </div>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gov-saffron-700)' }}>{stats.medium_priority || 0}</span>
            </div>

            <div style={{ background: '#f0fdf4', border: '1px solid #dcfce7', borderRadius: '8px', padding: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--gov-green-600)', display: 'inline-block' }}></span>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--gov-green-700)', fontSize: '0.88rem' }}>सामान्य प्राथमिकता (Low)</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>हाल ही में जमा, पूर्ण दस्तावेज़</div>
                </div>
              </div>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gov-green-700)' }}>{stats.low_priority || 0}</span>
            </div>
          </div>
        </div>

        {/* Legal & SLA Compliance Card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Calendar size={18} style={{ color: 'var(--gov-blue-700)' }} />
              <span>लोक सेवा गारंटी समयसीमा (SLA Tracking)</span>
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', fontSize: '0.85rem' }}>
            <div style={{ padding: '0.65rem 0.8rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                <span>विहित समय सीमा (Statutory Limit):</span>
                <span style={{ color: 'var(--gov-navy-700)' }}>15 कार्य दिवस (15 Days)</span>
              </div>
            </div>

            <div style={{ padding: '0.65rem 0.8rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                <span>समय-सीमा पार प्रकरण (Overdue):</span>
                <span style={{ color: agedBacklog > 0 ? 'var(--gov-red-600)' : 'var(--gov-green-600)', fontWeight: 800 }}>
                  {agedBacklog} आवेदन
                </span>
              </div>
            </div>

            <div style={{ padding: '0.65rem 0.8rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                <span>दस्तावेज़ पूर्णता अनुपात:</span>
                <span style={{ color: 'var(--gov-navy-700)', fontWeight: 700 }}>
                  {pending > 0 ? Math.round(((pending - incomplete) / pending) * 100) : 100}%
                </span>
              </div>
            </div>

            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: 1.4, marginTop: '0.2rem' }}>
              * म.प्र. लोक सेवा प्रदाय गारंटी अधिनियम 2010 अंतर्गत नागरिकों को समयबद्ध सेवा उपलब्ध कराना अनिवार्य है।
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
