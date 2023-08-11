export default {
  'GET /api/conversations': {
    items: [
      {
        id: 1,
        topic: 'Conversation 1',
        description: 'Description 1',
        createdAt: 1691577625000,
        updatedAt: 1691577625000,
      },
      {
        id: 2,
        topic: 'Conversation 2',
        description: 'Description 2',
        createdAt: 1691577625000,
        updatedAt: 1691577625000,
      },
      {
        id: 3,
        topic: 'Conversation 3',
        description: 'Description 3',
        createdAt: 1691577625000,
        updatedAt: 1691577625000,
      },
    ],
    total: 3,
    page: 1,
    size: 10,
    pages: 1,
  },

  'GET /api/conversations/:id': {
    data: {
      id: 1,
      topic: 'Conversation 1',
      description: 'Description 1',
      bot: 2,
      messages: [
        {
          id: 1,
          content: 'Message 1',
          role: 'user', // user or bot
          createdAt: 1691577625000,
          updatedAt: 1691577625000,
        },
        {
          id: 2,
          content: 'Message 2',
          role: 'bot', // user or bot
          createdAt: 1691577625000,
          updatedAt: 1691577625000,
        },
      ],
      createdAt: 1691577625000,
      updatedAt: Date.now(),
    },
  },

  'POST /api/conversations': (req: any, res: any) => {
    // payload:
    // {
    //     "bot": 2
    // }
    res.send({
      id: 1,
      topic: 'Conversation 1',
      description: 'Description 1',
      createdAt: 1691577625000,
      updatedAt: Date.now(),
      bot: 2,
    });
  },

  'POST /api/conversations/:id/messages': (req: any, res: any) => {
    // payload:
    // {
    //     "content": "Message 1"
    // }

    res.send({
      items: [
        {
          id: 1,
          content: 'Message 1',
          role: 'user', // user or bot
          createdAt: 1691577625000,
        },
        {
          id: 2,
          content: 'Message 2',
          role: 'bot', // user or bot
          createdAt: 1691577625000,
        },
      ],
      total: 2,
      page: 1,
      size: 10,
      pages: 1,
    });
  },

  'DELETE /api/conversations/:id': (req: any, res: any) => {
    res.send({});
  },
};
