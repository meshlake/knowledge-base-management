import React, { useState, useEffect } from 'react';
import { ConfigProvider, Empty } from 'antd';
import { getApplicationList } from '@/services/application';
import { PageContainer, ProList } from '@ant-design/pro-components';
import CommonCard from '@/components/CommonCard';
import { history } from '@umijs/max';
import styles from './index.less';

const ApplicationList = () => {
  const [loading, setLoading] = useState(true);
  const [list, setList] = useState<Application_API.Application[]>([]);

  useEffect(() => {
    setLoading(true);
    getApplicationList()
      .then((list) => setList(list))
      .catch(() => {})
      .finally(() => {
        setLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const wechatHeader = (
    <>
      <div className={styles.moduleHeader}>
        <img className={styles.moduleIcon} src="/images/wechat_icon.png" alt="" />
        <span className={styles.moduleTitle}>公众号</span>
        <span className={styles.moduleDescription}>请联系人工客服添加新的公众号</span>
      </div>
    </>
  );

  const weworkHeader = (
    <>
      <div className={styles.moduleHeader}>
        <img className={styles.moduleIcon} src="/images/wxwork_icon.png" alt="" />
        <span className={styles.moduleTitle}>企业微信</span>
        <span className={styles.moduleDescription}>请联系人工客服添加新的企业微信</span>
      </div>
    </>
  );

  return (
    <PageContainer
      className={styles.pageContainer}
      header={{
        title: '应用列表',
      }}
      loading={loading}
    >
      <ConfigProvider
        renderEmpty={() => (
          <Empty
            image="/images/empty.svg"
            imageStyle={{ height: 100 }}
            description={<p style={{ opacity: 0.4 }}>暂无公众号应用</p>}
          />
        )}
      >
        <ProList
          headerTitle={wechatHeader}
          pagination={false}
          bordered={false}
          ghost
          dataSource={list.filter((item) => item.category === 'WX_PUBLIC')}
          metas={{
            content: {
              render: (i, item) => (
                <CommonCard key={item.id} data={item} icon="/images/wx_public.png" />
              ),
            },
          }}
          onItem={(record) => {
            return {
              onClick: () => {
                history.push(`/application/${record.id}`);
              },
            };
          }}
          rowKey="id"
          grid={{ gutter: 16, column: 3 }}
          rowClassName={styles.cardItem}
        />
      </ConfigProvider>
      <ConfigProvider
        renderEmpty={() => (
          <Empty
            image="/images/empty.svg"
            imageStyle={{ height: 100 }}
            description={<p style={{ opacity: 0.4 }}>暂无企业微信应用</p>}
          />
        )}
      >
        <ProList
          headerTitle={weworkHeader}
          pagination={false}
          bordered={false}
          ghost
          dataSource={list
            .filter((item) => item.category !== 'WX_PUBLIC')
            .map((item) => {
              return {
                id: item.id,
                name: item.name,
                description: item.description,
                icon: item.login_info?.avatar
                  ? 'data:image/png;base64,' + item.login_info?.avatar
                  : '',
              };
            })}
          metas={{
            content: {
              render: (i, item) => (
                <CommonCard key={item.id} data={item} icon="/images/wxwork_icon.png" />
              ),
            },
          }}
          onItem={(record) => {
            return {
              onClick: () => {
                history.push(`/application/${record.id}`);
              },
            };
          }}
          rowKey="id"
          grid={{ gutter: 16, column: 3 }}
          rowClassName={styles.cardItem}
          style={{ marginTop: 16 }}
        />
      </ConfigProvider>
    </PageContainer>
  );
};

export default ApplicationList;
