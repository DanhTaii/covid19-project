import { useState } from 'react'
// import './App.css'
import MainLayout from './layout/MainLayout';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/home/Home';
import Overview from './pages/overview/Overview';
import Prediction from './pages/prediction/Prediction';
import Visualization from './pages/visualization/Visualization';

function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
      <Routes>
        {/* Định tuyến Lồng ghép (Nested Routing). Route này định nghĩa một nhóm các Route con sẽ sử dụng cùng một bố cục (MainLayout) */}
        <Route element={<MainLayout />}>
        {/* Các route con sẽ được nhúng vào Route cha */}
          {/* Route Con 1 (Trang Chủ) */}
          <Route path="/" element={<Home />} />
          {/* Route Con 2 (Dashboard) */}
          <Route path="/overview" element={<Overview />} />
          {/* Route Con 3 (Dự đoán) */}
          <Route path="/prediction" element={<Prediction />} />
          {/* Route Con 3 (Dự đoán) */}
          <Route path="/visualization" element={<Visualization />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
