from app.jobs import JobStore


def run_once() -> dict[str, int | str] | None:
    store = JobStore()
    store.enqueue("noop")
    return store.run_once()


if __name__ == "__main__":
    print(run_once())

