import React from 'react';
import { HelpCircle, ShieldAlert, FileText, CheckCircle2, Scale, Sparkles, BookOpen } from 'lucide-react';

export default function HelpPage() {
  return (
    <div className="container" style={{ maxWidth: '1000px' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--gov-navy-900)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <HelpCircle size={24} style={{ color: 'var(--gov-navy-600)' }} />
          <span>सहायता एवं मार्गदर्शिका (SOP & User Guide)</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          आय प्रमाण पत्र समीक्षा प्रक्रिया, नियम-आधारित सत्यापन एवं AI सहायता संबंधी आधिकारिक निर्देश
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Prototype Warning Banner */}
        <div style={{ background: '#fffbeb', border: '1.5px solid #fde68a', borderRadius: '12px', padding: '1rem 1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#b45309', fontWeight: 800, fontSize: '0.95rem' }}>
            <ShieldAlert size={18} />
            <span>महत्वपूर्ण अस्वीकरण (Demonstration Prototype Disclaimer)</span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#78350f', marginTop: '0.35rem', lineHeight: 1.6 }}>
            यह सॉफ्टवेयर प्रणाली Kenpath असाइनमेंट मूल्यांकन हेतु तैयार किया गया एक <strong>पूर्ण कार्यात्मक प्रोटोटाइप (Full Stack MVP)</strong> है। 
            इसमें प्रदर्शित सभी 26 नागरिक आवेदन, नाम, पते एवं अभिलेख पूर्णतः <strong>काल्पनिक (Synthetic/Fictional)</strong> हैं। 
            किसी भी वास्तविक जीवित व्यक्ति अथवा सरकारी नागरिक डेटा से इसका कोई संबंध नहीं है।
          </p>
        </div>

        {/* Card 1: Standard Operating Procedure (SOP) */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--gov-navy-900)', marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BookOpen size={18} style={{ color: 'var(--gov-navy-600)' }} />
            <span>मध्य प्रदेश आय प्रमाण पत्र — मानक संचालन प्रक्रिया (SOP)</span>
          </h2>

          <div style={{ fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--text-main)' }}>
            <p style={{ marginBottom: '0.75rem' }}>
              मध्य प्रदेश लोक सेवा प्रदाय गारंटी अधिनियम 2010 एवं राजस्व पुस्तक परिपत्र (RBC) अंतर्गत आय प्रमाण पत्र सेवा हेतु 
              <strong>15 कार्य दिवस</strong> की समयसीमा निर्धारित है।
            </p>

            <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--gov-navy-800)', marginTop: '0.75rem', marginBottom: '0.35rem' }}>
              विहित 6 आवश्यक दस्तावेज़ (Mandatory 6 Document Checklist):
            </h3>
            <ol style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <li><strong>पहचान प्रमाण (Identity Proof):</strong> आधार कार्ड (Aadhaar), मतदाता परिचय पत्र (Voter ID) अथवा पैन कार्ड।</li>
              <li><strong>पता प्रमाण (Address Proof):</strong> बिजली बिल, पानी बिल, पंजीकृत किरायानामा अथवा राशन कार्ड।</li>
              <li><strong>आय प्रमाण (Income Proof):</strong> शासकीय/निजी वेतन पर्ची, कृषि खसरा बी-1 खतौनी, अथवा नियोक्ता प्रमाण पत्र।</li>
              <li><strong>राशन कार्ड (Ration Card):</strong> समग्र पोर्टल से लिंक अंत्योदय (AAY), बीपीएल (BPL) अथवा एपीएल (APL) कार्ड।</li>
              <li><strong>स्व-घोषणा पत्र (Self Declaration):</strong> मध्य प्रदेश शासन के विहित प्रारूप में हस्ताक्षरित/नोटरीकृत शपथ पत्र।</li>
              <li><strong>बैंक पासबुक/विवरण (Bank Statement):</strong> आवेदक के नाम से पिछले 6 माह का बैंक खाता विवरण।</li>
            </ol>
          </div>
        </div>

        {/* Card 2: AI Assistant & Human Decision Philosophy */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--gov-navy-900)', marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Scale size={18} style={{ color: 'var(--gov-navy-600)' }} />
            <span>नियम-आधारित सत्यापन बनाम AI सहायता (Deterministic Rules vs LLM)</span>
          </h2>

          <div style={{ fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ background: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <strong>1. नियम-आधारित सत्यापन (Deterministic Rule Engine):</strong><br />
              दस्तावेज़ों की गिनती, तारीखों की वैधता, और आय की गणितीय विसंगति 100% सटीक पाइथन नियमों द्वारा जांचे जाते हैं। AI को इस गणितीय गणना में शामिल नहीं किया जाता ताकि किसी भी 'Hallucination' से बचा जा सके।
            </div>

            <div style={{ background: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <strong>2. AI समीक्षा (Groq LLM Layer):</strong><br />
              Groq API (Llama 3.1) का उपयोग केवल जटिल केस को मानवीय हिंदी में संक्षेप करने, साक्ष्य प्रस्तुत करने तथा प्रारंभिक सुझाव देने के लिए किया जाता है।
            </div>

            <div style={{ background: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <strong>3. मानव-नियंत्रण (Human-in-the-Loop):</strong><br />
              AI के पास डेटाबेस में आवेदन की स्थिति बदलने का अधिकार नहीं है। केवल अधिकृत तहसीलदार/राजस्व अधिकारी ही अनिवार्य टिप्पणी अंकित करके और पुष्टि के उपरांत डिजिटल हस्ताक्षर से आदेश जारी कर सकते हैं।
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
