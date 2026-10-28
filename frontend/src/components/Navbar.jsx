import React, { useState, useEffect } from 'react';
import { ShieldCheck, User, LogOut, Clock, RotateCcw, AlertTriangle } from 'lucide-react';

export default function Navbar({ officer, onLogout, onReseed, isReseeding }) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('hi-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="top-nav">
      <div className="container nav-content">
        {/* Brand & Emblem */}
        <div className="brand-section">
          <div className="emblem-badge" title="मध्य प्रदेश शासन">
            🏛️
          </div>
          <div>
            <div className="brand-title">
              <span>जनसहायक AI</span>
              <span className="demo-chip">
                <AlertTriangle size={12} />
                डेमो वातावरण (Demonstration Prototype)
              </span>
            </div>
            <div className="brand-sub">
              मध्य प्रदेश शासन • राजस्व एवं लोक सेवा प्रबंधन विभाग
            </div>
          </div>
        </div>

        {/* Right Officer Status & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: '#c5cae9' }}>
            <Clock size={14} />
            <span>{time}</span>
          </div>

          {officer && (
            <div className="officer-badge">
              <User size={15} style={{ color: '#ffb74d' }} />
              <div>
                <div style={{ fontWeight: 700 }}>{officer.officer_name || 'श्री राजेश शर्मा'}</div>
                <div style={{ fontSize: '0.7rem', color: '#c5cae9' }}>{officer.role || 'तहसीलदार (राजस्व अधिकारी)'}</div>
              </div>
            </div>
          )}

          <button
            onClick={onReseed}
            disabled={isReseeding}
            className="btn btn-outline btn-sm"
            style={{ color: '#ffffff', borderColor: 'rgba(255,255,255,0.25)', background: 'rgba(255,255,255,0.08)' }}
            title="काल्पनिक डेटा रीसेट करें"
          >
            <RotateCcw size={14} className={isReseeding ? 'animate-spin' : ''} />
            <span>डेटा रीसेट</span>
          </button>

          {officer && (
            <button
              onClick={onLogout}
              className="btn btn-sm"
              style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#fca5a5' }}
              title="लॉगआउट करें"
            >
              <LogOut size={14} />
              <span>लॉगआउट</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
