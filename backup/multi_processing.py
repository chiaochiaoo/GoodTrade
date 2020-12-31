from multiprocessing import Process, Pipe
import time

def f(conn):
    i = 0
    while i<50:
        conn.send("wew")
        i+=1
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()

    time.sleep(0.1)
    k = []
    while len(k)!=50:
        while parent_conn.poll():
            k.append(parent_conn.recv())
            
        print(len(k))
        print("check")

    p.join()