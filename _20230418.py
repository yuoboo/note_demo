from threading import Thread


class Q:

    def __init__(self):
        self.queue = []

    def put_q(self, a):
        self.queue.append(a)

    def get_q(self):
        if self.is_empty():
            raise
        return self.queue[0]

    def is_empty(self):
        if len(self.queue) == 0:
            return True
        return False


def handle_task(t):
    print(f"handle task: {t}")


q = Q()


def put_task(t):
    q.put_q(t)


def get_task():
    t = q.get_q()
    handle_task(t)


t1 = Thread(target=put_task, args=[1])
t2 = Thread(target=get_task, args=[])
t1.start()
t2.start()

