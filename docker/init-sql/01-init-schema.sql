-- ============================================================
-- Xuni Scheduling Platform - 数据库初始化脚本
-- PostgreSQL
-- ============================================================

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========== 系统用户表 ==========
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    real_name VARCHAR(64),
    email VARCHAR(128),
    phone VARCHAR(20),
    avatar VARCHAR(256),
    role VARCHAR(32) DEFAULT 'USER',
    department VARCHAR(64),
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 业务订单表 ==========
CREATE TABLE IF NOT EXISTS biz_order (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    order_type VARCHAR(32) DEFAULT 'SALE',
    status VARCHAR(16) DEFAULT 'PENDING',
    customer_id BIGINT,
    customer_name VARCHAR(128),
    product_id BIGINT,
    product_name VARCHAR(128),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(12,2),
    total_amount DECIMAL(14,2),
    warehouse_id BIGINT,
    warehouse_name VARCHAR(128),
    shipping_address VARCHAR(512),
    required_date TIMESTAMP,
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP,
    remark VARCHAR(256),
    created_by VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 业务库存表 ==========
CREATE TABLE IF NOT EXISTS biz_inventory (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT,
    product_name VARCHAR(128),
    sku_code VARCHAR(64),
    warehouse_id BIGINT,
    warehouse_name VARCHAR(128),
    quantity INTEGER DEFAULT 0,
    safety_stock INTEGER DEFAULT 0,
    locked_quantity INTEGER DEFAULT 0,
    available_quantity INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'NORMAL',
    last_check_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 业务调度任务表 ==========
CREATE TABLE IF NOT EXISTS biz_schedule_task (
    id BIGSERIAL PRIMARY KEY,
    task_no VARCHAR(32) NOT NULL UNIQUE,
    task_type VARCHAR(32) DEFAULT 'DISPATCH',
    status VARCHAR(16) DEFAULT 'PENDING',
    order_id BIGINT,
    order_no VARCHAR(32),
    from_warehouse_id BIGINT,
    from_warehouse_name VARCHAR(128),
    to_warehouse_id BIGINT,
    to_warehouse_name VARCHAR(128),
    product_id BIGINT,
    product_name VARCHAR(128),
    quantity INTEGER DEFAULT 1,
    ai_suggestion TEXT,
    ai_model_used VARCHAR(32),
    approved_by VARCHAR(64),
    approved_at TIMESTAMP,
    remark VARCHAR(256),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 业务履约表 ==========
CREATE TABLE IF NOT EXISTS biz_fulfillment (
    id BIGSERIAL PRIMARY KEY,
    fulfillment_no VARCHAR(32) NOT NULL UNIQUE,
    order_id BIGINT,
    order_no VARCHAR(32),
    type VARCHAR(32) DEFAULT 'DELIVERY',
    status VARCHAR(16) DEFAULT 'PENDING',
    carrier_name VARCHAR(128),
    tracking_number VARCHAR(64),
    warehouse_id BIGINT,
    warehouse_name VARCHAR(128),
    origin_address VARCHAR(512),
    destination_address VARCHAR(512),
    logistics_info TEXT,
    estimated_delivery TIMESTAMP,
    actual_delivery TIMESTAMP,
    signed_at TIMESTAMP,
    signed_by VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 业务供应商表 ==========
CREATE TABLE IF NOT EXISTS biz_supplier (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    code VARCHAR(32) UNIQUE,
    type VARCHAR(32),
    status VARCHAR(16) DEFAULT 'ACTIVE',
    contact_name VARCHAR(64),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(128),
    address VARCHAR(256),
    rating DECIMAL(3,2),
    cooperation_years INTEGER,
    on_time_delivery_rate REAL,
    quality_pass_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 创建索引 ==========
CREATE INDEX idx_order_status ON biz_order(status);
CREATE INDEX idx_order_customer ON biz_order(customer_name);
CREATE INDEX idx_order_created ON biz_order(created_at);
CREATE INDEX idx_inventory_product ON biz_inventory(product_id, warehouse_id);
CREATE INDEX idx_inventory_status ON biz_inventory(status);
CREATE INDEX idx_schedule_status ON biz_schedule_task(status);
CREATE INDEX idx_fulfillment_status ON biz_fulfillment(status);
CREATE INDEX idx_fulfillment_tracking ON biz_fulfillment(tracking_number);
CREATE INDEX idx_supplier_status ON biz_supplier(status);
