import ujson as json
import mmap


def read_events(events_file_path):
    """Read a stream of Spark events from a log file.
    """
    print("Read events from '{}'...".format(events_file_path))
    with open(events_file_path, "r") as file:
        mm_file = mmap.mmap(
            file.fileno(),
            0,
            access=mmap.ACCESS_READ
        )
        while True:
            line = mm_file.readline()
            if line:
                yield json.loads(line)
            else:
                break


def transition(value, maximum, start_point, end_point):
    """Linear interpolation between `start_point` and `end_point`.
    """
    return start_point + (end_point - start_point) * value / maximum


def transition3(value, maximum, start, end):
    """Pointwise linear interpolation between `start` and `end`.
    """
    (s1, s2, s3) = start
    (e1, e2, e3) = end
    r1 = transition(value, maximum, s1, e1)
    r2 = transition(value, maximum, s2, e2)
    r3 = transition(value, maximum, s3, e3)
    return (r1, r2, r3)
