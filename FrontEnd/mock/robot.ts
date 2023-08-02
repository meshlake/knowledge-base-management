import { Request, Response } from 'express';

export default {
  'GET /api/chatbot/list': {
    items: [
      {
        id: 1,
        name: 'chatbot1',
        description:
          '机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述',
        createdAt: '2021-01-01 00:00:00',
      },
      {
        id: 2,
        name: 'chatbot2',
        description:
          '机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述',
        createdAt: '2021-01-01 00:00:00',
      },
      {
        id: 3,
        name: 'chatbot3',
        description:
          '机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述机器人描述',
        createdAt: '2021-01-01 00:00:00',
      },
    ],
  },
  'POST /api/chatbot': (req: Request, res: Response) => {
    res.send({
      success: true,
    });
  },
  'DELETE /api/chatbot/:id': (req: Request, res: Response, id: string) => {
    res.send({
      id: req.params.id,
      success: true,
    });
  },
};
