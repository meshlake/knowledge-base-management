import React, { useEffect, useState } from 'react';
import Markdown from 'react-markdown';
import classNames from 'classnames';
import { useLocation, history } from '@umijs/max';
import {
  DeleteOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import Button from 'antd/es/button';
import * as conversationServices from '@/services/conversation';
import * as chatbotServices from '@/services/chatbot';
import { Form, Modal, Select, Spin, message } from 'antd';
import { OptionProps } from 'antd/es/select';
import Chat, { Bubble, useMessages } from '@chatui/core';
import '@chatui/core/dist/index.css';
import styles from './index.less';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const ChatComponent: React.FC = () => {
  const pageQuery = useQuery();

  const { confirm } = Modal;
  const [chatbotForm] = Form.useForm();
  const [activeConversationId, setActiveConversationId] = useState<string>();
  const [hoveredConversationId, setHoveredConversationId] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [conversationList, setConversationList] = useState<Conversation_API.Conversation[]>([]);
  const [botId, setBotId] = useState<string>();
  const [chatbotList, setChatbotList] = useState<OptionProps[]>([]);

  const { messages, appendMsg, setTyping, resetList } = useMessages([]);
  const [messageLoading, setMessageLoading] = useState<boolean>(false);

  const getChatbotList = async () => {
    try {
      const data = await chatbotServices.getChatbotList();
      const list = data
        .map((item) => {
          return {
            value: item.id + '',
            label: item.name,
            disabled: item.knowledge_bases.length === 0,
            children: [],
          };
        })
        .sort((a, b) => (a.disabled ? 1 : 0) - (b.disabled ? 1 : 0));
      setChatbotList(list);
    } catch (e) {
      console.log(e);
    }
  };

  const getConversationList = () => {
    return conversationServices
      .getConversationList({ page: 1, size: 100 })
      .then((data) => {
        return data.items;
      })
      .catch(() => {
        return [];
      });
  };

  const getChatHistory = (conversationId: string) => {
    return conversationServices
      .getConversation(conversationId)
      .then((response) => {
        if (response.messages) {
          response.messages.forEach((item) => {
            appendMsg({
              type: 'text',
              content: { text: item.content },
              position: item.role === 'user' ? 'right' : 'left',
              user: {
                avatar:
                  item.role === 'user' ? '/images/default_avatar.png' : '/images/bot_avatar.png',
              },
            });
          });
        }
      })
      .catch(() => {});
  };

  const initializeState = () => {
    resetList();
    setActiveConversationId(undefined);
    setBotId(undefined);
    setLoading(true);
    getConversationList().then((list) => {
      setLoading(false);
      setConversationList(list);
      if (pageQuery.get('botId')) {
        chatbotForm.setFieldsValue({ chatbotId: pageQuery.get('botId') });
      } else {
        const firstItem = list[0];
        if (firstItem) {
          setActiveConversationId(firstItem.id);
          setBotId(firstItem.bot_id + '');
          getChatHistory(firstItem.id);
        }
      }
    });
  };

  const updateConversationList = () => {
    return getConversationList().then((list) => {
      setConversationList(list);
    });
  };

  const handleClickConversation = (conversation: Conversation_API.Conversation) => {
    if (conversation.id === activeConversationId) {
      return;
    }
    setActiveConversationId(conversation.id);
    setBotId(conversation.bot_id + '');
    resetList();
    getChatHistory(conversation.id);
  };

  const handleAddConversation = () => {
    setBotId(undefined);
    setActiveConversationId(undefined);
    resetList();
    chatbotForm.setFieldsValue({ chatbotId: undefined });
  };

  const handleDeleteConversation = (id: string) => {
    confirm({
      title: '提示',
      icon: <ExclamationCircleOutlined style={{ color: 'red' }} />,
      content: `确定删除对话么？删除不可恢复`,
      okText: '确定',
      cancelText: '取消',
      onOk() {
        conversationServices
          .deleteConversation(id)
          .then(() => {
            if (id === activeConversationId) {
              initializeState();
            } else {
              updateConversationList();
            }
          })
          .catch(() => {});
      },
      onCancel() {},
    });
  };

  const handleChooseChatbot = () => {
    chatbotForm
      .validateFields()
      .then((values) => {
        setBotId(values.chatbotId + '');
      })
      .catch(() => {
        setBotId(undefined);
      });
  };

  const sendMessage = async (text: string) => {
    if (!botId) {
      return;
    }
    let currentConversationId = activeConversationId;
    if (!activeConversationId) {
      try {
        const newConversation = await conversationServices.createConversation({
          bot: botId,
          topic: text,
        });
        currentConversationId = newConversation.id;
        setActiveConversationId(newConversation.id);
        await updateConversationList();
      } catch (error) {
        throw new Error('创建对话失败，请重试');
      }
    }
    try {
      const response = await conversationServices.sendMessage(currentConversationId as string, {
        role: 'user',
        content: text,
      });
      if (Array.isArray(response.items) && response.items[1]) {
        return response.items[1];
      } else {
        return {
          content: '',
        };
      }
    } catch (err) {
      throw new Error('服务异常');
    }
  };

  const handleSendMessage = async (type: string, val: string) => {
    if (messageLoading) {
      message.loading(`请稍后`);
      return;
    }
    if (type === 'text' && val.trim()) {
      appendMsg({
        type: 'text',
        content: { text: val },
        position: 'right',
        user: {
          avatar: '/images/default_avatar.png',
        },
      });
      setTyping(true);
      setMessageLoading(true);
      try {
        const response = await sendMessage(val);
        setTyping(false);
        setMessageLoading(false);
        if (response && response.content) {
          appendMsg({
            type: 'text',
            content: { text: response.content },
            user: {
              avatar: '/images/bot_avatar.png',
            },
          });
          updateConversationList();
        }
      } catch (error: any) {
        message.error(error.message);
        setTyping(false);
        setMessageLoading(false);
      }
    }
  };

  const handleNavigateChatbot = () => {
    if (botId) {
      history.push(`/chatbot/${botId}`);
    }
  };

  useEffect(() => {
    initializeState();
    getChatbotList();
  }, []);

  const newConversation = (
    <>
      <div className={styles.newConversationContainer}>
        <div className={styles.chooseChatbotContainer}>
          <div className={styles.chooseChatbotTitle}>选择机器人</div>
          <div className={styles.chooseChatbotDes}>开启新对话前，请先选择机器人</div>
          <Form
            form={chatbotForm}
            colon={false}
            autoComplete="off"
            requiredMark={false}
            style={{ maxWidth: '80%' }}
          >
            <Form.Item label="" name="chatbotId" rules={[{ required: true, message: '请选择' }]}>
              <Select options={chatbotList} placeholder="请选择"></Select>
            </Form.Item>
          </Form>
          <div className={styles.chooseChatbotButtonContainer}>
            <Button type="primary" onClick={handleChooseChatbot}>
              开启对话
            </Button>
          </div>
        </div>
      </div>
    </>
  );

  return (
    <div className={styles.pageContainer}>
      <div className={styles.leftContainer}>
        <Spin spinning={loading} delay={200} wrapperClassName={styles.listContainer}>
          {conversationList.map((conversation) => {
            return (
              <div
                key={conversation.id}
                className={classNames(
                  styles.conversationCard,
                  conversation.id === activeConversationId ? styles.active : '',
                )}
                onClick={() => {
                  handleClickConversation(conversation);
                }}
                onMouseEnter={() => {
                  setHoveredConversationId(conversation.id);
                }}
                onMouseLeave={() => {
                  setHoveredConversationId(undefined);
                }}
              >
                <img className={styles.conversationIcon} src="/images/conversation_icon.png" />
                <div className={styles.conversationCardContent}>
                  <div className={styles.conversationTopic}>{conversation.topic || '新的对话'}</div>
                  {conversation.description ? (
                    <div className={styles.conversationDescription}>{conversation.description}</div>
                  ) : null}
                </div>
                {hoveredConversationId === conversation.id ? (
                  <div className={styles.actions}>
                    <DeleteOutlined
                      style={{ fontSize: 16 }}
                      onClick={(e: any) => {
                        e.stopPropagation();
                        handleDeleteConversation(conversation.id);
                      }}
                    />
                  </div>
                ) : null}
              </div>
            );
          })}
        </Spin>
        <Button
          className={styles.addButton}
          type="primary"
          ghost
          icon={<PlusOutlined />}
          onClick={handleAddConversation}
        >
          新对话
        </Button>
      </div>
      <div className={styles.rightContainer} style={{ opacity: loading ? 0 : 1 }}>
        {!activeConversationId && !botId && !loading ? newConversation : null}
        <div className={styles.topBar}>
          <span>{chatbotList.find((item) => item.value === botId)?.label}</span>
          <Button
            type="link"
            className={styles.settingIcon}
            onClick={() => handleNavigateChatbot()}
            icon={<SettingOutlined style={{ color: '#616675', fontSize: 18 }} />}
          ></Button>
        </div>
        <div className={styles.messageContainer}>
          <Chat
            messages={messages}
            renderMessageContent={(msg: any) => (
              <Bubble>
                <Markdown>{msg.content.text}</Markdown>
              </Bubble>
            )}
            onSend={handleSendMessage}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;
