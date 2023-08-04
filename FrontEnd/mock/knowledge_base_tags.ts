import { Request, Response, response } from 'express';
import { random } from 'lodash';

export default {
  'GET /api/knowledge_bases/:id/tags': (req: Request, res: Response) => {
    let id = req.params.id;
    let response_data = {
      items: [
        {
          id: 1,
          name: '消费税',
          user_id: 1,
          knowledge_base_id: id,
          parent_id: 0,
          description: '消费',
          createdAt: 1690981561000,
          updatedAt: 1691030210000,
        },
        {
          id: 2,
          name: '个税',
          user_id: 1,
          knowledge_base_id: id,
          parent_id: 0,
          description: '个税',
          createdAt: 1690981561000,
          updatedAt: 1691030210000,
        },
        {
          id: 3,
          name: '印花税',
          user_id: 1,
          knowledge_base_id: id,
          parent_id: 0,
          description: '个税',
          createdAt: 1690981561000,
          updatedAt: 1691030210000,
        },
        {
          id: 4,
          name: '增值税专用发票',
          user_id: 1,
          knowledge_base_id: id,
          parent_id: 0,
          description: '个税',
          createdAt: 1690981561000,
          updatedAt: 1691030210000,
        },
      ],
    };
    res.send(response_data);
  },

  'POST /api/knowledge_bases/:id/tags': (req: Request, res: Response) => {
    res.send({
      id: random(10000, 9999999),
      name: '新增Mock标签',
      parent_id: 0,
      description:
        '标签描述标签描述标签描述标签描述标签描述标签描述标签描述标签描述标签描述标签描述',
      knowledge_base_id: req.params.id,
    });
  },

  'GET /api/knowledge_bases/:id/tags/:tag_id': (req: Request, res: Response) => {
    res.send({
      id: req.params.tag_id,
      name: '消费税',
      user_id: 1,
      knowledge_base_id: req.params.id,
      parent_id: 0,
      description:
        '标签描述标签描述标签描述标签描述标签描述标签描述标签描述标签描述标签描述标签描述',
      createdAt: 1691030210000,
      updatedAt: 1691030210000,
    });
  },

  'PATCH /api/knowledge_bases/:id/tags/:tag_id': (req: Request, res: Response) => {
    res.send({});
  },

  'DELETE /api/knowledge_bases/:id/tags/:tag_id': (req: Request, res: Response) => {
    res.send({});
  },
};
