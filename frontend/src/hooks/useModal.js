import { useState, useCallback } from 'react';
import { Form } from 'antd';

export function useModal(initialValues = {}) {
  const [visible, setVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const show = useCallback((id, values = {}) => {
    setEditingId(id);
    form.setFieldsValue({ ...initialValues, ...values });
    setVisible(true);
  }, [form, initialValues]);

  const hide = useCallback(() => {
    setVisible(false);
    setEditingId(null);
    form.resetFields();
  }, [form]);

  const confirm = useCallback((onSubmit) => {
    form.validateFields().then(values => {
      onSubmit(values, editingId).then(() => {
        hide();
      });
    });
  }, [form, editingId, hide]);

  return {
    visible,
    editingId,
    form,
    show,
    hide,
    confirm,
    isEditing: !!editingId,
  };
}