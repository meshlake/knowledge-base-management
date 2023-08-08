import React, { useState, useRef, useEffect } from 'react';
import { Modal, notification } from 'antd';
import { history } from '@umijs/max';
import { ActionType, PageContainer, ProList } from '@ant-design/pro-components';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { getChatbotList, deleteChatbot } from '@/services/chatbot';
import AddForm from './components/AddForm';
import CardItem from './components/CardItem';
import AddCard from './components/AddCard';
import styles from './index.less';

const ChatbotList = () => {
  const { confirm } = Modal;
  const ref = useRef<ActionType>();
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
      icon: <ExclamationCircleOutlined style={{ color: 'red' }} />,
      content: `确定删除机器人【${bot.name}】吗？删除不可恢复，并会影响相关应用。`,
      okText: '确定删除',
      cancelText: '取消',
      onOk() {
        return deleteChatbot(bot.id)
          .then((response) => {
            if (response.code === 200) {
              handleRefresh();
            } else if (response.code === 400) {
              notification.error({
                message: '删除失败',
                description: '机器人已被应用绑定，请先解除绑定',
              });
            }
          })
          .catch(() => {});
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
          const list = await getChatbotList();
          return {
            data: [...list, { id: '', name: '' } as Chatbot_API.Chatbot],
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
                history.push(`/chatbot/${record.id}`);
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

export default ChatbotList;
