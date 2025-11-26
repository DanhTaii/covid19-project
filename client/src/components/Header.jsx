// src/layout/Header.jsx
import { AppBar, Toolbar, Typography, Container } from '@mui/material';
import CoronavirusIcon from '@mui/icons-material/Coronavirus';

export default function Header() {
  return (
      <header className="web__header">
        <div className="grid">
            <div className="header__box">
                <CoronavirusIcon sx={{ mr: 2, fontSize: 40, color: 'white' }} />
                  <div className='header__browse'>
                    <div className='browse__text text-small-title'>
                        COVID-19 Dashboard & Prediction
                    </div>
                  </div>
           
          {/* <Typography variant="subtitle1" sx={{color:'white', fontWeight: 'bold'}}>
            Nhóm 11 
          </Typography> */}
            </div>
        </div>
    </header>
  );
}