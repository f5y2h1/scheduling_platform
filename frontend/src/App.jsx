import React, { useEffect } from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import GlassLayout from './components/layout/GlassLayout';
import LoginPage from './modules/system/pages/LoginPage';
import { useAuthStore } from './store/authStore';
import smartRequest from './services/smartRequest';

// 懒加载模块页面
const Dashboard = React.lazy(() => import('./modules/report/pages/Dashboard'));
const UserManagement = React.lazy(() => import('./modules/system/pages/UserManagement'));
const OrderManagement = React.lazy(() => import('./modules/order/pages/OrderManagement'));
const InventoryManagement = React.lazy(() => import('./modules/inventory/pages/InventoryManagement'));
const SchedulingCenter = React.lazy(() => import('./modules/scheduling/pages/SchedulingCenter'));
const FulfillmentManagement = React.lazy(() => import('./modules/fulfillment/pages/FulfillmentManagement'));
const SupplierManagement = React.lazy(() => import('./modules/supplier/pages/SupplierManagement'));
const ReportCenter = React.lazy(() => import('./modules/report/pages/ReportCenter'));
const AIDashboard = React.lazy(() => import('./modules/ai-dashboard/pages/AIDashboard'));
const KnowledgeManagement = React.lazy(() => import('./modules/ai-dashboard/pages/KnowledgeManagement'));
const AgentWorkflow = React.lazy(() => import('./modules/ai-dashboard/pages/AgentWorkflow'));

const PageLoading = () => (
  <div style={{
    display: 'flex', justifyContent: 'center', alignItems: 'center',
    height: '100%', minHeight: 400, fontSize: 16, color: '#64748b'
  }}>
    页面加载中...
  </div>
);

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          height: '100vh', padding: 40, background: '#f5f7fa'
        }}>
          <div style={{
            background: '#fff', borderRadius: 16, padding: 40,
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            textAlign: 'center', maxWidth: 500
          }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
            <h2 style={{ margin: 0, color: '#ef4444', fontSize: 20 }}>页面加载出错</h2>
            <p style={{ color: '#94a3b8', marginTop: 12, fontSize: 14 }}>
              {this.state.error?.message || '未知错误'}
            </p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              style={{
                marginTop: 20, padding: '10px 24px', borderRadius: 8,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff', border: 'none', cursor: 'pointer', fontSize: 14
              }}
            >
              刷新重试
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function PrivateRoute() {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <GlassLayout><Outlet /></GlassLayout>;
}

export default function App() {
  useEffect(() => {
    smartRequest.checkBackend();
  }, []);

  return (
    <ErrorBoundary>
      <React.Suspense fallback={<PageLoading />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<PrivateRoute />}>
            <Route index element={<Dashboard />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="system/users" element={<UserManagement />} />
            <Route path="orders" element={<OrderManagement />} />
            <Route path="inventory" element={<InventoryManagement />} />
            <Route path="scheduling" element={<SchedulingCenter />} />
            <Route path="fulfillment" element={<FulfillmentManagement />} />
            <Route path="suppliers" element={<SupplierManagement />} />
            <Route path="reports" element={<ReportCenter />} />
            <Route path="ai-dashboard" element={<AIDashboard />} />
            <Route path="ai-workflow" element={<AgentWorkflow />} />
            <Route path="knowledge" element={<KnowledgeManagement />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </React.Suspense>
    </ErrorBoundary>
  );
}
