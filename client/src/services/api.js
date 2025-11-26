// src/services/api.js
const API_BASE = '/api'; // dùng /api vì đã proxy rồi, đẹp hơn!

export const fetchWorldMapData = async (mode = 'cases') => {
  try {
    const response = await fetch(`${API_BASE}/covid/overview/world-map/?mode=${mode}`);
    if (!response.ok) throw new Error('Network error');
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};

// Thêm vài hàm sau này cũng dễ
// export const fetchCountryDetail = async (country) => { ... }