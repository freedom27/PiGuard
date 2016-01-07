from time import sleep
import queue
import threading
import factory


class BaseStatusesThread(threading.Thread):

    def __init__(self, statuses_queue):
        super().__init__()
        self._statuses_queue = statuses_queue
        self._stop = False

    def stop(self):
        self._stop = True


class StatusesHandlerThread(BaseStatusesThread):

    def run(self):
        handler = factory.get_status_handler()
        while not self._stop:
            try:
                status = statuses_queue.get()
                handler.manage_status(status)
                statuses_queue.task_done()
            except:
                print("Unexpected error - Worker")

        print("Statuses handler thread stopped!")


class StatusesGeneratorThread(BaseStatusesThread):

    def run(self):
        generator = factory.get_status_generator()
        while not self._stop:
            try:
                status = generator.get_current_status()
                statuses_queue.put(status)
                sleep(sampling_frequence)
            except:
                print("Unexpected error - Main")
                
        #add an extra status in the queue to avoid
        status = generator.get_current_status()
        statuses_queue.put(status)
        print("Statuses generator thread stopped!")


def command_console(server):
    server.serve_forever()

if __name__ == "__main__":
    sampling_frequence = factory.get_sampling_interval()

    statuses_queue = queue.Queue()
    commands_queue = queue.Queue()

    handler_thread = StatusesHandlerThread(statuses_queue)
    handler_thread.start()

    generator_thread = StatusesGeneratorThread(statuses_queue)
    generator_thread.start()

    command_console_server = factory.get_console_server(commands_queue)
    console_thread = threading.Thread(target=command_console, args=(command_console_server, ))
    console_thread.start()

    while True:
        command = commands_queue.get()
        if command == "stop":
            handler_thread.stop = True
            generator_thread.stop = True
        elif command == "exit":
            handler_thread.stop = True
            generator_thread.stop = True
            command_console_server.shutdown()
            break
        elif command == "start":
            if handler_thread.stop and generator_thread.stop:
                handler_thread = StatusesHandlerThread(statuses_queue)
                generator_thread = StatusesGeneratorThread(statuses_queue)
                generator_thread.start()
                handler_thread.start()

    print("PiGuard Terminated")