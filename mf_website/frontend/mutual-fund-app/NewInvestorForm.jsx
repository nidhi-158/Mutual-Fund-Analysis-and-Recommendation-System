import React, { useState } from 'react';
import axios from 'axios';


const NewInvestorForm = () => {
  const [form, setForm] = useState({
    budget: '',
    risk_level: '',
    asset_class: '',
    market_cap: ''
  });


  const [results, setResults] = useState([]);
  const [error, setError] = useState("");


  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResults([]);
    try {
      const res = await axios.post("http://localhost:8000/recommend/new", form);
      if (res.data.message) {
        setError(res.data.message);
      } else {
        setResults(res.data);
      }
    } catch (err) {
      setError("❌ Failed to fetch recommendations.");
    }
  };


  return (
    <div className="container">
      <h2>📊 New Investor Recommendation</h2>
      <form onSubmit={handleSubmit}>
        <label>Budget:</label>
        <input
          type="number"
          name="budget"
          value={form.budget}
          onChange={handleChange}
          required
        />


        <label>Risk Level:</label>
        <select
          name="risk_level"
          value={form.risk_level}
          onChange={handleChange}
          required
        >
          <option value="">-- Select --</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>


        <label>Asset Class:</label>
        <select
          name="asset_class"
          value={form.asset_class}
          onChange={handleChange}
        >
          <option value="">-- Optional --</option>
          <option value="Equity">Equity</option>
          <option value="Debt">Debt</option>
          <option value="Hybrid">Hybrid</option>
          <option value="Gold">Gold</option>
          <option value="Liquid">Liquid</option>
          <option value="Other">Other</option>
          <option value="Index/ETF">Index/ETF</option>
          <option value="Specialized">Specialized</option>
        </select>


        <label>Market Cap:</label>
        <select
          name="market_cap"
          value={form.market_cap}
          onChange={handleChange}
        >
          <option value="">-- Optional --</option>
          <option value="Large Cap">Large Cap</option>
          <option value="Mid Cap">Mid Cap</option>
          <option value="Small Cap">Small Cap</option>
          <option value="Multi Cap">Multi Cap</option>
          <option value="Focused/Value">Focused/Value</option>
          <option value="Sectoral/Thematic">Sectoral/Thematic</option>
          <option value="Mid/Small Cap">Mid/Small Cap</option>
          <option value="Other">Other</option>
        </select>


        <button type="submit">Get Recommendations</button>
      </form>


      {error && <p style={{ color: 'red' }}>{error}</p>}


      {results.length > 0 && (
        <div className="result-box">
          <h3 style={{ marginBottom: '16px' }}>📊 Recommended Funds</h3>
          <table className="fund-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Scheme Name (ID)</th>
                <th>NAV (₹)</th>
                <th>Units</th>
              </tr>
            </thead>
            <tbody>
              {results.map((fund, index) => (
                <tr key={index}>
                  <td>{index + 1}</td>
                  <td>{`${fund.Scheme_Name} (ID: ${fund.SchemeID})`}</td>
                  <td>{parseFloat(fund.NAV).toFixed(2)}</td>
                  <td>{fund.Units_Purchasable}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};


export default NewInvestorForm;
