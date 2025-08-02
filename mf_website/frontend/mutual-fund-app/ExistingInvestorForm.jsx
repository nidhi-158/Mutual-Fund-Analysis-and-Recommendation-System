import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';


const ExistingInvestorForm = () => {
  const [form, setForm] = useState({
    scheme_id: '',
    nav_at_purchase: '',
    units_held: '',
    purchase_date: ''
  });


  const [schemeOptions, setSchemeOptions] = useState([]);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");


  // 🔁 Fetch all available schemes on page load
  useEffect(() => {
    axios.get("http://localhost:8000/schemes")
      .then(res => {
        const options = res.data.map(s => ({
          value: s.SchemeID,
          label: s.Scheme
        }));
        setSchemeOptions(options);
      })
      .catch(err => {
        console.error("❌ Failed to fetch scheme list", err);
      });
  }, []);


  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setError("");


    try {
      const res = await axios.post("http://localhost:8000/recommend/existing", form);
      if (res.data.error) {
        setError(res.data.error);
        setResult(null);
      } else {
        setResult(res.data);
        setError("");
      }
    } catch (err) {
      console.error("❌ Recommendation API failed", err);
      setError("❌ Failed to fetch recommendation.");
      setResult(null);
    }
  };


  return (
    <div className="container">
      <h2>🧾 Existing Investor Analysis</h2>


      <form onSubmit={handleSubmit}>
        <label>Select Scheme Name:</label>
        <Select
          options={schemeOptions}
          value={selectedScheme}
          onChange={(selected) => {
            setSelectedScheme(selected);
            setForm({ ...form, scheme_id: selected.value });
          }}
          placeholder="Search scheme..."
          isSearchable
        />


        <label>NAV at Purchase:</label>
        <input
          type="number"
          name="nav_at_purchase"
          value={form.nav_at_purchase}
          onChange={handleChange}
          required
        />


        <label>Units Held:</label>
        <input
          type="number"
          name="units_held"
          value={form.units_held}
          onChange={handleChange}
          required
        />


        <label>Purchase Date:</label>
        <input
          type="date"
          name="purchase_date"
          value={form.purchase_date}
          onChange={handleChange}
          required
        />


        <button type="submit">Analyze</button>
      </form>


      {/* Show only actual error */}
      {error && <p style={{ color: 'red' }}>{error}</p>}


      {/* Show results only if valid */}
      {result && (
        <div className="result-box">
          <h3>📊 Analysis Result</h3>
          <table className="result-table">
            <tbody>
              <tr>
                <td><strong>Current Fund ID:</strong></td>
                <td>{result?.Your_Fund?.SchemeID ?? "-"}</td>
              </tr>
              <tr>
                <td><strong>Scheme Name:</strong></td>
                <td>{result?.Your_Fund?.Scheme ?? "-"}</td>
              </tr>
              <tr>
                <td><strong>NAV at Purchase:</strong></td>
                <td>₹{result?.Your_Fund?.NAV_at_Purchase ?? "-"}</td>
              </tr>
              <tr>
                <td><strong>Latest NAV:</strong></td>
                <td>₹{result?.Your_Fund?.Current_NAV ?? "-"}</td>
              </tr>
              <tr>
                <td><strong>Top Similar Fund:</strong></td>
                <td>{result?.Recommended_Fund?.Recommended_Scheme ?? "N/A"}</td>
              </tr>
              <tr>
                <td><strong>📢 Recommendation:</strong></td>
                <td>{result?.Suggestion ?? "-"}</td>
              </tr>
              <tr>
                <td><strong>ℹ️ Reason:</strong></td>
                <td>{result?.Reason ?? "-"}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};


export default ExistingInvestorForm;
