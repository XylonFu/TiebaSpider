import subprocess
import time
from datetime import datetime


def run_spider():
    process = subprocess.Popen(['python', 'run_spider.py'])
    return process


def log_restart(time):
    with open("restart_log.txt", "a") as log_file:
        log_file.write(f"爬虫重启于: {time}\n")


def terminate_process(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def monitor_process():
    process = run_spider()

    try:
        while True:
            if process.poll() is not None:
                restart_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"爬虫停止了，正在重新启动... 时间：{restart_time}")
                log_restart(restart_time)
                process = run_spider()
            else:
                time.sleep(60)
    except KeyboardInterrupt:
        print("正在停止爬虫...")
        terminate_process(process)
        print("爬虫已停止。")


if __name__ == '__main__':
    monitor_process()
