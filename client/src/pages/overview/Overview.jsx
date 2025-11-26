// src/pages/Overview.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyWrapper from "../../components/PlotlyWrapper";

const Overview = () => {
  const [mode, setMode] = useState('cases');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.get(`http://127.0.0.1:8000/api/world-map/?mode=${mode}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Lỗi API:', err);
        setLoading(false);
      });
  }, [mode]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '120px', fontSize: '20px', color: '#666' }}>
        Đang tải bản đồ thế giới...
      </div>
    );
  }

  if (!data) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Không có dữ liệu – kiểm tra API Django!</div>;
  }

  const plotData = [
    {
      type: 'choropleth',
      locations: data.locations,
      z: data.values,
      text: data.locations,
      hovertemplate: '<b>%{text}</b><br>Tổng: %{z:,.0f}<extra></extra>',
      colorscale: mode === 'deaths' ? 'Blues' : 'Reds',
      zmid: Math.max(...data.values) / 2,
      marker: { line: { color: 'white', width: 0.5 } },
      colorbar: {
        title: { text: mode === 'deaths' ? 'Total Deaths' : 'Total Cases', side: 'right' },
        thickness: 15,
        len: 0.8
      }
    }
  ];

  return (
    <div style={{ padding: '30px', maxWidth: '1400px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#2c3e50', fontSize: '32px', fontWeight: 'bold' }}>
        COVID-19 Global Overview
      </h1>

      {/* Radio buttons – giống Streamlit */}
      <div style={{ 
        textAlign: 'center', 
        marginBottom: '40px', 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '12px', 
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)' 
      }}>
        <strong style={{ fontSize: '18px', marginRight: '20px' }}>Chọn chế độ hiển thị:</strong>
        <label style={{ margin: '0 20px', cursor: 'pointer', fontSize: '16px' }}>
          <input
            type="radio"
            name="mode"
            value="cases"
            checked={mode === 'cases'}
            onChange={(e) => setMode(e.target.value)}
          />
          <span style={{ marginLeft: '8px', fontWeight: mode === 'cases' ? 'bold' : 'normal', color: '#e74c3c' }}>Total Cases</span>
        </label>
        <label style={{ margin: '0 20px', cursor: 'pointer', fontSize: '16px' }}>
          <input
            type="radio"
            name="mode"
            value="deaths"
            checked={mode === 'deaths'}
            onChange={(e) => setMode(e.target.value)}
          />
          <span style={{ marginLeft: '8px', fontWeight: mode === 'deaths' ? 'bold' : 'normal', color: '#2980b9' }}>Total Deaths</span>
        </label>
      </div>

      {/* DÙNG WRAPPER TỪ FILE RIÊNG – KHÔNG LỖI NỮA! */}
      <div style={{ borderRadius: '16px', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.1)', backgroundColor: 'white' }}>
        <PlotlyWrapper
          data={plotData}
          layout={{
            title: {
              text: `<b>${data.title}</b>`,
              x: 0.5,
              xanchor: 'center',
              font: { size: 26, color: '#2c3e50' }
            },
            geo: {
              projection: { type: 'natural earth' },
              showframe: false,
              showcoastlines: true,
              coastlinecolor: 'white',
              bgcolor: '#f8f9fa'
            },
            height: 720,
            margin: { t: 100, b: 20, l: 10, r: 10 },
            paper_bgcolor: 'white'
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['sendDataToCloud', 'lasso2d', 'select2d']
          }}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  );
};

export default Overview;