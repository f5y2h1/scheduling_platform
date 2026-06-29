import { useState, useCallback, useEffect } from 'react';

export function useTable(fetchData, initialParams = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [filters, setFilters] = useState(initialParams);

  const fetch = useCallback(async (page = pagination.current, pageSize = pagination.pageSize, searchFilters = filters) => {
    setLoading(true);
    try {
      const params = {
        page,
        size: pageSize,
        ...searchFilters,
      };
      const result = await fetchData(params);
      if (result) {
        setData(result.records || result || []);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize,
          total: result.total || 0,
        }));
      }
    } catch (e) {
      console.error('Fetch data failed:', e);
    } finally {
      setLoading(false);
    }
  }, [fetchData, pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetch(pagination.current, pagination.pageSize, filters);
  }, [fetch, pagination.current, pagination.pageSize, filters]);

  const handleChange = useCallback((page, pageSize) => {
    setPagination(prev => ({ ...prev, current: page, pageSize }));
  }, []);

  const handleFilterChange = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialParams);
    setPagination(prev => ({ ...prev, current: 1 }));
  }, [initialParams]);

  const refresh = useCallback(() => {
    fetch(pagination.current, pagination.pageSize, filters);
  }, [fetch, pagination.current, pagination.pageSize, filters]);

  return {
    data,
    loading,
    pagination,
    filters,
    handleChange,
    handleFilterChange,
    resetFilters,
    refresh,
  };
}