import React, { useState, useMemo } from 'react';
import { 
  Search, Filter, ArrowUpDown, FileText, CheckCircle2, 
  AlertCircle, ChevronRight, X, Sparkles, MapPin, Calendar, Clock
} from 'lucide-react';

export default function ApplicationList({ applications, onSelectApplication, initialFilters = {} }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState(initialFilters.status || 'all');
  const [priorityFilter, setPriorityFilter] = useState(initialFilters.priority || 'all');
  const [docFilter, setDocFilter] = useState(initialFilters.doc_filter || 'all');
  const [districtFilter, setDistrictFilter] = useState('all');
  const [sortBy, setSortBy] = useState('priority'); // priority, days, date, income

  // Extract unique districts
  const districts = useMemo(() => {
    const set = new Set();
    applications.forEach(a => {
      if (a.district) set.add(a.district);
    });
    return Array.from(set).sort();
  }, [applications]);

  // Filter & Sort applications
  const filteredApps = useMemo(() => {
    let result = [...applications];

    // Search query
    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      result = result.filter(a => 
        a.application_id?.toLowerCase().includes(q) ||
        a.applicant_name?.toLowerCase().includes(q) ||
        a.applicant_name_en?.toLowerCase().includes(q) ||
        a.district?.toLowerCase().includes(q) ||
        a.address?.toLowerCase().includes(q)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      result = result.filter(a => a.status === statusFilter);
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      result = result.filter(a => a.priority?.level === priorityFilter);
    }

    // Document filter
    if (docFilter === 'incomplete') {
      result = result.filter(a => !a.doc_complete);
    } else if (docFilter === 'complete') {
      result = result.filter(a => a.doc_complete);
    }

    // District filter
    if (districtFilter !== 'all') {
      result = result.filter(a => a.district === districtFilter);
    }

    // Sorting
    result.sort((a, b) => {
      if (sortBy === 'priority') {
        const scoreDiff = (b.priority?.score || 0) - (a.priority?.score || 0);
        if (scoreDiff !== 0) return scoreDiff;
        return (a.submission_date || '').localeCompare(b.submission_date || '');
      }
      if (sortBy === 'days') {
        return (b.days_pending || 0) - (a.days_pending || 0);
      }
      if (sortBy === 'date') {
        return (b.submission_date || '').localeCompare(a.submission_date || '');
      }
      if (sortBy === 'income') {
        return (a.declared_annual_income || 0) - (b.declared_annual_income || 0);
      }
      return 0;
    });

    return result;
  }, [applications, searchTerm, statusFilter, priorityFilter, docFilter, districtFilter, sortBy]);

  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setPriorityFilter('all');
    setDocFilter('all');
    setDistrictFilter('all');
    setSortBy('priority');
  };

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

  const getPriorityBadge = (priority) => {
    const level = priority?.level || 'low';
    const label = priority?.level_hi || 'सामान्य';
    const score = priority?.score || 0;
    return (
      <span className={`badge badge-priority-${level}`}>
        {level === 'high' && <span className="pulse-dot" style={{ marginRight: '0.2rem' }}></span>}
        {label} ({score})
      </span>
    );
  };

  return (
    <div className="container">
      {/* Title */}
      <div style={{ marginBottom: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--gov-navy-900)' }}>
            📋 लंबित आवेदन कार्यक्षेत्र (Application Queue)
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            कुल {applications.length} में से {filteredApps.length} आवेदन प्रदर्शित
          </p>
        </div>

        {(searchTerm || statusFilter !== 'all' || priorityFilter !== 'all' || docFilter !== 'all' || districtFilter !== 'all') && (
          <button onClick={resetFilters} className="btn btn-outline btn-sm" style={{ color: 'var(--gov-red-600)', borderColor: '#fca5a5' }}>
            <X size={14} />
            <span>फ़िल्टर रीसेट करें</span>
          </button>
        )}
      </div>

      {/* Filter and Search Toolbar */}
      <div className="filter-bar">
        {/* Search */}
        <div className="search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="खोजें: आवेदन ID (MP-INC-...), आवेदक नाम, जिला..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Status Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <select 
            className="filter-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">📌 स्थिति: सभी (All)</option>
            <option value="pending">लंबित (Pending)</option>
            <option value="under_review">समीक्षाधीन (Under Review)</option>
            <option value="approved">स्वीकृत (Approved)</option>
            <option value="rejected">अस्वीकृत (Rejected)</option>
            <option value="returned_for_correction">सुधार हेतु वापस (Returned)</option>
          </select>
        </div>

        {/* Priority Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <select 
            className="filter-select"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="all">🎯 प्राथमिकता: सभी (All)</option>
            <option value="high">🔴 उच्च (High Priority)</option>
            <option value="medium">🟡 मध्यम (Medium Priority)</option>
            <option value="low">🟢 सामान्य (Low Priority)</option>
          </select>
        </div>

        {/* Documents Completeness Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <select 
            className="filter-select"
            value={docFilter}
            onChange={(e) => setDocFilter(e.target.value)}
          >
            <option value="all">📄 दस्तावेज़: सभी</option>
            <option value="complete">✅ दस्तावेज़ पूर्ण (100%)</option>
            <option value="incomplete">❌ दस्तावेज़ अधूरे (&lt;100%)</option>
          </select>
        </div>

        {/* District Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <select 
            className="filter-select"
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
          >
            <option value="all">📍 जिला: सभी</option>
            {districts.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        {/* Sort Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <select 
            className="filter-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{ fontWeight: 600, background: '#f8fafc' }}
          >
            <option value="priority">क्रमबद्ध: प्राथमिकता (सर्वोच्च पहले)</option>
            <option value="days">क्रमबद्ध: लंबित दिन (अधिकतम पहले)</option>
            <option value="date">क्रमबद्ध: नवीन आवेदन पहले</option>
            <option value="income">क्रमबद्ध: घोषित आय (न्यूनतम पहले)</option>
          </select>
        </div>
      </div>

      {/* Applications Table */}
      {filteredApps.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
          <FileText size={48} style={{ color: 'var(--text-dim)', margin: '0 auto 0.75rem auto' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-muted)' }}>कोई आवेदन नहीं मिला</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
            चयनित खोज अथवा फ़िल्टर मापदंड के अनुसार कोई प्रकरण उपलब्ध नहीं है।
          </p>
          <button onClick={resetFilters} className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }}>
            फ़िल्टर साफ़ करें (Reset Filters)
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table className="app-table">
            <thead>
              <tr>
                <th>आवेदन विवरण (Application)</th>
                <th>आवेदक एवं जिला (Applicant & District)</th>
                <th>घोषित आय (Income)</th>
                <th>लंबित अवधि (Days)</th>
                <th>दस्तावेज़ पूर्णता (Docs)</th>
                <th>प्राथमिकता (Priority)</th>
                <th>वर्तमान स्थिति (Status)</th>
                <th style={{ textAlign: 'right' }}>कार्यवाही (Action)</th>
              </tr>
            </thead>
            <tbody>
              {filteredApps.map((app) => {
                const days = app.days_pending || 0;
                const daysColor = days > 14 ? 'var(--gov-red-600)' : days > 7 ? 'var(--gov-saffron-600)' : 'var(--gov-green-600)';
                const pct = app.completeness_pct || 0;
                const pctColor = pct === 100 ? 'var(--gov-green-600)' : pct >= 60 ? 'var(--gov-saffron-600)' : 'var(--gov-red-600)';

                return (
                  <tr key={app.application_id} style={{ cursor: 'pointer' }} onClick={() => onSelectApplication(app.application_id)}>
                    {/* App ID & Type */}
                    <td>
                      <div style={{ fontWeight: 800, color: 'var(--gov-navy-700)', fontSize: '0.92rem' }}>
                        {app.application_id}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.15rem' }}>
                        <Calendar size={12} />
                        <span>जमा: {app.submission_date}</span>
                      </div>
                    </td>

                    {/* Applicant & District */}
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.92rem' }}>
                        {app.applicant_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.15rem' }}>
                        <MapPin size={12} />
                        <span>{app.district} {app.tehsil ? `• ${app.tehsil}` : ''}</span>
                      </div>
                    </td>

                    {/* Income */}
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--gov-navy-900)' }}>
                        ₹{app.declared_annual_income?.toLocaleString('en-IN')}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {app.income_source || 'सामान्य'}
                      </div>
                    </td>

                    {/* Days Pending */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 800, color: daysColor }}>
                        <Clock size={14} />
                        <span>{days} दिन</span>
                      </div>
                      {days > 14 && (
                        <span style={{ fontSize: '0.68rem', color: 'var(--gov-red-700)', fontWeight: 700 }}>
                          समयसीमा पार
                        </span>
                      )}
                    </td>

                    {/* Document Completeness */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '50px', background: '#e2e8f0', height: '6px', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${pct}%`, height: '100%', background: pctColor }} />
                        </div>
                        <span style={{ fontWeight: 700, fontSize: '0.8rem', color: pctColor }}>
                          {pct}%
                        </span>
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>
                        {app.doc_complete ? 'समस्त 6 संलग्न' : 'कमियां मौजूद'}
                      </div>
                    </td>

                    {/* Priority Badge */}
                    <td>
                      {getPriorityBadge(app.priority)}
                    </td>

                    {/* Status Badge */}
                    <td>
                      {getStatusBadge(app.status)}
                    </td>

                    {/* Action Button */}
                    <td style={{ textAlign: 'right' }}>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectApplication(app.application_id);
                        }}
                        className="btn btn-sm btn-primary"
                        style={{ whiteSpace: 'nowrap' }}
                      >
                        <span>समीक्षा करें</span>
                        <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
