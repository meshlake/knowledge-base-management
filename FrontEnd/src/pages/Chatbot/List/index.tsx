import React, { useState, useRef, useEffect } from 'react';
import { ActionType, PageContainer, ProList } from '@ant-design/pro-components';
import AddForm from './component/AddForm';
import CardItem from './component/CardItem';
import AddCard from './component/AddCard';
import { getChatbotList } from '@/services/chatbot';
import styles from './index.less';

const OrgManagement = () => {
  const ref = useRef<ActionType>();
  const handleRefresh = () => ref?.current?.reload();

  // const [loading, setLoading] = useState(true);
  const [addVisible, setAddVisible] = useState(false);

  // const handleAdd = () => {
  //   setAddVisible(true);
  // };

  const refresh = (needRefresh: boolean) => {
    setAddVisible(false);
    if (needRefresh) {
      handleRefresh();
    }
  };

  const handleDelete = (id: string) => {
    console.log(id);
  };

  useEffect(() => {
    console.log('mount');
    console.log(ref?.current);
    if (ref?.current?.reloadAndRest) {
      ref.current.reloadAndRest();
      console.log('load');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ref]);

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
                      handleDelete(item.id);
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
            onMouseEnter: () => {
              console.log(record);
            },
            onClick: () => {
              console.log(record);
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
