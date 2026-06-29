/**
 * Ant Design 5 主题配置
 * 精致优雅的供应链调度平台视觉方案
 */
export const themeConfig = {
  token: {
    colorPrimary: '#4f46e5',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorInfo: '#3b82f6',
    borderRadius: 8,
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontSize: 14,
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f5f5f9',
    colorBorder: '#e5e7eb',
  },
  components: {
    Layout: {
      siderBg: '#1e1b4b',
      headerBg: '#ffffff',
      bodyBg: '#f5f5f9',
      triggerBg: '#312e81',
    },
    Menu: {
      darkItemBg: '#1e1b4b',
      darkItemSelectedBg: '#4f46e5',
      darkItemHoverBg: 'rgba(79, 70, 229, 0.3)',
      darkSubMenuItemBg: '#1e1b4b',
      itemBorderRadius: 8,
    },
    Button: {
      borderRadius: 8,
      controlHeight: 38,
    },
    Card: {
      borderRadiusLG: 12,
    },
    Table: {
      borderRadiusLG: 10,
      headerBg: '#fafafa',
    },
    Input: {
      controlHeight: 38,
      borderRadius: 8,
    },
    Select: {
      controlHeight: 38,
      borderRadius: 8,
    },
  },
};
