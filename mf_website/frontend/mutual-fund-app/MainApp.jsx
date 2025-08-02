import React, { useState } from 'react';
import NewInvestorForm from './NewInvestorForm';
import ExistingInvestorForm from './ExistingInvestorForm';
import './styles.css';
import { useNavigate } from 'react-router-dom';

const MainApp = () => {
  const [userType, setUserType] = useState('new');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <div className="page-wrapper">
      {/* Header without outer container */}
      <div className="header-strip">
        <h2>🎯 Mutual Fund Recommendation</h2>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </div>

      {/* Toggle */}
      <div className="toggle-container">
        <label>
          <input
            type="radio"
            name="userType"
            value="new"
            checked={userType === 'new'}
            onChange={() => setUserType('new')}
          /> New Investor
        </label>
        <label style={{ marginLeft: '20px' }}>
          <input
            type="radio"
            name="userType"
            value="existing"
            checked={userType === 'existing'}
            onChange={() => setUserType('existing')}
          /> Existing Investor
        </label>
      </div>

      {/* Form based on user type */}
      {userType === 'new' ? <NewInvestorForm /> : <ExistingInvestorForm />}
    </div>
  );
};

export default MainApp;
