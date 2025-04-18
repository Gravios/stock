import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { getStockData, getDailySummary, getMetadata, populateMetadata } from './api';

export default function App() {
  const [session, setSession] = useState(null);
  const [symbol, setSymbol] = useState("AAPL");
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState([]);
  const [metadata, setMetadata] = useState({});
  const handleLogout = () => {
      localStorage.removeItem("token"); // 🚫 clear token
      window.location.reload();         // 🔄 reload to return to login
  };

  useEffect(() => {
       getStockData(symbol)
         .then(res => setData(res.data.data.map(d => ({
               date: d[0],
               open: d[1],
               high: d[2],
               low: d[3],
               close: d[4],
               volume: d[5]
           }))))
          .catch(err => console.error(err));

       getDailySummary(symbol)
         .then(res => setSummary(res.data))
         .catch(err => console.error(err));

       getMetadata(symbol)
         .then(res => setMetadata(res.data))
         .catch(err => console.error(err));
  }, [symbol, session]);

  return (
    <div style={{ padding: 20 }}>
      <button onClick={handleLogout}>Log Out</button>
      <h1>Stock Dashboard</h1> 
      <select onChange={e => setSymbol(e.target.value)} value={symbol}>
        <option value="AAPL">AAPL</option>
        <option value="GOOG">GOOG</option>
        <option value="MSFT">MSFT</option>
      </select>

      <button onClick={() => populateMetadata(symbol)
                               .then(res => alert(res.data.message))
                               .catch(err => alert(err.message))}
              style={{ marginLeft: 10 }}>
        Populate Metadata
      </button>

      <h2>{metadata.name} ({metadata.symbol})</h2>
      <p>{metadata.sector} | {metadata.industry}</p>

      <h3>Stock Price History</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="close" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>

      <h3>Trading Volume</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="volume" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>

      <h3>7-Day Summary</h3>
      <table border="1" cellPadding="5" style={{ marginTop: 20 }}>
        <thead>
          <tr>
            <th>Date</th><th>High</th><th>Low</th><th>Close</th>
          </tr>
        </thead>
        <tbody>
          {summary.map((row, i) => (
            <tr key={i}>
              <td>{row.date}</td><td>{row.high}</td><td>{row.low}</td><td>{row.close}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

