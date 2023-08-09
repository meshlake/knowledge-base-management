import { Button, Col, Modal, Pagination, Row, Spin, notification } from 'antd';
import React, { useEffect, useState } from 'react';
import Styles from './index.less';
import KnowledgeItem from '../KnowledgeItem';
import ImportFile from '../ImportFile';
import ManuallyEnter from '../ManuallyEnter';
import { KnowledgeBaseModel } from '@/pages/KnowledgeBase/types';
import { getKnowledgeItems, deleteKnowledgeItem } from '@/services/knowledgeItem';
import { useParams } from '@umijs/max';

type TPagination = Omit<DEFAULT_API.Paginate<KNOWLEDGE_ITEM_API.KnowledgeItem>, 'items'>;
type KnowledgeListProps = {
  knowledgeBase: KnowledgeBaseModel;
  isFileEmbedding: boolean;
  refresh: () => void;
};

const App: React.FC<KnowledgeListProps> = (props) => {
  const { knowledgeBase, isFileEmbedding, refresh } = props;
  const params = useParams();

  const [knowledgeList, setKnowledgeList] = useState<KNOWLEDGE_ITEM_API.KnowledgeItem[]>([]);

  const [pagination, setPagination] = useState<TPagination>({
    page: 1,
    pages: 0,
    total: 0,
    size: 15,
  });

  const [isImportFileModalOpen, setIsImportFileModalOpen] = useState<boolean>(false);
  const [isManuallyEnterModalOpen, setIsManuallyEnterModalOpen] = useState<boolean>(false);

  const [currentData, setCurrentData] = useState<KNOWLEDGE_ITEM_API.KnowledgeItem>(
    {} as KNOWLEDGE_ITEM_API.KnowledgeItem,
  );

  const [loading, setLoading] = useState<boolean>(false);

  const [modal, contextHolder] = Modal.useModal();

  const getKnowledgeList = async (page: number) => {
    setLoading(true);
    try {
      const data = await getKnowledgeItems(Number(params.id), page);
      setKnowledgeList(data.items);
      setPagination({
        page: data.page,
        pages: data.pages,
        total: data.total,
        size: data.size,
      });
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const handleDeleteKnowledgeItem = async (id: number) => {
    modal.confirm({
      title: '',
      icon: null,
      content: (
        <div style={{ marginBottom: '47px', fontSize: '18px' }}>
          确定删除该知识点吗？删除不可恢复。
        </div>
      ),
      okText: '确认删除',
      cancelText: '取消',
      width: '600px',
      bodyStyle: {
        padding: '80px 46px',
        paddingBottom: '5px',
        paddingRight: '6px',
      },
      onOk: async () => {
        setLoading(true);
        try {
          await deleteKnowledgeItem(id);
          getKnowledgeList(pagination.page);
          notification.success({ message: '删除成功' });
          setLoading(false);
        } catch (error) {
          setLoading(false);
        }
      },
    });
  };

  const handleOpenManuallyEnterModal = () => {
    setCurrentData({} as KNOWLEDGE_ITEM_API.KnowledgeItem);
    setIsManuallyEnterModalOpen(true);
  };

  const handleEditKnowledgeItem = (id: number) => {
    const current = knowledgeList.find((item) => item.id === id);
    if (current) {
      setCurrentData(current);
      setIsManuallyEnterModalOpen(true);
    }
  };

  const handleCloseModal = (isNeedRefresh: boolean) => {
    if (isNeedRefresh) {
      getKnowledgeList(pagination.page);
    }
    refresh();
    setIsManuallyEnterModalOpen(false);
    setIsImportFileModalOpen(false);
  };

  const handleOpenImportFileModal = () => {
    if (!isFileEmbedding) {
      setIsImportFileModalOpen(true);
    } else {
      notification.warning({ message: '抱歉，有文件正在上传处理中，暂时不能进行该操作' });
    }
  };

  useEffect(() => {
    getKnowledgeList(1);
  }, []);

  return (
    <div className={Styles.knowledgeList}>
      <Spin spinning={loading} style={{ height: '100px' }}>
        <div className={Styles.header}>
          <div>
            {knowledgeBase.name}：{knowledgeList.length}条知识
          </div>
          {/* <div>搜索</div> */}
          <div>
            <Button onClick={handleOpenImportFileModal} style={{ marginRight: '20px' }}>
              文件导入
            </Button>
            <Button type="primary" ghost onClick={handleOpenManuallyEnterModal}>
              手动添加
            </Button>
          </div>
        </div>
        {knowledgeList?.length > 0 ? (
          <div className={Styles.listContentWrapper}>
            <Row gutter={[16, 16]}>
              {knowledgeList.map((item) => {
                return (
                  <Col span={8} key={item.id} onClick={() => handleEditKnowledgeItem(item.id)}>
                    <KnowledgeItem
                      key={item.id}
                      data={item}
                      onDelete={() => handleDeleteKnowledgeItem(item.id)}
                    ></KnowledgeItem>
                  </Col>
                );
              })}
            </Row>
          </div>
        ) : (
          <div className={Styles.emptyTips}>
            <div className={Styles.tipWrapper}>
              <div className={Styles.title}>还没有知识点</div>
              <div className={Styles.content}>
                您还没有添加任何知识点，可以通过手动输入或者文件导入完成知识点录入～
              </div>
              <div className={Styles.btns}>
                <Button style={{ width: '140px' }} onClick={handleOpenImportFileModal}>
                  文件导入
                </Button>
                <Button
                  style={{ width: '140px' }}
                  type="primary"
                  ghost
                  onClick={handleOpenManuallyEnterModal}
                >
                  手动添加
                </Button>
              </div>
            </div>
          </div>
        )}
      </Spin>
      <ImportFile isModalOpen={isImportFileModalOpen} onClose={handleCloseModal}></ImportFile>
      <ManuallyEnter
        isModalOpen={isManuallyEnterModalOpen}
        onClose={handleCloseModal}
        data={currentData}
      ></ManuallyEnter>
      {knowledgeList?.length > 0 && (
        <div className={Styles.paginationWrapper}>
          <Pagination
            total={pagination.total}
            showTotal={(total) => `共${pagination.pages}页/${total}条`}
            defaultPageSize={pagination.size}
            defaultCurrent={1}
            showSizeChanger={false}
            size="small"
            onChange={(page) => getKnowledgeList(page)}
          />
        </div>
      )}
      {contextHolder}
    </div>
  );
};

export default App;
