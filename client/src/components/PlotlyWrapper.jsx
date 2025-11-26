// src/components/PlotlyWrapper.jsx
import React from 'react';
// import Plot from 'react-plotly.js'; // KHÔNG DÙNG CÁCH NÀY!

// BƯỚC QUAN TRỌNG: Import toàn bộ module và lấy component mặc định (.default)
import * as PlotlyReactModule from 'react-plotly.js'; 
const PlotComponent = PlotlyReactModule.default; // <--- Lấy component chính xác

import Plotly from 'plotly.js-dist-min'; 
// Giữ lại import Plotly gốc

const PlotlyWrapper = (props) => {
  return (
    // SỬ DỤNG TÊN BIẾN MỚI
    <PlotComponent // <--- CHỈ SỬ DỤNG BIẾN ĐÃ ĐƯỢC GÁN BẰNG .default
      {...props} 
      plotly={Plotly} // Cung cấp Plotly gốc
    />
  );
};

export default PlotlyWrapper;