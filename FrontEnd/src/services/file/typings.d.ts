declare namespace FILE_API {
  type File = {
    id: number;
    knowledge_base_id: number;
    name: string;
    path: string;
    status: 'UPLOADED' | 'SUCCESS' | 'FAILED' | 'EMBEDDING';
  };

  type FileCreate = Omit<File, 'id'>;
}
