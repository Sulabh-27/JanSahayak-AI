import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, User, Clock, FileText, CheckCircle, XCircle, RotateCcw } from 'lucide-react';

export default function AuditHistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/audit-history')
      .then(res => res.json())
      .then(data => {
        setHistory(data.history || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load audit history', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="container">
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <History size={24} style={{ color: 'var(--gov-navy-600)' }} />
          <span>निर्णय इतिहास एवं डिजिटल ऑडिट लॉग (Audit Trail Log)</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          मध्य प्रदेश शासन लोक सेवा अंतर्गत सभी अधिकारियों द्वारा लिए गए निर्णयों का अपरिवर्तनीय इतिहास
        </p>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
            ऑडिट लॉग लोड हो रहा है...
          </div>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
            कोई पूर्व निर्णय अथवा इतिहास प्रविष्टि दर्ज नहीं है।
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {history.map((item, idx) => {
              const isApprove = item.event_type?.includes('approve') || item.new_status === 'approved';
              const isReject = item.event_type?.includes('reject') || item.new_status === 'rejected';
              const isReturn = item.event_type?.includes('return') || item.new_status === 'returned_for_correction';

              const icon = isApprove ? (
                <CheckCircle size={18} style={{ color: 'var(--gov-green-600)' }} />
              ) : isReject ? (
                <XCircle size={18} style={{ color: 'var(--gov-red-600)' }} />
              ) : (
                <RotateCcw size={18} style={{ color: 'var(--gov-saffron-600)' }} />
              );

              return (
                <div 
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    padding: '0.9rem 1.1rem',
                    background: '#f8fafc',
                    border: '1px solid var(--border-light)',
                    borderRadius: '10px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                    <div style={{ marginTop: '0.2rem' }}>{icon}</div>
                    <div>
                      <div style={{ fontWeight: 800, color: 'var(--gov-navy-900)', fontSize: '0.92rem' }}>
                        आवेदन सं.: {item.application_id}
                        <span style={{ fontWeight: 500, fontSize: '0.78rem', color: 'var(--text-muted)', marginLeft: '0.6rem' }}>
                          ({item.old_status || 'लंबित'} ➔ <strong>{item.new_status}</strong>)
                        </span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#334155', marginTop: '0.25rem', fontStyle: 'italic' }}>
                        "{item.remarks || 'कोई टिप्पणी नहीं'}"
                      </div>
                      {item.ai_recommendation && (
                        <div style={{ fontSize: '0.75rem', color: '#6d28d9', marginTop: '0.25rem', fontWeight: 600 }}>
                          🤖 AI सिफारिश रिकॉर्ड: {item.ai_recommendation}
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                    <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{item.officer_name || 'अधिकारी'}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', justifyContent: 'flex-end', marginTop: '0.15rem' }}>
                      <Clock size={12} />
                      <span>{item.created_at}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
