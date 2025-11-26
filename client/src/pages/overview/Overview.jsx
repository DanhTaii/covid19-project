// // pages/Overview.jsx
// import { useState, useEffect } from 'react';
// import WorldMap from '@components/WorldMap';
// import { fetchWorldMapData } from '@services/api';
// import './Overview.module.css'; // hoặc dùng Tailwind

// const Overview = () => {
//   const [mode, setMode] = useState('cases'); // 'cases' | 'deaths'
//   const [chartData, setChartData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     const loadData = async () => {
//       try {
//         setLoading(true);
//         const data = await fetchWorldMapData(mode);
//         setChartData(data);
//         setError(null);
//       } catch (err) {
//         setError("Không tải được dữ liệu. Backend Django đang chạy chưa bro?");
//       } finally {
//         setLoading(false);
//       }
//     };
//     loadData();
//   }, [mode]);

//   return (
//     <div className="flex h-screen bg-gray-50">
//       {/* Sidebar */}
//       <div className="w-80 bg-white shadow-lg p-6">
//         <h2 className="text-2xl font-bold text-indigo-700 mb-8">COVID-19 OVERVIEW</h2>
        
//         <div className="space-y-4">
//           <h3 className="text-lg font-semibold text-gray-700">Chế độ hiển thị</h3>
          
//           <div className="space-y-3">
//             <label className="flex items-center space-x-3 cursor-pointer">
//               <input
//                 type="radio"
//                 name="mode"
//                 value="cases"
//                 checked={mode === 'cases'}
//                 onChange={(e) => setMode(e.target.value)}
//                 className="w-5 h-5 text-indigo-600"
//               />
//               <span className="text-gray-800 font-medium">Total Cases</span>
//             </label>

//             <label className="flex items-center space-x-3 cursor-pointer">
//               <input
//                 type="radio"
//                 name="mode"
//                 value="deaths"
//                 checked={mode === 'deaths'}
//                 onChange={(e) => setMode(e.target.value)}
//                 className="w-5 h-5 text-red-600"
//               />
//               <span className="text-gray-800 font-medium">Total Deaths</span>
//             </label>
//           </div>
//         </div>
//       </div>

//       {/* Main content */}
//       <div className="flex-1 p-8">
//         {loading && (
//           <div className="flex items-center justify-center h-full">
//             <div className="text-2xl text-gray-600">Đang tải bản đồ...</div>
//           </div>
//         )}

//         {error && (
//           <div className="text-red-600 text-center text-xl">{error}</div>
//         )}

//         {chartData && <WorldMap data={chartData} />}
//       </div>
//     </div>
//   );
// };

// export default Overview;

export default function Overview() {
  return (
    <div>Overview</div>
  );
}