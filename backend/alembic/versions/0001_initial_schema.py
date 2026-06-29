"""Initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-06-28 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sys_user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('real_name', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=128), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('avatar', sa.String(length=256), nullable=True),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('department', sa.String(length=64), nullable=True),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_sys_user_username'), 'sys_user', ['username'], unique=True)

    op.create_table(
        'biz_order',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_no', sa.String(length=32), nullable=False),
        sa.Column('order_type', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('customer_name', sa.String(length=128), nullable=True),
        sa.Column('product_name', sa.String(length=128), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('warehouse_name', sa.String(length=128), nullable=True),
        sa.Column('shipping_address', sa.Text(), nullable=True),
        sa.Column('required_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('shipped_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('remark', sa.String(length=256), nullable=True),
        sa.Column('created_by', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no'),
    )
    op.create_index(op.f('ix_biz_order_order_no'), 'biz_order', ['order_no'], unique=True)
    op.create_index(op.f('ix_biz_order_status'), 'biz_order', ['status'], unique=False)

    op.create_table(
        'biz_inventory',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('product_name', sa.String(length=128), nullable=True),
        sa.Column('sku_code', sa.String(length=64), nullable=True),
        sa.Column('warehouse_id', sa.Integer(), nullable=True),
        sa.Column('warehouse_name', sa.String(length=128), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('safety_stock', sa.Integer(), nullable=False),
        sa.Column('locked_quantity', sa.Integer(), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('last_check_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_biz_inventory_status'), 'biz_inventory', ['status'], unique=False)

    op.create_table(
        'biz_schedule_task',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_no', sa.String(length=32), nullable=False),
        sa.Column('task_type', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('order_no', sa.String(length=32), nullable=True),
        sa.Column('from_warehouse_name', sa.String(length=128), nullable=True),
        sa.Column('to_warehouse_name', sa.String(length=128), nullable=True),
        sa.Column('product_name', sa.String(length=128), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('ai_suggestion', sa.Text(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=32), nullable=True),
        sa.Column('approved_by', sa.String(length=64), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('remark', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_no'),
    )
    op.create_index(op.f('ix_biz_schedule_task_task_no'), 'biz_schedule_task', ['task_no'], unique=True)
    op.create_index(op.f('ix_biz_schedule_task_status'), 'biz_schedule_task', ['status'], unique=False)

    op.create_table(
        'biz_fulfillment',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fulfillment_no', sa.String(length=32), nullable=False),
        sa.Column('order_no', sa.String(length=32), nullable=True),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('carrier_name', sa.String(length=128), nullable=True),
        sa.Column('tracking_number', sa.String(length=64), nullable=True),
        sa.Column('warehouse_name', sa.String(length=128), nullable=True),
        sa.Column('origin_address', sa.Text(), nullable=True),
        sa.Column('destination_address', sa.Text(), nullable=True),
        sa.Column('logistics_info', sa.Text(), nullable=True),
        sa.Column('estimated_delivery', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery', sa.DateTime(timezone=True), nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('signed_by', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fulfillment_no'),
    )
    op.create_index(op.f('ix_biz_fulfillment_status'), 'biz_fulfillment', ['status'], unique=False)
    op.create_index(op.f('ix_biz_fulfillment_tracking_number'), 'biz_fulfillment', ['tracking_number'], unique=False)

    op.create_table(
        'biz_supplier',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=True),
        sa.Column('type', sa.String(length=32), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('contact_name', sa.String(length=64), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=128), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('cooperation_years', sa.Integer(), nullable=True),
        sa.Column('on_time_delivery_rate', sa.Float(), nullable=True),
        sa.Column('quality_pass_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_biz_supplier_status'), 'biz_supplier', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_biz_supplier_status'), table_name='biz_supplier')
    op.drop_table('biz_supplier')

    op.drop_index(op.f('ix_biz_fulfillment_tracking_number'), table_name='biz_fulfillment')
    op.drop_index(op.f('ix_biz_fulfillment_status'), table_name='biz_fulfillment')
    op.drop_table('biz_fulfillment')

    op.drop_index(op.f('ix_biz_schedule_task_status'), table_name='biz_schedule_task')
    op.drop_index(op.f('ix_biz_schedule_task_task_no'), table_name='biz_schedule_task')
    op.drop_table('biz_schedule_task')

    op.drop_index(op.f('ix_biz_inventory_status'), table_name='biz_inventory')
    op.drop_table('biz_inventory')

    op.drop_index(op.f('ix_biz_order_status'), table_name='biz_order')
    op.drop_index(op.f('ix_biz_order_order_no'), table_name='biz_order')
    op.drop_table('biz_order')

    op.drop_index(op.f('ix_sys_user_username'), table_name='sys_user')
    op.drop_table('sys_user')