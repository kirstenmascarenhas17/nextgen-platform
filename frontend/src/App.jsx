import { useState, useEffect } from 'react'
import logoImg from './assets/logo.jpg'
import './App.css'
import AiChatWidget from './components/AiChatWidget';

import { FaFacebook, FaInstagram, FaLinkedin, FaWhatsapp, FaPhoneAlt, FaEnvelope, FaArrowUp, FaMapMarkerAlt } from 'react-icons/fa';
import { IoCheckmarkCircle } from 'react-icons/io5';

const COUNTRY_INFO = [
  { 
    name: 'UAE', 
    info: 'Booming sectors in Construction, Tech, and Retail.', 
    url: 'https://en.wikipedia.org/wiki/United_Arab_Emirates' 
  },
  { 
    name: 'Singapore', 
    info: 'High demand for Shipyard, Maritime, and Hospitality staff.', 
    url: 'https://en.wikipedia.org/wiki/Singapore' 
  }
];

function App() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    preferred_country: ''
  });

  const [statusMessage, setStatusMessage] = useState('');
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 300) {
        setShowScrollTop(true);
      } else {
        setShowScrollTop(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handlePhoneChange = (e) => {
    const cleanValue = e.target.value.replace(/\D/g, '');
    if (cleanValue.length <= 10) {
      setFormData({ ...formData, phone_number: cleanValue });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); 

    const phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(formData.phone_number)) {
      setStatusMessage('Error: Please enter a valid 10-digit Indian phone number starting with 6, 7, 8, or 9.');
      return; 
    }

    setStatusMessage('Sending...');

    try {
      const response = await fetch('https://nextgen-api-11jg.onrender.com/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setStatusMessage('Success! Your profile has been registered.');
        setFormData({ full_name: '', email: '', phone_number: '', preferred_country: '' });
      } else {
        setStatusMessage(`Error: ${data.detail}`);
      }
    } catch (error) {
      console.error("Connection error:", error);
      setStatusMessage('Error connecting to the server. Is the backend running?');
    }
  };

  return (
    <div className="app-container" id="home">
      
      <header className="navbar sticky-header">
        <div className="logo-section">
          <img src={logoImg} alt="NextGen Consultancy Logo" className="main-logo" />
          <div className="logo-text">
            <h1 className="company-name">NextGen Consultancy</h1>
          </div>
        </div>
        
        <nav className="desktop-nav">
          <a href="#home">Home</a>
          <a href="#about">About Us</a>
          <a href="#services">Services</a>
          <a href="#contact">Contact Us</a>
          <a href="#register" className="nav-register-btn">Candidate Registration</a>
        </nav>
      </header>
      
      <main className="main-layout">
        <aside className="sidebar">
          <h2>Explore Destinations</h2>
          <p className="sidebar-subtitle">Click to learn more about living and working abroad.</p>
          
          <div className="country-link-list">
            {COUNTRY_INFO.map((country) => (
              <a 
                key={country.name} 
                href={country.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="country-info-card"
              >
                <h3>{country.name} <span className="link-icon">↗</span></h3>
                <p>{country.info}</p>
              </a>
            ))}
          </div>
        </aside>

        <section className="content-area home-page-layout">
          
          <div className="hero-text" id="about">
            <h2>Your Global Career Starts Here.</h2>
            <p>Over a Decade of Global Connections. NextGen Consultancy connects Indian talent with premium international employers. Register your profile today, and our placement team will match you with the perfect opportunity.</p>
          </div>

          <div className="trust-ribbon" id="services">
            <p>Specialized Placement Pathways For:</p>
            <div className="trust-badges" style={{ flexWrap: 'wrap', gap: '15px' }}>
              <span><IoCheckmarkCircle className="check-icon" /> Israel</span>
              <span><IoCheckmarkCircle className="check-icon" /> Portugal</span>
              <span><IoCheckmarkCircle className="check-icon" /> Greece</span>
              <span><IoCheckmarkCircle className="check-icon" /> Austria</span>
              <span><IoCheckmarkCircle className="check-icon" /> UAE</span>
            </div>
          </div>

          <div className="registration-section central-form" id="register">
            <h2>Candidate Registration</h2>
            <p>Secure your spot in our global database.</p>
            <p style={{ fontSize: '13px', color: '#666', marginBottom: '15px' }}>
              *Age limits strictly apply (typically 21–48 depending on region). Candidates must possess basic English proficiency and verifiable domain experience.
            </p>
            
            <form className="apply-form" onSubmit={handleSubmit}>
              <input type="text" name="full_name" placeholder="Full Name" value={formData.full_name} onChange={handleInputChange} required />
              <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleInputChange} required />
              
              <input type="tel" name="phone_number" placeholder="Phone Number (Required)" value={formData.phone_number} onChange={handlePhoneChange} required />
              
              <select name="preferred_country" className="country-dropdown" value={formData.preferred_country} onChange={handleInputChange} required>
                <option value="" disabled>Select Preferred Country...</option>
                <option value="Israel">Israel</option>
                <option value="Europe">Europe (Portugal, Greece, Austria, etc.)</option>
                <option value="UAE">United Arab Emirates (UAE)</option>
                <option value="Singapore">Singapore</option>
                <option value="Any">Open to Any Location</option>
              </select>

              <button type="submit">Submit Profile</button>
              {statusMessage && <p className="status-msg">{statusMessage}</p>}
            </form>
          </div>
        </section>
      </main>

      <footer className="premium-footer" id="contact">
        <div 
          className="footer-grid" 
          style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', 
            gap: '30px', 
            alignItems: 'start' 
          }}
        >
          
          {/* Column 1: Brand Info */}
          <div className="footer-col">
            <h3>NextGen Consultancy</h3>
            <p>Your Gateway to Global Careers.</p>
            <p style={{ fontSize: '14px', marginTop: '10px' }}>Overseas Recruitment | Visa Documentation Support | Skills Verification | Pre-Interview Mock Training</p>
          </div>

          {/* Column 2: Offices (Combined) */}
          <div className="footer-col">
            <h3>Our Offices</h3>
            
            <h4 style={{ fontSize: '14px', marginBottom: '5px', color: '#38bdf8', fontWeight: 'bold' }}>Head Office</h4>
            <p style={{ fontSize: '14px', marginBottom: '15px', lineHeight: '1.6' }}>
              <FaMapMarkerAlt size={14} style={{ marginRight: '8px', color: '#38bdf8', verticalAlign: 'top', marginTop: '3px' }} /> 
              <span style={{ display: 'inline-block', width: '85%' }}>
                21/165, Jyoti Cottage, Old Anand Nagar Lane, Behind Vakola Police Station, Above Dyandeep Bank, Santacruz East, Mumbai - 400055
              </span>
            </p>

            <h4 style={{ fontSize: '14px', marginBottom: '5px', color: '#38bdf8', fontWeight: 'bold' }}>Branch Office</h4>
            <p style={{ fontSize: '14px', marginBottom: '15px', lineHeight: '1.6' }}>
              <FaMapMarkerAlt size={14} style={{ marginRight: '8px', color: '#38bdf8', verticalAlign: 'top', marginTop: '3px' }} /> 
              <span style={{ display: 'inline-block', width: '85%' }}>
                Shop No 2, A Wing, Krishna Prestige, MIDC Road, Opp Krishna Garden, Mira Road East, Thane - 401107
              </span>
            </p>
          </div>

          {/* Column 3: Contact Info */}
          <div className="footer-col">
            <h3>Contact Us</h3>
            <div style={{ marginBottom: '15px' }}>
              <p style={{ fontSize: '14px', marginBottom: '12px' }}>
                <FaPhoneAlt size={12} style={{ marginRight: '8px', color: '#38bdf8' }} /> +91 9076011522 / +91 9076011499
              </p>
              <p style={{ fontSize: '14px', marginBottom: '12px' }}>
                <FaPhoneAlt size={12} style={{ marginRight: '8px', color: '#38bdf8' }} /> +91 9076012125 / +91 9076011175
              </p>
              <p style={{ fontSize: '14px', marginBottom: '12px' }}>
                <a href="mailto:careers@nextgen-consultancy.net" style={{ color: 'inherit', textDecoration: 'none' }}>
                  <FaEnvelope size={12} style={{ marginRight: '8px', color: '#38bdf8' }} /> careers@nextgen-consultancy.net
                </a>
              </p>
              <p style={{ fontSize: '14px' }}>
                <a href="mailto:info.nextgenconsultancy1@gmail.com" style={{ color: 'inherit', textDecoration: 'none' }}>
                  <FaEnvelope size={12} style={{ marginRight: '8px', color: '#38bdf8' }} /> info.nextgenconsultancy1@gmail.com
                </a>
              </p>
            </div>
          </div>

          {/* Column 4: Social Links */}
          <div className="footer-col">
            <h3>Follow Us</h3>
            {/* Stacked vertically with text */}
            <div className="social-links" style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
              <a href="https://www.facebook.com/share/14aEPTxdTQg/" target="_blank" rel="noopener noreferrer" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', fontSize: '15px' }}>
                <FaFacebook size={20} style={{ marginRight: '10px' }} /> Facebook
              </a>
              <a href="https://www.instagram.com/info.nextgen?igsh=MWs3aGF1NjZhdGJ6aw==" target="_blank" rel="noopener noreferrer" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', fontSize: '15px' }}>
                <FaInstagram size={20} style={{ marginRight: '10px' }} /> Instagram
              </a>
              <a href="https://www.linkedin.com/in/nextgen-consultancy-430269397" target="_blank" rel="noopener noreferrer" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', fontSize: '15px' }}>
                <FaLinkedin size={20} style={{ marginRight: '10px' }} /> LinkedIn
              </a>
            </div>
          </div>

        </div>
        <div className="footer-bottom" style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <p>&copy; 2026 NextGen Consultancy. All rights reserved.</p>
        </div>
      </footer>

      <a href="https://wa.me/919076011175?text=Hi!%20I%20am%20interested%20in%20global%20job%20opportunities%20with%20NextGen." target="_blank" rel="noopener noreferrer" className="floating-whatsapp">
        <FaWhatsapp size={24} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
        WhatsApp Us
      </a>

      {showScrollTop && (
        <button onClick={scrollToTop} className="scroll-to-top">
          <FaArrowUp size={18} />
        </button>
      )}

      <AiChatWidget />
    </div>
  )
}

export default App