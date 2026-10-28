import React, { useState } from 'react';
import { 
  ArrowLeft, CheckCircle, XCircle, RotateCcw, AlertTriangle, 
  Sparkles, FileText, Eye, ShieldCheck, HelpCircle, Check, 
  AlertCircle, Info, Clock, User, MapPin, Building, Phone, Send
} from 'lucide-react';
import DocumentModal from './DocumentModal';

export default function ApplicationDetail({ 
  detail, 
  onBack, 
  onRunAiReview, 
  aiLoading, 
  aiResult, 
  onSubmitDecision, 
  decisionLoading 
}) {
  const [selectedDocForModal, setSelectedDocForModal] = useState(null);
  const [officerRemarks, setOfficerRemarks] = useState('');
  const [pendingAction, setPendingAction] = useState(null); // 'approve', 'reject', 'return'
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!detail || !detail.application) return null;

  const app = detail.application;
  const completeness = detail.completeness || { documents: [], completeness_pct: 0 };
  const findings = detail.findings || [];
  const priority = detail.priority || { level: 'low', level_hi: 'सामान्य', score: 0, reasons_hi: [] };
  const auditTrail = detail.audit_trail || [];

  const handleActionClick = (action) => {
    if (!officerRemarks.trim()) {
      setErrorMessage('कृपया निर्णय लेने से पूर्व अनिवार्य कारण अथवा टिप्पणी दर्ज करें।');
      return;
    }
    setErrorMessage('');
    setPendingAction(action);
    setShowConfirmModal(true);
  };

  const handleConfirmSubmit = () => {
    if (!pendingAction) return;
    const aiAction = aiResult?.review?.suggested_action || null;
    onSubmitDecision({
      action: pendingAction,
      reason: officerRemarks.trim(),
      ai_recommendation: aiAction
    });
    setShowConfirmModal(false);
    setPendingAction(null);
  };

  const quickRemarks = [
    'समस्त आवश्यक 6 दस्तावेज़ विधिमान्य एवं सत्यापित पाए गए। प्रमाण पत्र जारी करने योग्य।',
    'सकल आय ₹1,80,000 से अधिक दर्शित हो रही है। अद्यतन वेतन पर्ची संलग्न करें।',
    'आय प्रमाण पत्र एवं 6 माह का बैंक खाता पासबुक संलग्न नहीं है। सुधार हेतु वापस।',
    'घोषित आय एवं बैंक विवरण में स्पष्ट विसंगति पाई गई है। अस्वीकृत।'
  ];

  const getStatusBadge = (status) => {
    const map = {
      pending: { label: 'लंबित', class: 'badge-pending' },
      under_review: { label: 'समीक्षाधीन', class: 'badge-under_review' },
      approved: { label: 'स्वीकृत', class: 'badge-approved' },
      rejected: { label: 'अस्वीकृत', class: 'badge-rejected' },
      returned_for_correction: { label: 'सुधार हेतु वापस', class: 'badge-returned_for_correction' }
    };
    const item = map[status] || { label: status, class: 'badge-pending' };
    return <span className={`badge ${item.class}`}>{item.label}</span>;
  };

  return (
    <div className="container">
      {/* Top Breadcrumb & Action Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <button onClick={onBack} className="btn btn-outline btn-sm">
          <ArrowLeft size={16} />
          <span>लंबित आवेदन सूची पर वापस जाएं (Back to List)</span>
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>प्रकरण स्थिति:</span>
          {getStatusBadge(app.status)}
          <span className={`badge badge-priority-${priority.level}`}>
            🎯 {priority.level_hi} प्राथमिकता (स्कोर: {priority.score})
          </span>
        </div>
      </div>

      {/* Main Review Workspace Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* LEFT COLUMN: Application Details, Documents & Findings */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Card 1: Applicant Profile & Details */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.85rem', marginBottom: '1rem' }}>
              <div>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--gov-navy-900)' }}>
                  {app.applicant_name}
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500, marginLeft: '0.5rem' }}>
                    ({app.applicant_name_en || 'Applicant'})
                  </span>
                </h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--gov-navy-600)', fontWeight: 700, marginTop: '0.15rem' }}>
                  आवेदन क्रमांक: {app.application_id} • {app.application_type}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>जमा दिनांक</div>
                <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>{app.submission_date}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--gov-saffron-700)', fontWeight: 700 }}>
                  ({detail.days_pending || 0} दिन लंबित)
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.85rem', fontSize: '0.86rem' }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>पिता/पति का नाम:</span>
                <div style={{ fontWeight: 600 }}>{app.father_name || '—'}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>जिला एवं तहसील:</span>
                <div style={{ fontWeight: 600 }}>{app.district} {app.tehsil ? `(${app.tehsil})` : ''}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>घोषित वार्षिक आय:</span>
                <div style={{ fontWeight: 800, color: 'var(--gov-green-700)', fontSize: '1.1rem' }}>
                  ₹{app.declared_annual_income?.toLocaleString('en-IN')}
                </div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>आय का मुख्य स्रोत:</span>
                <div style={{ fontWeight: 600 }}>{app.income_source || '—'}</div>
              </div>
              {app.secondary_income_record && (
                <div style={{ gridColumn: 'span 2', background: '#fef2f2', border: '1px solid #fee2e2', padding: '0.6rem 0.8rem', borderRadius: '8px' }}>
                  <span style={{ color: 'var(--gov-red-700)', fontWeight: 700 }}>
                    ⚠️ द्वितीयक अभिलेख में दर्ज आय (Secondary Income Record):
                  </span>
                  <div style={{ fontWeight: 800, color: 'var(--gov-red-700)', fontSize: '1.05rem' }}>
                    ₹{app.secondary_income_record?.toLocaleString('en-IN')}
                    <span style={{ fontSize: '0.75rem', fontWeight: 500, marginLeft: '0.5rem' }}>
                      (घोषित आय से ₹{(app.secondary_income_record - app.declared_annual_income)?.toLocaleString('en-IN')} का अंतर)
                    </span>
                  </div>
                </div>
              )}
              <div>
                <span style={{ color: 'var(--text-muted)' }}>परिवार सदस्य संख्या:</span>
                <div style={{ fontWeight: 600 }}>{app.family_members || 0} सदस्य</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>संपर्क नंबर:</span>
                <div style={{ fontWeight: 600 }}>{app.contact || '—'}</div>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-muted)' }}>स्थायी निवास का पता:</span>
                <div style={{ fontWeight: 600 }}>{app.address || '—'}</div>
              </div>
              {app.review_notes && (
                <div style={{ gridColumn: 'span 2', background: '#f8fafc', padding: '0.6rem 0.8rem', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>प्रारंभिक समीक्षा टिप्पणी:</span>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.82rem' }}>{app.review_notes}</div>
                </div>
              )}
            </div>
          </div>

          {/* Card 2: Document Verification Checklist with Previews */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <FileText size={18} style={{ color: 'var(--gov-navy-600)' }} />
                  <span>दस्तावेज़ सत्यापन चेकलिस्ट (Document Checklist)</span>
                </h3>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  प्रमाण पत्र जारी करने हेतु विहित 6 मानक अभिलेख
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div style={{ width: '80px', height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${completeness.completeness_pct}%`, 
                      height: '100%', 
                      background: completeness.completeness_pct === 100 ? 'var(--gov-green-600)' : 'var(--gov-saffron-500)' 
                    }} 
                  />
                </div>
                <span style={{ fontWeight: 800, fontSize: '0.9rem', color: completeness.completeness_pct === 100 ? 'var(--gov-green-700)' : 'var(--gov-saffron-700)' }}>
                  {completeness.completeness_pct}% पूर्ण
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {completeness.documents.map((doc) => {
                const isSubmitted = doc.status === 'submitted' || doc.status === 'verified';
                const isNeedsVerification = doc.status === 'needs_verification';
                const isMissing = doc.status === 'missing';

                return (
                  <div 
                    key={doc.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.7rem 0.9rem',
                      borderRadius: '8px',
                      background: isMissing ? '#fff5f5' : isNeedsVerification ? '#fffbeb' : '#f8fafc',
                      border: `1px solid ${isMissing ? '#fed7d7' : isNeedsVerification ? '#fef08a' : 'var(--border-light)'}`
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      {isSubmitted ? (
                        <CheckCircle size={18} style={{ color: 'var(--gov-green-600)' }} />
                      ) : isNeedsVerification ? (
                        <AlertTriangle size={18} style={{ color: 'var(--gov-saffron-600)' }} />
                      ) : (
                        <XCircle size={18} style={{ color: 'var(--gov-red-600)' }} />
                      )}
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.88rem', color: isMissing ? 'var(--gov-red-700)' : 'var(--text-main)' }}>
                          {doc.name_hi}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                          {doc.name_en} {doc.detail?.doc_number ? `• सं.: ${doc.detail.doc_number}` : ''}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span className={`badge ${isSubmitted ? 'badge-approved' : isNeedsVerification ? 'badge-priority-medium' : 'badge-rejected'}`}>
                        {doc.status_hi || (isSubmitted ? 'संलग्न' : 'गायब')}
                      </span>

                      {isSubmitted && (
                        <button
                          onClick={() => setSelectedDocForModal({ ...doc, detail: detail.document_details?.[doc.id] || doc.detail })}
                          className="btn btn-sm btn-outline"
                          style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                        >
                          <Eye size={12} />
                          <span>देखें (Preview)</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Card 3: Deterministic Rule-Engine Findings */}
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--gov-navy-900)', marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <ShieldCheck size={18} style={{ color: 'var(--gov-navy-700)' }} />
              <span>नियम-आधारित सत्यापन निष्कर्ष (Deterministic Findings)</span>
            </h3>

            {findings.length === 0 ? (
              <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.9rem', color: 'var(--gov-green-700)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Check size={18} />
                <span>सभी नियम-आधारित जांच सफल रहीं — कोई त्रुटि अथवा विसंगति नहीं पाई गई।</span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {findings.map((f, i) => {
                  const isErr = f.severity === 'error';
                  const isWarn = f.severity === 'warning';
                  const bg = isErr ? '#fef2f2' : isWarn ? '#fffbeb' : '#f0f9ff';
                  const border = isErr ? '#fecaca' : isWarn ? '#fef08a' : '#bae6fd';
                  const color = isErr ? 'var(--gov-red-700)' : isWarn ? 'var(--gov-saffron-700)' : 'var(--gov-blue-700)';

                  return (
                    <div key={i} style={{ background: bg, border: `1px solid ${border}`, borderRadius: '8px', padding: '0.75rem 0.9rem', fontSize: '0.84rem' }}>
                      <div style={{ fontWeight: 700, color, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        {isErr ? <XCircle size={16} /> : isWarn ? <AlertTriangle size={16} /> : <Info size={16} />}
                        <span>{f.finding_hi}</span>
                      </div>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '0.25rem', paddingLeft: '1.4rem' }}>
                        <strong>साक्ष्य:</strong> {f.evidence}<br />
                        <strong>अपेक्षित कार्यवाही:</strong> {f.recommendation_hi}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: AI Review Assistant & Officer Decision Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Card 4: AI Review Assistant (Groq LLM) */}
          <div className="card ai-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)', color: '#ffffff', width: '32px', height: '32px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={18} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--gov-navy-900)' }}>
                    AI समीक्षा सहायक (Groq LLM)
                  </h3>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    मॉडल: llama-3.1-8b-instant / संरचित विश्लेषण
                  </div>
                </div>
              </div>

              <button
                onClick={() => onRunAiReview(app.application_id)}
                disabled={aiLoading}
                className="btn btn-sm btn-primary"
                style={{ background: 'linear-gradient(135deg, #6d28d9, #4f46e5)' }}
              >
                {aiLoading ? (
                  <>
                    <span className="pulse-dot" style={{ background: '#ffffff' }}></span>
                    <span>विश्लेषण जारी...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={14} />
                    <span>AI समीक्षा चलाएं</span>
                  </>
                )}
              </button>
            </div>

            {/* AI Review Content Output */}
            {aiResult ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {aiResult.is_demo && (
                  <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', color: '#b45309', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Info size={14} />
                    <span><strong>डेमो समीक्षा:</strong> नियम-आधारित फॉलबैक इंजन द्वारा निष्पादित (लाइव AI कॉल नहीं)।</span>
                  </div>
                )}

                {/* Suggested Action Badge */}
                <div style={{
                  background: '#ffffff',
                  border: '2px solid var(--border-light)',
                  borderRadius: '10px',
                  padding: '0.75rem 1rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    AI अनुशंसित कार्यवाही:
                  </span>
                  {aiResult.review?.suggested_action === 'APPROVE' && (
                    <span className="badge badge-approved" style={{ fontSize: '0.9rem', padding: '0.3rem 0.8rem' }}>
                      ✅ स्वीकृति (APPROVE)
                    </span>
                  )}
                  {aiResult.review?.suggested_action === 'REJECT' && (
                    <span className="badge badge-rejected" style={{ fontSize: '0.9rem', padding: '0.3rem 0.8rem' }}>
                      ❌ अस्वीकृति (REJECT)
                    </span>
                  )}
                  {aiResult.review?.suggested_action === 'RETURN_FOR_CORRECTION' && (
                    <span className="badge badge-priority-medium" style={{ fontSize: '0.9rem', padding: '0.3rem 0.8rem' }}>
                      🔄 सुधार हेतु वापसी (RETURN)
                    </span>
                  )}
                  {aiResult.review?.suggested_action === 'NEEDS_MANUAL_REVIEW' && (
                    <span className="badge badge-under_review" style={{ fontSize: '0.9rem', padding: '0.3rem 0.8rem' }}>
                      🔍 मैन्युअल जांच (MANUAL REVIEW)
                    </span>
                  )}
                </div>

                {/* Summary */}
                <div style={{ background: '#ffffff', border: '1px solid var(--border-light)', borderRadius: '8px', padding: '0.85rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                    हिंदी सारांश (Executive Summary):
                  </div>
                  <div style={{ fontSize: '0.85rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
                    {aiResult.review?.summary_hi}
                  </div>
                </div>

                {/* Supporting Reasons */}
                {aiResult.review?.reasons_hi?.length > 0 && (
                  <div style={{ background: '#ffffff', border: '1px solid var(--border-light)', borderRadius: '8px', padding: '0.85rem' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                      साक्ष्य-आधारित कारण (Grounds & Reasons):
                    </div>
                    <ul style={{ paddingLeft: '1.25rem', fontSize: '0.82rem', lineHeight: 1.5, color: 'var(--text-main)' }}>
                      {aiResult.review.reasons_hi.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Confidence & Uncertainty */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  <span>विश्वास स्तर (Confidence): <strong>{aiResult.review?.confidence || 'मध्यम'}</strong></span>
                  <span style={{ fontStyle: 'italic', maxWidth: '60%', textAlign: 'right' }}>
                    {aiResult.review?.uncertainty_hi || 'भौतिक सत्यापन अनुशंसित'}
                  </span>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
                <Sparkles size={32} style={{ color: '#a78bfa', margin: '0 auto 0.5rem auto' }} />
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>AI सहायता प्राप्त करें</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', maxWidth: '280px', margin: '0.2rem auto 0.8rem auto' }}>
                  आवेदन सारांश, विसंगतियों की पहचान और अनुशंसित कार्यवाही हेतु ऊपर दिए बटन पर क्लिक करें।
                </div>
              </div>
            )}
          </div>

          {/* Card 5: Officer Final Decision Panel */}
          <div className="card" style={{ border: '2px solid var(--gov-navy-600)' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--gov-navy-900)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>⚖️ सक्षम प्राधिकारी निर्णय (Officer Decision)</span>
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              * म.प्र. राजस्व संहिता अनुसार अंतिम निर्णय केवल अधिकृत अधिकारी द्वारा मान्य होगा।
            </p>

            {/* Remarks Input */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.35rem', color: 'var(--gov-navy-900)' }}>
                निर्णय का कारण / आदेश टिप्पणी (Mandatory Remarks) *
              </label>
              <textarea
                value={officerRemarks}
                onChange={(e) => {
                  setOfficerRemarks(e.target.value);
                  if (errorMessage) setErrorMessage('');
                }}
                placeholder="प्रकरण में अपना आदेश, साक्ष्य व टिप्पणी यहां अंकित करें..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.65rem',
                  borderRadius: '8px',
                  border: errorMessage ? '1.5px solid var(--gov-red-600)' : '1px solid var(--border-light)',
                  fontFamily: 'inherit',
                  fontSize: '0.85rem',
                  outline: 'none'
                }}
              />
              {errorMessage && (
                <div style={{ color: 'var(--gov-red-600)', fontSize: '0.75rem', marginTop: '0.2rem', fontWeight: 600 }}>
                  {errorMessage}
                </div>
              )}
            </div>

            {/* Quick remark chips */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.3rem' }}>
                त्वरित टिप्पणी विकल्प (Quick Suggestions):
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                {quickRemarks.map((qr, i) => (
                  <button
                    key={i}
                    onClick={() => setOfficerRemarks(qr)}
                    type="button"
                    style={{
                      background: '#f1f5f9',
                      border: '1px solid #cbd5e1',
                      borderRadius: '4px',
                      padding: '0.2rem 0.5rem',
                      fontSize: '0.72rem',
                      color: 'var(--text-main)',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    + {qr.slice(0, 32)}...
                  </button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.6rem' }}>
              <button
                onClick={() => handleActionClick('approve')}
                className="btn btn-success"
                style={{ flexDirection: 'column', padding: '0.75rem 0.4rem', fontSize: '0.82rem' }}
              >
                <CheckCircle size={18} />
                <span>स्वीकृत करें</span>
              </button>

              <button
                onClick={() => handleActionClick('reject')}
                className="btn btn-danger"
                style={{ flexDirection: 'column', padding: '0.75rem 0.4rem', fontSize: '0.82rem' }}
              >
                <XCircle size={18} />
                <span>अस्वीकृत करें</span>
              </button>

              <button
                onClick={() => handleActionClick('return')}
                className="btn btn-warning"
                style={{ flexDirection: 'column', padding: '0.75rem 0.4rem', fontSize: '0.82rem' }}
              >
                <RotateCcw size={18} />
                <span>सुधार हेतु वापस</span>
              </button>
            </div>
          </div>

          {/* Card 6: Audit Trail History */}
          <div className="card">
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--gov-navy-900)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Clock size={16} style={{ color: 'var(--text-muted)' }} />
              <span>प्रकरण इतिहास एवं ऑडिट लॉग (Audit Trail)</span>
            </h3>

            {auditTrail.length === 0 ? (
              <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textAlign: 'center', padding: '1rem 0' }}>
                इस प्रकरण में अभी तक कोई पूर्व निर्णय अथवा कार्यवाही दर्ज नहीं है।
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {auditTrail.map((ev, i) => (
                  <div key={i} style={{ borderLeft: '3px solid var(--gov-navy-600)', paddingLeft: '0.65rem', fontSize: '0.78rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                      <span><strong>{ev.officer_name || 'अधिकारी'}</strong></span>
                      <span>{ev.created_at}</span>
                    </div>
                    <div style={{ fontWeight: 600, color: 'var(--gov-navy-900)', marginTop: '0.15rem' }}>
                      कार्रवाई: {ev.new_status}
                    </div>
                    {ev.remarks && (
                      <div style={{ color: '#334155', fontStyle: 'italic', marginTop: '0.1rem' }}>
                        "{ev.remarks}"
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* CONFIRMATION MODAL BEFORE COMMITTING DECISION */}
      {showConfirmModal && (
        <div className="modal-overlay" onClick={() => setShowConfirmModal(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '520px' }}>
            <div style={{ padding: '1.25rem', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <AlertCircle size={22} style={{ color: pendingAction === 'approve' ? 'var(--gov-green-600)' : 'var(--gov-red-600)' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800 }}>निर्णय पुष्टि (Confirm Action)</h3>
            </div>

            <div style={{ padding: '1.25rem', fontSize: '0.88rem', lineHeight: 1.6 }}>
              <p>
                क्या आप वाकई आवेदन <strong>{app.application_id}</strong> को 
                <span style={{ fontWeight: 800, color: pendingAction === 'approve' ? 'var(--gov-green-700)' : pendingAction === 'reject' ? 'var(--gov-red-700)' : '#c2410c' }}>
                  {pendingAction === 'approve' ? ' "स्वीकृत"' : pendingAction === 'reject' ? ' "अस्वीकृत"' : ' "सुधार हेतु वापस"'}
                </span> करने की पुष्टि करते हैं?
              </p>

              <div style={{ background: '#f8fafc', border: '1px solid var(--border-light)', padding: '0.75rem', borderRadius: '8px', margin: '0.85rem 0' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>आपकी आदेश टिप्पणी:</span>
                <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '0.2rem' }}>
                  "{officerRemarks}"
                </div>
              </div>

              {/* AI comparison note */}
              {aiResult?.review?.suggested_action && (
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  🤖 AI सिफारिश थी: <strong>{aiResult.review.suggested_action}</strong>.
                  {((pendingAction === 'approve' && aiResult.review.suggested_action === 'APPROVE') ||
                    (pendingAction === 'reject' && aiResult.review.suggested_action === 'REJECT') ||
                    (pendingAction === 'return' && aiResult.review.suggested_action === 'RETURN_FOR_CORRECTION')) ? (
                    <span style={{ color: 'var(--gov-green-700)', fontWeight: 700, marginLeft: '0.4rem' }}>
                      (AI सिफारिश के अनुरूप)
                    </span>
                  ) : (
                    <span style={{ color: 'var(--gov-saffron-700)', fontWeight: 700, marginLeft: '0.4rem' }}>
                      (अधिकारी विवेकाधिकार से भिन्न निर्णय - सुरक्षित ऑडिट दर्ज होगा)
                    </span>
                  )}
                </div>
              )}
            </div>

            <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', background: '#f8fafc', borderRadius: '0 0 16px 16px' }}>
              <button onClick={() => setShowConfirmModal(false)} className="btn btn-secondary btn-sm">
                रद्द करें (Cancel)
              </button>
              <button 
                onClick={handleConfirmSubmit} 
                disabled={decisionLoading}
                className={`btn btn-sm ${pendingAction === 'approve' ? 'btn-success' : pendingAction === 'reject' ? 'btn-danger' : 'btn-warning'}`}
              >
                {decisionLoading ? 'सत्यापन जारी...' : 'हाँ, निर्णय दर्ज करें'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* SYNTHETIC DOCUMENT MODAL PREVIEW */}
      {selectedDocForModal && (
        <DocumentModal
          doc={selectedDocForModal}
          application={app}
          onClose={() => setSelectedDocForModal(null)}
        />
      )}
    </div>
  );
}
