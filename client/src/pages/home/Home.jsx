import { Container, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <Container maxWidth="md" sx={{ textAlign: 'center', mt: 10 }}>
      <Typography variant="h3" gutterBottom>
        Chào mừng đến với COVID-19 Dashboard
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        Phân tích dữ liệu & dự đoán dịch bệnh bằng Prophet
      </Typography>
      <Button component={Link} to="/visualization" variant="contained" size="large" sx={{ mt: 4 }}>
        Vào Dashboard ngay
      </Button>
    </Container>
  );
}