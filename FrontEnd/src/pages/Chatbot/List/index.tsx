import React, { useState, useRef, useEffect } from 'react';
import { Modal } from 'antd';
import { ActionType, PageContainer, ProList } from '@ant-design/pro-components';
import { ExclamationCircleFilled } from '@ant-design/icons';
import { getChatbotList, deleteChatbot } from '@/services/chatbot';
import AddForm from './component/AddForm';
import CardItem from './component/CardItem';
import AddCard from './component/AddCard';
import styles from './index.less';

const OrgManagement = () => {
  const ref = useRef<ActionType>();
  const { confirm } = Modal;
  const handleRefresh = () => ref?.current?.reload();

  const [addVisible, setAddVisible] = useState(false);

  const refresh = (needRefresh: boolean) => {
    setAddVisible(false);
    if (needRefresh) {
      handleRefresh();
    }
  };

  const handleDelete = (bot: Chatbot_API.Chatbot) => {
    confirm({
      title: '请谨慎操作',
      icon: <ExclamationCircleFilled />,
      content: `确定删除机器人（${bot.name}）吗？删除不可恢复，并会影响相关应用。`,
      onOk() {
        return deleteChatbot(bot.id).then((result) => {
          console.log(result);
          if (result.success) {
            handleRefresh();
          }
        });
      },
      onCancel() {},
    });
  };

  useEffect(() => {
    if (ref?.current?.reloadAndRest) {
      ref.current.reloadAndRest();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <PageContainer
      className={styles.pageContainer}
      header={{
        title: '机器人列表',
      }}
    >
      <ProList
        pagination={false}
        bordered={false}
        ghost
        actionRef={ref}
        request={async () => {
          const data = await getChatbotList();
          return {
            data: [...data.items, { id: '', name: '' }],
          };
        }}
        metas={{
          content: {
            render: (i, item: Chatbot_API.Chatbot) => {
              if (item.id) {
                return (
                  <CardItem
                    key={item.id}
                    data={item}
                    handleDelete={() => {
                      handleDelete(item);
                    }}
                  />
                );
              } else {
                return <AddCard />;
              }
            },
          },
        }}
        onItem={(record: Chatbot_API.Chatbot) => {
          return {
            onClick: () => {
              if (record.id) {
                console.log('navigate to detail');
              } else {
                setAddVisible(true);
              }
            },
          };
        }}
        rowKey="id"
        grid={{ gutter: 16, column: 3 }}
        rowClassName={styles.cardItem}
      />
      <AddForm visible={addVisible} refresh={refresh}></AddForm>
    </PageContainer>
  );
};

export default OrgManagement;
