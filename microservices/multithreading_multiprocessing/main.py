import threading
import time
class Demo():
    def __init__(self):
        self.result = []
        self.final_result = []

    def insert_number(self):
        count = 0
        while True:
            self.result.append(count)
            count = count + 1
            print('inside first thread ****>>>>' + str(self.result))
            time.sleep(4)
    
    def insert_event_number(self):
        while True:
            for i in self.result:
                if i%2==0:
                    self.final_result.append(i)
                    print('inside second thread ****>>>>' + str(self.final_result))
                    time.sleep(4)

if __name__ == "__main__":
    demo_instance = Demo()
    # numbers = [1, 2, 3]
    # p = threading.Thread(target=demo_instance.calc_square, args=(numbers,))
    threading.Thread(target=demo_instance.insert_number).start()
    threading.Thread(target=demo_instance.insert_event_number).start()
    # t1.start()
    # t2.start()
    

    print('outside  thread *****>>>' + str(demo_instance.result))
