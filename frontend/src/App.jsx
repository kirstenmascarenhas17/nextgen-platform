import { useState } from 'react'
import logoImg from './assets/logo.jpg'
import './App.css'
import AiChatWidget from './components/AiChatWidget';

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
  },
  { 
    name: 'Malta', 
    info: 'Fast-track visas for Healthcare and Logistics drivers.', 
    url: 'https://en.wikipedia.org/wiki/Malta' 
  }
];

function App() {
  // --- THE BRAIN: Memory (State) and Logic (Functions) ---
  
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    preferred_country: ''
  });

  const [statusMessage, setStatusMessage] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); 
    setStatusMessage('Sending...');

    try {
      // ✨ THE FIX: Pointing React to your live Render Cloud Engine!
      const response = await fetch('https://nextgen-api-11jg.onrender.com/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setStatusMessage('Success! Your profile has been registered.');
        setFormData({ full_name: '', email: '', phone_number: '', preferred_country: '' }); // Clears form
      } else {
        setStatusMessage(`Error: ${data.detail}`);
      }
    } catch (error) {
      console.error("Connection error:", error);
      setStatusMessage('Error connecting to the server. Is the backend running?');
    }
  };

  // --- THE FACE: What the user actually sees (HTML/JSX) ---
  return (
    <div className="app-container">
      <header className="navbar">
        <div className="logo-section">
          <img src={logoImg} alt="NextGen Consultancy Logo" className="main-logo" />
          <div className="logo-text">
            <h1 className="company-name">NextGen Consultancy</h1>
            <p className="brand-tagline">Adding Value to Lives!</p>
          </div>
        </div>
        <p className="contact-header">Call Us: +91 98765 43210 | email: jobs@nextgen.com</p>
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
          <div className="hero-text">
            <h2>Your Global Career Starts Here.</h2>
            <p>We connect skilled professionals with verified employers across the globe. Register your profile today, and our placement team will match you with the perfect opportunity.</p>
          </div>

          <div className="registration-section central-form">
            <h2>Candidate Registration</h2>
            <p>Secure your spot in our global database.</p>
            
            <form className="apply-form" onSubmit={handleSubmit}>
              <input 
                type="text" 
                name="full_name"
                placeholder="Full Name" 
                value={formData.full_name}
                onChange={handleInputChange}
                required 
              />
              <input 
                type="email" 
                name="email"
                placeholder="Email Address" 
                value={formData.email}
                onChange={handleInputChange}
                required 
              />
              <input 
                type="tel" 
                name="phone_number"
                placeholder="Phone Number (Required)" 
                value={formData.phone_number}
                onChange={handleInputChange}
                required 
              />
              
              <select 
                name="preferred_country"
                className="country-dropdown"
                value={formData.preferred_country}
                onChange={handleInputChange}
                required
              >
                <option value="" disabled>Select Preferred Country...</option>
                <option value="UAE">United Arab Emirates (UAE)</option>
                <option value="Singapore">Singapore</option>
                <option value="Malta">Malta</option>
                <option value="Any">Open to Any Location</option>
              </select>

              <button type="submit">Submit Profile</button>
              
              {statusMessage && <p style={{ marginTop: '10px', color: '#03a9f4', fontWeight: 'bold' }}>{statusMessage}</p>}
            </form>
          </div>
        </section>

      </main>
      <AiChatWidget />
    </div>
  )
}

export default App