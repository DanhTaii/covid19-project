// src/layout/MainLayout.jsx
import { Outlet } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Box } from '@mui/material';

export default function MainLayout() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header cố định ở trên */}
      <Header />
        <div className='grid'>
          <Outlet />          {/* ← Quan trọng: chỗ này sẽ render các page */}
        </div>
      {/* Footer cố định ở dưới */}
      <Footer />
    </Box>
  );
}