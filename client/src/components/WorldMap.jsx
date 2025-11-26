// components/CovidWorldMap.jsx
import Plotly from 'plotly.js';
import { useEffect, useRef } from 'react';

const WorldMap = ({ data }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    Plotly.newPlot(chartRef.current, data.data, data.layout, {
      responsive: true,
      displayModeBar: true,
    });

    return () => {
      Plotly.purge(chartRef.current);
    };
  }, [data]);

  return <div ref={chartRef} className="w-full h-screen" />;
};

export default WorldMap;