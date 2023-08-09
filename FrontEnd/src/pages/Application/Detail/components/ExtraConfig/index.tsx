import { Button, Form, Input, Modal, Switch, Tooltip, Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import { ExclamationCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import styles from './index.less';

const { Link } = Typography;

type Props = {
  data?: Application_API.Application;
  updateRequest: (id: string, data: Application_API.ApplicationUpdate) => Promise<void>;
};

const BaseInfo: React.FC<Props> = (props) => {
  const { data, updateRequest } = props;
  const [form] = Form.useForm();
  const [editable, setEditable] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleEdit = () => {
    setEditable(true);
  };

  const handleCancel = () => {
    form.setFieldsValue({
      name: data?.name,
      description: data?.description,
    });
    setEditable(false);
  };

  const handleSubmit = () => {
    if (!data) {
      return;
    }
    form
      .validateFields()
      .then((values) => {
        setLoading(true);
        const properties = data?.properties ? { ...data.properties, ...values } : values;
        updateRequest(data.id, { properties })
          .then(() => {
            setEditable(false);
          })
          .finally(() => {
            setLoading(false);
          });
      })
      .catch(() => {});
  };

  const conformRequest = (key: string, value: boolean) => {
    if (!data) return;
    const properties = {
      ...data?.properties,
      [key]: value,
    };
    return updateRequest(data.id, { properties }).catch(() => {});
  };

  const handlePropertyChange = (key: string, value: boolean) => {
    if (!value) {
      Modal.confirm({
        title: '提示',
        icon: <ExclamationCircleOutlined />,
        content: `确定关闭机器人${key === 'private_enable' ? '私聊' : '群聊'}功能吗？`,
        okText: '确定',
        cancelText: '取消',
        onOk() {
          conformRequest(key, value);
        },
        onCancel() {},
      });
    } else {
      conformRequest(key, value);
    }
  };

  useEffect(() => {
    form.setFieldsValue({
      webhook_url: data?.properties?.webhook_url,
    });
  }, [data]);

  return (
    <>
      <div className={styles.comContainer}>
        <div className={styles.header}>
          <div className={styles.title}>
            <span>企业微信群机器人 Webhook URL </span>
            <Tooltip
              title={
                <>
                  配置 Webhook URL 进行异常提醒，如何获取请
                  <Link href="https://open.work.weixin.qq.com/help2/pc/18401" target="_blank">
                    查看文档
                  </Link>
                </>
              }
            >
              <QuestionCircleOutlined style={{ fontSize: 16, color: '#1677ff' }} />
            </Tooltip>
          </div>
          {!editable && (
            <Button type="link" onClick={handleEdit}>
              编辑
            </Button>
          )}
        </div>
        <Form
          form={form}
          colon={false}
          autoComplete="off"
          requiredMark={false}
          labelAlign="left"
          className={styles.editableForm}
        >
          {editable ? (
            <>
              <Form.Item
                key="webhook_url"
                label=""
                name="webhook_url"
                rules={[{ required: false }]}
              >
                <Input
                  maxLength={255}
                  disabled={!editable}
                  placeholder={editable ? '请输入' : ''}
                  bordered={editable}
                />
              </Form.Item>
              <Form.Item style={{ textAlign: 'right', marginTop: 24 }}>
                <Button
                  disabled={loading}
                  onClick={handleCancel}
                  style={{ marginLeft: 12, width: 120 }}
                >
                  取消
                </Button>
                <Button
                  loading={loading}
                  onClick={handleSubmit}
                  type="primary"
                  style={{ marginLeft: 12, width: 120 }}
                >
                  保存
                </Button>
              </Form.Item>
            </>
          ) : (
            <div className={styles.webhookUrl}>
              {data?.properties?.webhook_url || <span style={{ opacity: 0.6 }}>未配置</span>}
            </div>
          )}
        </Form>
      </div>

      <div className={styles.comContainer}>
        <div className={styles.header}>
          <div className={styles.title}>
            <span>应用开关</span>
            <span className={styles.subTitle}>配置机器人是否在应用中生效</span>
          </div>
        </div>
        <div className={styles.switchItemList}>
          <div className={styles.switchItem}>
            <span className={styles.switchItemLabel}>群聊开关</span>
            <Switch
              defaultChecked
              checked={data?.properties?.room_enable}
              onChange={(value) => {
                handlePropertyChange('room_enable', value);
              }}
            />
          </div>
          <div className={styles.switchItem}>
            <span className={styles.switchItemLabel}>私聊开关</span>
            <Switch
              defaultChecked
              checked={data?.properties?.private_enable}
              onChange={(value) => {
                handlePropertyChange('private_enable', value);
              }}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default BaseInfo;
