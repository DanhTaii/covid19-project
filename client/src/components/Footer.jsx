// src/layout/Footer.jsx
import { Typography, Container, Link } from '@mui/material';

export default function Footer() {
  return (
    <div className='footer-fullwidth'>
    <Container
      maxWidth={false}
      component="footer"
      sx={{
        py: 3,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.grey[200],
        textAlign: 'center'
      }}
    >
      <Typography variant="body2" color="text.secondary">
        © {new Date().getFullYear()} COVID-19 Dashboard • Dữ liệu từ{' '}
        <Link href="https://ourworldindata.org/coronavirus" target="_blank" rel="noopener">
          Our World in Data
        </Link>
      </Typography>
    </Container>
    </div>

  );
}