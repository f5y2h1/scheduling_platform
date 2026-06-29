-- ============================================================
-- Xuni Scheduling Platform - 种子数据
-- 默认用户: admin / admin123 (BCrypt 加密)
-- ============================================================

-- 默认管理员用户 (密码: admin123)
INSERT INTO sys_user (username, password, real_name, email, role, status)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '系统管理员', 'admin@xuni.com', 'ADMIN', 1)
ON CONFLICT (username) DO NOTHING;

-- 默认操作员
INSERT INTO sys_user (username, password, real_name, email, role, status)
VALUES ('operator', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '操作员', 'operator@xuni.com', 'OPERATOR', 1)
ON CONFLICT (username) DO NOTHING;

-- 示例供应商
INSERT INTO biz_supplier (name, code, type, status, contact_name, contact_phone, rating, cooperation_years)
VALUES
  ('华东科技有限公司', 'SUP001', 'MANUFACTURER', 'ACTIVE', '张三', '13800138001', 4.8, 5),
  ('南方物流集团', 'SUP002', 'LOGISTICS', 'ACTIVE', '李四', '13800138002', 4.5, 3),
  ('北方电子制造', 'SUP003', 'MANUFACTURER', 'ACTIVE', '王五', '13800138003', 4.2, 2),
  ('西部批发商贸', 'SUP004', 'WHOLESALER', 'ACTIVE', '赵六', '13800138004', 3.8, 1)
ON CONFLICT (code) DO NOTHING;

-- 示例库存数据
INSERT INTO biz_inventory (product_name, sku_code, warehouse_name, quantity, safety_stock, status)
VALUES
  ('华为Mate 60 Pro', 'HW-M60P-001', '北京仓', 500, 100, 'NORMAL'),
  ('华为Mate 60 Pro', 'HW-M60P-001', '上海仓', 350, 100, 'NORMAL'),
  ('iPhone 15 Pro', 'AP-IP15P-001', '北京仓', 80, 150, 'LOW'),
  ('MacBook Pro 14', 'AP-MBP14-001', '广州仓', 200, 50, 'NORMAL'),
  ('AirPods Pro', 'AP-APP-001', '上海仓', 15, 50, 'LOW'),
  ('iPad Air', 'AP-IPA-001', '成都仓', 0, 30, 'OUT_OF_STOCK'),
  ('小米14 Ultra', 'XM-MI14U-001', '广州仓', 420, 80, 'NORMAL'),
  ('联想ThinkPad X1', 'LN-TPX1-001', '北京仓', 600, 100, 'OVERSTOCK')
ON CONFLICT DO NOTHING;

-- 示例订单数据
INSERT INTO biz_order (order_no, order_type, status, customer_name, product_name, quantity, total_amount, warehouse_name)
VALUES
  ('SO20260627001', 'SALE', 'SHIPPING', '华东科技', '华为Mate 60 Pro', 10, 69990.00, '北京仓'),
  ('SO20260627002', 'SALE', 'PENDING', '南方制造', 'MacBook Pro 14', 5, 74995.00, '广州仓'),
  ('SO20260627003', 'SALE', 'DELIVERED', '北方电子', '小米14 Ultra', 20, 119980.00, '广州仓'),
  ('SO20260627004', 'SALE', 'CONFIRMED', '西部物流', 'iPhone 15 Pro', 3, 26997.00, '北京仓')
ON CONFLICT (order_no) DO NOTHING;
