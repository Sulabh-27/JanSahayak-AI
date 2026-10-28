import React from 'react';
import { X, CheckCircle2, ShieldCheck, FileText, Stamp, MapPin, Calendar, Building, User } from 'lucide-react';

export default function DocumentModal({ doc, application, onClose }) {
  if (!doc) return null;

  const docId = doc.id;
  const docName = doc.name_hi;
  const details = doc.detail || {};

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={{
          padding: '1rem 1.4rem',
          borderBottom: '1px solid var(--border-light)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'linear-gradient(135deg, var(--gov-navy-900), var(--gov-navy-800))',
          color: '#ffffff',
          borderRadius: '16px 16px 0 0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <FileText size={20} style={{ color: 'var(--gov-saffron-500)' }} />
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem' }}>दस्तावेज़ पूर्वावलोकन (Simulated Document Viewer)</div>
              <div style={{ fontSize: '0.75rem', color: '#c5cae9' }}>{docName} • {application?.application_id}</div>
            </div>
          </div>
          <button 
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', padding: '0.2rem' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '1.5rem', background: '#f8fafc' }}>
          {/* Status Bar */}
          <div style={{
            background: '#ffffff',
            border: '1px solid var(--border-light)',
            borderRadius: '10px',
            padding: '0.75rem 1rem',
            marginBottom: '1.25rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <ShieldCheck size={18} style={{ color: doc.status === 'verified' ? 'var(--gov-green-600)' : 'var(--gov-saffron-600)' }} />
              <span>सत्यापन स्थिति: <strong>{doc.status === 'verified' ? '✅ पूर्व-सत्यापित (Verified)' : '📎 संलग्न (Submitted - Verification Pending)'}</strong></span>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              प्रकार: <strong>{details.type || docName}</strong>
            </span>
          </div>

          {/* SIMULATED DOCUMENT VISUAL RENDERING */}
          {docId === 'identity_proof' && (
            <div className="doc-mockup-aadhaar">
              <div className="doc-stripe-tricolor" />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #cbd5e1', paddingBottom: '0.5rem', marginBottom: '0.85rem' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--gov-navy-900)' }}>भारत विशिष्ट पहचान प्राधिकरण (UIDAI)</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Unique Identification Authority of India</div>
                </div>
                <div style={{ fontSize: '1.4rem' }}>🏛️</div>
              </div>

              <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
                <div style={{ width: '80px', height: '96px', background: '#cbd5e1', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #94a3b8' }}>
                  <User size={40} style={{ color: '#64748b' }} />
                </div>
                <div style={{ flex: 1, fontSize: '0.85rem' }}>
                  <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--gov-navy-900)' }}>{application?.applicant_name}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{application?.applicant_name_en}</div>
                  <div style={{ marginTop: '0.35rem' }}><strong>पिता / Husband:</strong> {application?.father_name}</div>
                  <div><strong>पता:</strong> {application?.address}</div>
                </div>
              </div>

              <div style={{ marginTop: '1rem', paddingTop: '0.6rem', borderTop: '1px dashed #cbd5e1', textAlign: 'center' }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '0.15em', color: 'var(--gov-navy-900)' }}>
                  {details.doc_number || 'XXXX-XXXX-8901'}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--gov-red-700)', fontWeight: 700, marginTop: '0.2rem' }}>
                  मेरा आधार, मेरी पहचान (Demonstration Synthetic Record)
                </div>
              </div>
            </div>
          )}

          {docId === 'income_proof' && (
            <div style={{ background: '#ffffff', border: '2px solid #cbd5e1', borderRadius: '10px', padding: '1.25rem' }}>
              <div style={{ textAlign: 'center', borderBottom: '2px solid #0f172a', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 800, textTransform: 'uppercase' }}>आय प्रमाणक पत्रक / वेतन प्रमाण (Income Verification Sheet)</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>सत्यापन अभिलेख संख्या: {details.doc_number || 'INC-DOC-2024'}</div>
              </div>

              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', marginBottom: '1rem' }}>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.45rem', fontWeight: 600, width: '40%' }}>आवेदक का नाम:</td>
                    <td style={{ padding: '0.45rem' }}>{application?.applicant_name} ({application?.applicant_name_en})</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.45rem', fontWeight: 600 }}>व्यवसाय / आय स्रोत:</td>
                    <td style={{ padding: '0.45rem' }}>{application?.income_source}</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.45rem', fontWeight: 600 }}>घोषित वार्षिक आय:</td>
                    <td style={{ padding: '0.45rem', fontWeight: 700, color: 'var(--gov-green-700)' }}>₹{application?.declared_annual_income?.toLocaleString('en-IN')}</td>
                  </tr>
                  {application?.secondary_income_record && (
                    <tr style={{ borderBottom: '1px solid #fee2e2', background: '#fef2f2' }}>
                      <td style={{ padding: '0.45rem', fontWeight: 700, color: 'var(--gov-red-700)' }}>वेतन पर्ची/ITR सकल आय:</td>
                      <td style={{ padding: '0.45rem', fontWeight: 800, color: 'var(--gov-red-700)' }}>
                        ₹{application?.secondary_income_record?.toLocaleString('en-IN')}
                        <span style={{ fontSize: '0.72rem', marginLeft: '0.5rem', fontWeight: 600 }}>(⚠️ विसंगति!)</span>
                      </td>
                    </tr>
                  )}
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.45rem', fontWeight: 600 }}>जारीकर्ता प्राधिकारी:</td>
                    <td style={{ padding: '0.45rem' }}>{details.type || 'नियोक्ता / तहसीलदार राजस्व'}</td>
                  </tr>
                </tbody>
              </table>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  दिनांक: {details.issue_date || '2024-10-01'}<br />
                  जिला: {application?.district}
                </div>
                <div style={{ textAlign: 'center', border: '1.5px dashed #0284c7', padding: '0.3rem 0.8rem', borderRadius: '6px', color: '#0284c7', fontSize: '0.75rem', fontWeight: 800 }}>
                  मुहर / DIGITAL STAMP<br />तहसील कार्यालय
                </div>
              </div>
            </div>
          )}

          {docId === 'ration_card' && (
            <div style={{ background: '#fefce8', border: '2px solid #fef08a', borderRadius: '10px', padding: '1.25rem' }}>
              <div style={{ borderBottom: '1.5px solid #ca8a04', paddingBottom: '0.5rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#854d0e' }}>मध्य प्रदेश खाद्य, नागरिक आपूर्ति एवं उपभोक्ता संरक्षण विभाग</div>
                  <div style={{ fontSize: '0.72rem', color: '#a16207' }}>राष्ट्रीय खाद्य सुरक्षा अधिनियम (NFSA) राशन कार्ड</div>
                </div>
                <span className="badge badge-priority-medium">{details.type || 'APL/BPL'}</span>
              </div>

              <div style={{ fontSize: '0.82rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div><strong>कार्ड धारक:</strong> {application?.applicant_name}</div>
                <div><strong>कार्ड क्रमांक:</strong> {details.doc_number || 'RC-MP-9921'}</div>
                <div><strong>परिवार सदस्य:</strong> {application?.family_members} सदस्य</div>
                <div><strong>उचित मूल्य दुकान:</strong> FPS-{application?.district}-01</div>
              </div>

              <div style={{ marginTop: '1rem', padding: '0.5rem', background: '#ffffff', borderRadius: '6px', fontSize: '0.75rem', border: '1px solid #fef08a' }}>
                ✔️ समग्र पोर्टल (Samagra Social Security Mission) द्वारा सत्यापित विवरण।
              </div>
            </div>
          )}

          {docId === 'address_proof' && (
            <div style={{ background: '#ffffff', border: '2px solid #cbd5e1', borderRadius: '10px', padding: '1.25rem' }}>
              <div style={{ borderBottom: '1px solid #cbd5e1', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 800 }}>म.प्र. विद्युत वितरण कंपनी लिमिटेड (Electricity Bill)</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>बिल संख्या: {details.doc_number || 'EB-BILL-4410'}</div>
              </div>

              <div style={{ fontSize: '0.82rem', lineHeight: 1.6 }}>
                <div><strong>उपभोक्ता नाम:</strong> {application?.applicant_name}</div>
                <div><strong>परिसर पता:</strong> {application?.address}</div>
                <div><strong>सत्यापित जिला:</strong> {application?.district} (म.प्र.)</div>
                <div><strong>बिल माह:</strong> {details.issue_date || 'हालिया माह'}</div>
              </div>
            </div>
          )}

          {docId === 'bank_statement' && (
            <div style={{ background: '#ffffff', border: '2px solid #cbd5e1', borderRadius: '10px', padding: '1.25rem' }}>
              <div style={{ borderBottom: '1px solid #cbd5e1', paddingBottom: '0.5rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 800 }}>बैंक खाता विवरण / पासबुक (Bank Statement)</div>
                <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>खाता सं.: {details.doc_number || 'SB-9876543210'}</span>
              </div>

              <div style={{ fontSize: '0.82rem', lineHeight: 1.6, marginBottom: '0.75rem' }}>
                <div><strong>बैंक शाखा:</strong> {details.type || 'भारतीय स्टेट बैंक (SBI)'}</div>
                <div><strong>खाताधारक:</strong> {application?.applicant_name}</div>
                <div><strong>विवरण तिथि:</strong> {details.statement_date || details.issue_date || 'अद्यतन 6 माह'}</div>
              </div>

              {application?.conflicting_dates && (
                <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.75rem', color: 'var(--gov-red-700)' }}>
                  ⚠️ <strong>सावधानी:</strong> {application.conflicting_dates.issue || 'बैंक स्टेटमेंट 6 माह से अधिक पुराना है'}
                </div>
              )}
            </div>
          )}

          {docId === 'self_declaration' && (
            <div style={{ background: '#fffbeb', border: '2px solid #fef3c7', borderRadius: '10px', padding: '1.25rem' }}>
              <div style={{ textAlign: 'center', borderBottom: '1px solid #d97706', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#92400e' }}>स्व-प्रमाणित घोषणा पत्र (Self Declaration Affidavit)</div>
                <div style={{ fontSize: '0.7rem', color: '#b45309' }}>मध्य प्रदेश शासन सामान्य प्रशासन विभाग परिपत्र अनुसार</div>
              </div>

              <p style={{ fontSize: '0.8rem', lineHeight: 1.6, color: '#451a03', fontStyle: 'italic', marginBottom: '1rem' }}>
                "मैं {application?.applicant_name}, पिता {application?.father_name}, निवासी {application?.address}, 
                सत्यनिष्ठा से घोषित करता/करती हूँ कि मेरे समस्त स्रोतों से कुल वार्षिक आय ₹{application?.declared_annual_income?.toLocaleString('en-IN')} है। 
                उक्त तथ्य पूर्णतः सत्य एवं सही हैं।"
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', fontSize: '0.75rem' }}>
                <div>सत्यापन संख्या: {details.doc_number || 'SD-AFFIDAVIT-01'}</div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontStyle: 'italic', color: '#78350f', fontWeight: 700 }}>{application?.applicant_name}</div>
                  <div>(आवेदक के डिजिटल हस्ताक्षर)</div>
                </div>
              </div>
            </div>
          )}

          <div style={{ marginTop: '1.25rem', textAlign: 'center' }}>
            <button onClick={onClose} className="btn btn-secondary" style={{ minWidth: '140px' }}>
              बंद करें (Close)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
