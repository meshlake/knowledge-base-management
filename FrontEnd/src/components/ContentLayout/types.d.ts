declare namespace KnowledgeBase {
  interface BaseModel {
    id: int;
    name: string;
  }

  interface ContentItemRender<T extends KnowledgeBase.BaseModel> {
    fetch: () => Promise<{ data: T[] }>;
    display: (dom: React.ReactNode, item: T) => React.ReactNode;
    events: (item: T) => { [key: string]: (e: React.SyntheticEvent) => void };
  }
}

export default KnowledgeBase;
