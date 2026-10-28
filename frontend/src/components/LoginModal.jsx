import React, { useState } from 'react';
import { Lock, User, ShieldAlert, Check, ArrowRight } from 'lucide-react';

export default function LoginModal({ onLogin, error }) {
  const [username, setUsername] = useState('officer');
  const [password, setPassword] = useState('jansahayak2024');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    onLogin(username, password).finally(() => setLoading(false));
  };

  const handleFillDemo = () => {
    setUsername('officer');
    setPassword('jansahayak2024');
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 20%, #1a237e 0%, #0a1128 100%)',
      padding: '1.5rem'
    }}>
      <div style={{
        background: '#ffffff',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '460px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        overflow: 'hidden'
      }}>
        {/* Card Header */}
        <div style={{
          background: 'linear-gradient(135deg, var(--gov-navy-900), var(--gov-navy-800))',
          padding: '2rem 1.75rem',
          textAlign: 'center',
          color: '#ffffff',
          borderBottom: '3px solid var(--gov-saffron-500)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.4rem' }}>🏛️</div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.01em' }}>
            जनसहायक AI — JanSahayak AI
          </h1>
          <p style={{ fontSize: '0.82rem', color: '#c5cae9', marginTop: '0.2rem' }}>
            मध्य प्रदेश शासन • राजस्व अधिकारी पोर्टल
          </p>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            background: 'rgba(245, 158, 11, 0.2)',
            border: '1px solid var(--gov-saffron-500)',
            color: '#fef3c7',
            padding: '0.2rem 0.65rem',
            borderRadius: '9999px',
            fontSize: '0.72rem',
            fontWeight: 700,
            marginTop: '0.75rem'
          }}>
            🔶 असाइनमेंट डेमो वातावरण (Demo Prototype)
          </div>
        </div>

        {/* Form Body */}
        <div style={{ padding: '2rem 1.75rem' }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
            {error && (
              <div style={{
                background: '#fef2f2',
                border: '1px solid #fecaca',
                padding: '0.75rem',
                borderRadius: '8px',
                color: 'var(--gov-red-700)',
                fontSize: '0.82rem',
                fontWeight: 600
              }}>
                {error}
              </div>
            )}

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.35rem', color: 'var(--gov-navy-900)' }}>
                उपयोगकर्ता नाम (Username)
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="officer"
                  style={{
                    width: '100%',
                    padding: '0.7rem 1rem 0.7rem 2.4rem',
                    borderRadius: '8px',
                    border: '1.5px solid var(--border-light)',
                    fontSize: '0.9rem',
                    outline: 'none',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.35rem', color: 'var(--gov-navy-900)' }}>
                पासवर्ड (Password)
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    padding: '0.7rem 1rem 0.7rem 2.4rem',
                    borderRadius: '8px',
                    border: '1.5px solid var(--border-light)',
                    fontSize: '0.9rem',
                    outline: 'none',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.8rem', fontSize: '0.95rem', marginTop: '0.4rem' }}
            >
              {loading ? 'सत्यापन जारी...' : 'सुरक्षित लॉगिन करें (Secure Login)'}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          {/* Quick Demo Credentials Box */}
          <div style={{
            marginTop: '1.5rem',
            padding: '0.85rem',
            background: '#f8fafc',
            border: '1px dashed #cbd5e1',
            borderRadius: '10px',
            fontSize: '0.78rem',
            textAlign: 'center'
          }}>
            <div style={{ fontWeight: 700, color: 'var(--gov-navy-800)', marginBottom: '0.2rem' }}>
              मूल्यांकन हेतु डेमो क्रेडेंशियल्स (Default):
            </div>
            <div style={{ color: 'var(--text-muted)' }}>
              Username: <code>officer</code> | Password: <code>jansahayak2024</code>
            </div>
            <button
              type="button"
              onClick={handleFillDemo}
              style={{
                marginTop: '0.5rem',
                background: 'none',
                border: 'none',
                color: 'var(--gov-navy-600)',
                fontWeight: 700,
                cursor: 'pointer',
                fontSize: '0.78rem',
                textDecoration: 'underline'
              }}
            >
              ⚡ एक क्लिक में क्रेडेंशियल्स भरें (Auto-Fill)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
