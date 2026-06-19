import { useState, useEffect, useRef } from 'react'
import logoImg from './assets/logo.jpg'
import './App.css'
import AiChatWidget from './components/AiChatWidget';

import { FaFacebook, FaInstagram, FaLinkedin, FaWhatsapp, FaPhoneAlt, FaEnvelope, FaArrowUp, FaMapMarkerAlt, FaShip, FaOilCan, FaHardHat, FaPowerOff, FaHotel, FaHeartbeat, FaLaptopCode, FaTruckLoading, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import { IoCheckmarkCircle, IoCheckmarkDoneCircle } from 'react-icons/io5';

const SERVICES_INFO = [
  { 
    id: 'oil-gas',
    icon: <FaOilCan />,
    title: 'Oil and Gas', 
    image: 'https://images.unsplash.com/photo-1516937941344-00b4e0337589?auto=format&fit=crop&q=80&w=1200',
    description: "NextGen Consultancy specializes in providing highly skilled and semi-skilled manpower for the global Oil and Gas sector. From rig operations to refinery maintenance, our candidates are rigorously vetted to ensure they meet stringent international safety and technical standards. We provide Riggers, Welders, Safety Officers, and Petroleum Engineers."
  },
  { 
    id: 'construction',
    icon: <FaHardHat />,
    title: 'Construction', 
    image: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&q=80&w=1200',
    description: "Our expertise in the Construction sector ensures that large-scale infrastructure projects are staffed with competent professionals. We recruit top-tier civil engineers, heavy equipment operators, masons, carpenters, and project managers who are experienced in executing high-value international projects efficiently."
  },
  { 
    id: 'marine-shipping',
    icon: <FaShip />,
    title: 'Marine & Shipping', 
    image: 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?auto=format&fit=crop&q=80&w=1200',
    description: "We connect maritime employers with certified and experienced shipping personnel. Our marine placement division focuses on sourcing skilled seafarers, marine engineers, deck officers, and shipyard workers who comply with all international maritime regulations and possess a strong track record of safety at sea."
  },
  { 
    id: 'power-plants',
    icon: <FaPowerOff />,
    title: 'Power Plants', 
    image: 'https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&q=80&w=1200',
    description: "Power generation requires precise technical expertise. We supply the energy sector with qualified electrical engineers, mechanical technicians, turbine operators, and maintenance crews. Our candidates have extensive experience in working within thermal, nuclear, and renewable energy power plants."
  },
  { 
    id: 'hospitality',
    icon: <FaHotel />,
    title: 'Hospitality', 
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=1200',
    description: "Supporting the global tourism boom, we provide skilled manpower for luxury hotels, resorts, and cruise liners. Our placement officers vet Chefs, Housekeeping staff, Front Office managers, and F&B supervisors, primarily for clients in UAE, Malta, and Europe."
  },
  { 
    id: 'healthcare',
    icon: <FaHeartbeat />,
    title: 'Healthcare', 
    image: 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=1200',
    description: "We help international hospitals and clinics secure dedicated medical professionals from India. We specialize in placing Nurses, Lab Technicians, Radiologists, and specialized doctors who hold internationally recognized certifications."
  },
  { 
    id: 'it-telecom',
    icon: <FaLaptopCode />,
    title: 'IT & Telecom', 
    image: 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&q=80&w=1200',
    description: "Bridging the global tech gap, we recruit top Indian IT talent for roles abroad. Our candidates include Software Developers, Network Engineers, Cybersecurity analysts, and Data Scientists experienced in modern tech stacks."
  },
  { 
    id: 'logistics',
    icon: <FaTruckLoading />,
    title: 'Logistics', 
    image: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=1200',
    description: "Ensuring global supply chains run smoothly, we source reliable personnel for logistics hubs. We provide Warehouse Managers, Forklift Operators, Supply Chain coordinators, and heavy-duty drivers for Middle Eastern and European clients."
  }
];

function App() {
  const [formData, setFormData] = useState({
    full_name: '', email: '', phone_number: '', preferred_country: ''
  });
  const [statusMessage, setStatusMessage] = useState('');
  const [showScrollTop, setShowScrollTop] = useState(false);

  const [currentView, setCurrentView] = useState('home'); 
  const carouselRef = useRef(null);

  // ✨ NEW: Admin Dashboard States
  const [adminPassword, setAdminPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [candidatesList, setCandidatesList] = useState([]);
  const [adminError, setAdminError] = useState('');

  useEffect(() => {
    const handleScroll = () => setShowScrollTop(window.scrollY > 300);
    window.addEventListener('scroll', handleScroll);

    let scrollInterval;
    if (currentView === 'home') {
      scrollInterval = setInterval(() => {
        if (carouselRef.current) {
          const { scrollLeft, scrollWidth, clientWidth } = carouselRef.current;
          if (scrollLeft + clientWidth >= scrollWidth - 10) {
            carouselRef.current.scrollTo({ left: 0, behavior: 'smooth' });
          } else {
            carouselRef.current.scrollBy({ left: 300, behavior: 'smooth' }); 
          }
        }
      }, 3000); 
    }

    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (scrollInterval) clearInterval(scrollInterval);
    };
  }, [currentView]);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  // Navigation Handlers
  const navigateToHome = (e) => {
    if(e) e.preventDefault();
    setCurrentView('home');
    window.scrollTo(0, 0);
  };

  const navigateToAbout = (e) => {
    if(e) e.preventDefault();
    setCurrentView('about');
    window.scrollTo(0, 0);
  };

  const navigateToServices = (service, e) => {
    if(e) e.preventDefault();
    setCurrentView('services');
    
    setTimeout(() => {
      if (service && service.id) {
        const element = document.getElementById(service.id);
        if (element) {
          const headerOffset = 80;
          const elementPosition = element.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
          window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
      } else {
        window.scrollTo(0, 0);
      }
    }, 100);
  };

  const scrollToService = (id, e) => {
    if(e) e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      const headerOffset = 80;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
      window.scrollTo({ top: offsetPosition, behavior: "smooth" });
    }
  };

  const scrollToContact = (e) => {
    if(e) e.preventDefault();
    const footer = document.getElementById('contact');
    if(footer) {
      window.scrollTo({ top: footer.offsetTop, behavior: 'smooth' });
    }
  };

  const navigateToRegistration = (e) => {
    if(e) e.preventDefault();
    setCurrentView('home');
    
    setTimeout(() => {
      const element = document.getElementById('register');
      if (element) {
        const headerOffset = 80;
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        window.scrollTo({ top: offsetPosition, behavior: "smooth" });
      }
    }, 100);
  };

  // ✨ NEW: The Admin Login Handler
  const handleAdminLogin = async (e) => {
    e.preventDefault();
    setAdminError('Authenticating...');
    try {
      const response = await fetch(`https://nextgen-api-11jg.onrender.com/admin/candidates?secret=${adminPassword}`);
      if (response.ok) {
        const data = await response.json();
        setCandidatesList(data.candidates);
        setIsAuthenticated(true);
        setAdminError('');
      } else {
        setAdminError('Incorrect PIN. Access Denied.');
      }
    } catch (error) {
      setAdminError('Error connecting to the secure server.');
    }
  };

  const scrollLeft = () => {
    if (carouselRef.current) carouselRef.current.scrollBy({ left: -300, behavior: 'smooth' });
  };
  const scrollRight = () => {
    if (carouselRef.current) carouselRef.current.scrollBy({ left: 300, behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handlePhoneChange = (e) => {
    const cleanValue = e.target.value.replace(/\D/g, '');
    if (cleanValue.length <= 10) setFormData({ ...formData, phone_number: cleanValue });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); 
    const phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(formData.phone_number)) {
      setStatusMessage('Error: Please enter a valid 10-digit Indian phone number.');
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
      setStatusMessage('Error connecting to the server.');
    }
  };

  return (
    <div className="app-container" id="home">
      
      <header className="navbar sticky-header">
        <div className="logo-section" onClick={navigateToHome} style={{ cursor: 'pointer' }}>
          <img src={logoImg} alt="NextGen Consultancy Logo" className="main-logo" />
          <div className="logo-text">
            <h1 className="company-name">NextGen Consultancy</h1>
          </div>
        </div>
        
        <nav className="desktop-nav">
          <a onClick={navigateToHome}>Home</a>
          <a onClick={navigateToAbout}>About Us</a>
          <a onClick={(e) => navigateToServices(null, e)}>Services</a>
          <a onClick={scrollToContact}>Contact Us</a> 
          <a onClick={navigateToRegistration} className="nav-register-btn">Candidate Registration</a> 
        </nav>
      </header>
      
      <main className="main-layout">
        
        {/* =========================================
             HOME PAGE VIEW
           ========================================= */}
        {currentView === 'home' && (
          <>
            <section className="home-hero-section">
              <div className="home-hero-overlay"></div>
              <div className="hero-text" id="home-hero">
                <h2>Your Global Career Starts Here.</h2>
                <p>Over a Decade of Global Connections. NextGen Consultancy connects Indian talent with premium international employers. Register your profile today, and our placement team will match you with the perfect opportunity.</p>
              </div>
            </section>

            <section className="content-area home-page-layout">
              <div className="trust-ribbon" style={{ marginBottom: '50px', marginTop: '-60px', position: 'relative', zIndex: 10 }}>
                <p>Specialized Placement Pathways For:</p>
                <div className="trust-badges" style={{ flexWrap: 'wrap', gap: '15px', justifyContent: 'center' }}>
                  <span><IoCheckmarkCircle className="check-icon" /> Israel</span>
                  <span><IoCheckmarkCircle className="check-icon" /> Portugal</span>
                  <span><IoCheckmarkCircle className="check-icon" /> Greece</span>
                  <span><IoCheckmarkCircle className="check-icon" /> Austria</span>
                  <span><IoCheckmarkCircle className="check-icon" /> UAE</span>
                </div>
              </div>

              <div id="services" className="services-section">
                <h2>Our Services</h2>
                
                <div className="carousel-wrapper">
                  <button className="scroll-arrow left" onClick={scrollLeft}><FaChevronLeft /></button>
                  
                  <div className="services-grid" ref={carouselRef}>
                    {SERVICES_INFO.map((service, index) => (
                      <div key={index} className="service-card" onClick={(e) => navigateToServices(service, e)}>
                        <img src={service.image} alt={service.title} className="service-image" />
                        <div className="service-overlay"></div>
                        <h3 className="service-title">{service.title}</h3>
                      </div>
                    ))}
                  </div>

                  <button className="scroll-arrow right" onClick={scrollRight}><FaChevronRight /></button>
                </div>
              </div>

              <div className="registration-section central-form" id="register" style={{ marginTop: '60px' }}>
                <h2>Candidate Registration</h2>
                <p>Secure your spot in our global database.</p>
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
          </>
        )}

        {/* =========================================
             SERVICES DETAIL VIEW
           ========================================= */}
        {currentView === 'services' && (
          <section className="services-page-layout">
            <aside className="services-sidebar">
              <h2 className="sidebar-header">Job Sectors</h2>
              <div className="sidebar-links-container">
                {SERVICES_INFO.map((service) => (
                  <button 
                    key={service.id} 
                    className="sidebar-tab"
                    onClick={(e) => scrollToService(service.id, e)}
                  >
                    <span className="sidebar-icon">{service.icon}</span> 
                    {service.title}
                  </button>
                ))}
              </div>
            </aside>
            <div className="services-main-content">
              {SERVICES_INFO.map((service) => (
                <div id={service.id} key={service.id} className="service-detail-block">
                  <div className="service-header-row">
                    <div className="header-icon">{service.icon}</div>
                    <h2>{service.title}</h2>
                  </div>
                  <img src={service.image} alt={service.title} />
                  <p>{service.description}</p>
                  <div className="detail-divider"></div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* =========================================
             ABOUT US PAGE VIEW
           ========================================= */}
        {currentView === 'about' && (
          <section className="about-page-layout">
            <div className="about-hero">
              <img 
                src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80&w=2000" 
                alt="NextGen Team" 
                className="about-hero-image" 
              />
              <div className="about-hero-overlay"></div>
              <h1 className="about-hero-title">About Us</h1> 
            </div>

            <div className="about-content">
              <div className="about-text-block">
                <h2>Our Mission</h2>
                <p>NextGen Consultancy was founded with a singular vision: to bridge the gap between world-class international employers and the incredibly driven talent pool in India. For over a decade, we have dedicated ourselves to changing lives by providing secure, verified, and highly lucrative overseas career opportunities.</p>
              </div>
              <div className="about-text-block">
                <h2>Why Choose Us?</h2>
                <ul className="about-list">
                  <li><IoCheckmarkDoneCircle className="about-check" /> <strong>Verified Employers:</strong> We only partner with recognized international companies, ensuring your safety and career growth.</li>
                  <li><IoCheckmarkDoneCircle className="about-check" /> <strong>End-to-End Support:</strong> From pre-interview training to visa documentation, our team guides you through every step.</li>
                  <li><IoCheckmarkDoneCircle className="about-check" /> <strong>Global Reach:</strong> Specialized pathways into Europe, Israel, UAE, and Singapore across 8+ major industrial sectors.</li>
                </ul>
              </div>
              <div className="about-text-block">
                <h2>Our Story</h2>
                <p>What started as a small recruitment desk in Mumbai has grown into a trusted international placement agency. We have successfully placed thousands of candidates in roles ranging from heavy construction to luxury hospitality. Our success is built entirely on trust, transparency, and a relentless commitment to our candidates' futures.</p>
              </div>
            </div>
          </section>
        )}

        {/* =========================================
             ✨ NEW: HIDDEN ADMIN DASHBOARD
           ========================================= */}
        {currentView === 'admin' && (
          <section style={{ minHeight: '60vh', padding: '60px 20px', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
            <h2 style={{ textAlign: 'center', color: '#0c4a6e', marginBottom: '30px', fontSize: '2.5rem' }}>Admin Control Panel</h2>
            
            {!isAuthenticated ? (
              <div style={{ maxWidth: '400px', margin: '0 auto', background: 'white', padding: '40px', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }}>
                <p style={{textAlign: 'center', marginBottom: '25px', color: '#475569'}}>Enter secure PIN to access candidate database.</p>
                <form onSubmit={handleAdminLogin} style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
                  <input 
                    type="password" 
                    placeholder="Enter Security PIN" 
                    value={adminPassword} 
                    onChange={(e) => setAdminPassword(e.target.value)} 
                    style={{padding: '15px', borderRadius: '8px', border: '1px solid #ccc', fontSize: '1.1rem'}}
                  />
                  <button type="submit" style={{background: '#0ea5e9', color: 'white', padding: '15px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: 'bold', fontSize: '1.1rem'}}>
                    Authenticate
                  </button>
                </form>
                {adminError && <p style={{color: '#ef4444', textAlign: 'center', marginTop: '20px', fontWeight: 'bold'}}>{adminError}</p>}
              </div>
            ) : (
              <div style={{ overflowX: 'auto', background: 'white', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.05)', padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3 style={{ color: '#0ea5e9', margin: 0 }}>Total Registered Candidates: {candidatesList.length}</h3>
                  <button onClick={() => {setIsAuthenticated(false); setAdminPassword('');}} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '6px', cursor: 'pointer' }}>Lock Dashboard</button>
                </div>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ background: '#f0f9ff', color: '#0c4a6e' }}>
                      <th style={{ padding: '15px', borderBottom: '2px solid #bae6fd' }}>Name</th>
                      <th style={{ padding: '15px', borderBottom: '2px solid #bae6fd' }}>Email</th>
                      <th style={{ padding: '15px', borderBottom: '2px solid #bae6fd' }}>Phone</th>
                      <th style={{ padding: '15px', borderBottom: '2px solid #bae6fd' }}>Preferred Location</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidatesList.length === 0 ? (
                      <tr><td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>No candidates found in the database.</td></tr>
                    ) : (
                      candidatesList.map((c, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '15px', fontWeight: 'bold', color: '#334155' }}>{c.full_name}</td>
                          <td style={{ padding: '15px', color: '#475569' }}>{c.email}</td>
                          <td style={{ padding: '15px', color: '#475569' }}>{c.phone_number}</td>
                          <td style={{ padding: '15px' }}>
                            <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '5px 10px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 'bold' }}>
                              {c.preferred_country}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

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
          <div className="footer-col">
            <h3>NextGen Consultancy</h3>
            <p>Your Gateway to Global Careers.</p>
            <p style={{ fontSize: '14px', marginTop: '10px' }}>Overseas Recruitment | Visa Documentation Support | Skills Verification | Pre-Interview Mock Training</p>
          </div>
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
          <div className="footer-col">
            <h3>Follow Us</h3>
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
          {/* ✨ NEW: The Secret Admin Door (Click the copyright text!) */}
          <p 
            onClick={() => {setCurrentView('admin'); window.scrollTo(0,0);}} 
            style={{ cursor: 'pointer', display: 'inline-block' }}
          >
            &copy; 2026 NextGen Consultancy. All rights reserved.
          </p>
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