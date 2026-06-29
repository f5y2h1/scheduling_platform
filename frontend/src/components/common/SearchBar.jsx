import { Input, Select, Button, Space } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

export default function SearchBar({
  onSearch,
  keyword,
  setKeyword,
  filters = [],
  filterValues = {},
  onFilterChange,
}) {
  return (
    <Space wrap>
      <Input.Search
        placeholder="搜索..."
        allowClear
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        onSearch={onSearch}
        prefix={<SearchOutlined />}
        style={{ width: 280 }}
      />
      {filters.map((filter) => (
        <Select
          key={filter.key}
          placeholder={filter.label}
          allowClear
          value={filterValues[filter.key]}
          onChange={(value) => onFilterChange(filter.key, value)}
          options={filter.options}
          style={{ width: 160 }}
        />
      ))}
      <Button type="primary" onClick={onSearch}>
        查询
      </Button>
    </Space>
  );
}