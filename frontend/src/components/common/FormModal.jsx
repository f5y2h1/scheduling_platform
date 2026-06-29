import { Modal, Form } from 'antd';

function FormModal({
  visible,
  title,
  onCancel,
  onOk,
  children,
  form,
  okText = '确定',
  cancelText = '取消',
  width = 600,
  okButtonProps,
}) {
  const handleOk = () => {
    form.validateFields().then(values => {
      onOk(values);
    });
  };

  return (
    <Modal
      open={visible}
      title={title}
      onCancel={onCancel}
      onOk={handleOk}
      okText={okText}
      cancelText={cancelText}
      width={width}
      okButtonProps={okButtonProps}
      style={{ borderRadius: 12 }}
    >
      <Form form={form} layout="vertical">
        {children}
      </Form>
    </Modal>
  );
}

FormModal.Item = Form.Item;

export default FormModal;