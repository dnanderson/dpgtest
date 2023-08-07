import atomics
from multiprocessing import Process, shared_memory


def fn(shmem_name: str, width: int, n: int) -> None:
    shmem = shared_memory.SharedMemory(name=shmem_name)
    buf = shmem.buf[:width]
    with atomics.atomicview(buffer=buf, atype=atomics.INT) as a:
        for _ in range(n):
            a.inc()
    del buf
    shmem.close()


if __name__ == "__main__":
    # setup
    width = 4
    shmem = shared_memory.SharedMemory(create=True, size=width)
    buf = shmem.buf[:width]
    total = 10_000
    # run processes to completion
    p1 = Process(target=fn, args=(shmem.name, width, total // 2))
    p2 = Process(target=fn, args=(shmem.name, width, total // 2))
    p1.start(), p2.start()
    p1.join(), p2.join()
    # print results and cleanup
    with atomics.atomicview(buffer=buf, atype=atomics.INT) as a:
        print(f"a[{a.load()}] == total[{total}]")
    del buf
    shmem.close()
    shmem.unlink()