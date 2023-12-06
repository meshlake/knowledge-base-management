export default class Stream {
  interval: number; // 每个字符间隔时间，毫秒
  queue: string[]; // 字符数组
  done: boolean = false;
  consume: (data: string) => void; // 消费函数

  constructor(interval: number, consume: (data: string) => void) {
    this.interval = interval;
    this.queue = [];
    this.consume = consume;
    this.run();
  }

  push(data: string[]) {
    this.queue.push(...data);
  }

  end() {
    this.done = true;
  }

  run() {
    const id = setInterval(() => {
      if (this.done && this.queue.length === 0) {
        clearInterval(id);
        return;
      }
      const char = this.queue.shift();
      if (char !== undefined) {
        this.consume(char);
      }
    }, this.interval);
  }
}
