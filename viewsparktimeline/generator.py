import sys
import random
from heapq import heappush, heappop
from viewsparktimeline.utils import read_events
from viewsparktimeline.outputs import SvgOutput
from viewsparktimeline.exceptions import CliException


def anticipate_task_end(time_uncertainty_ms, events):
    """Sort by time an almost-sorted stream of Spark events.

    The `SparkListenerTaskEnd` are slightly anticipated to handle cases in which
    tasks seem to overlap due to an imprecision in the logged times.

    Arguments:
    * `time_uncertainty_ms` is the maximum allowed imprecision in the times.
    * `events` is a stream of Spark events of type dict.
    """
    timeline_buffer = []
    max_seen_time = 0
    start_time_of_task = {}
    for data in events:
        # Add a new event to the timeline_buffer
        if data["Event"] == "SparkListenerTaskStart":
            task_info = data["Task Info"]
            task_id = int(task_info["Task ID"])
            launch_time = int(task_info["Launch Time"])
            max_seen_time = max(max_seen_time, launch_time)
            start_time_of_task[task_id] = launch_time
            # The tuple contains `task_id` to compare tasks that start at the same time
            heappush(timeline_buffer, (launch_time, 0, task_id, data))
        elif data["Event"] == "SparkListenerTaskEnd":
            task_info = data["Task Info"]
            task_id = int(task_info["Task ID"])
            finish_time = int(task_info["Finish Time"])
            max_seen_time = max(max_seen_time, finish_time)
            current_task_start_time = start_time_of_task.pop(task_id)
            # Anticipate the end by `time_uncertainty_ms`
            anticipated_finish_time = max(
                finish_time - time_uncertainty_ms,
                current_task_start_time
            )
            heappush(timeline_buffer, (anticipated_finish_time, 1, task_id, data))
        else:
            continue

        # Yeal all elements more than `time_uncertainty_ms` in the past
        min_time_in_buffer = timeline_buffer[0][0]
        while max_seen_time - min_time_in_buffer >= time_uncertainty_ms:
            yield heappop(timeline_buffer)[3]
            if timeline_buffer:
                min_time_in_buffer = timeline_buffer[0][0]
            else:
                break

    # Drain the timeline_buffer at the end
    while timeline_buffer:
        yield heappop(timeline_buffer)[3]


def generate(events_file_path, output_file_path, time_uncertainty_ms):
    """Analyze a Spark log file and generate an SVG visualization.

    `time_uncertainty_ms` is the maximum allowed time imprecision in the log.
    """
    total_tasks = 0
    total_cores = 0
    min_time = None
    max_time = None
    min_task_duration = None
    max_task_duration = None
    cumulative_task_duration = 0
    executor_free_cores = {}

    # First pass: count the number of total cores and compute other statistics
    for data in read_events(events_file_path):
        if data["Event"] == "SparkListenerExecutorAdded":
            executor_id = data["Executor ID"]
            executor_info = data["Executor Info"]
            executor_total_cores = int(executor_info["Total Cores"])
            executor_free_cores[executor_id] = set(
                range(total_cores, total_cores + executor_total_cores)
            )
            total_cores += executor_total_cores

        elif data["Event"] == "SparkListenerTaskEnd":
            task_info = data["Task Info"]
            task_id = task_info["Task ID"]
            launch_time = int(task_info["Launch Time"])
            finish_time = int(task_info["Finish Time"])
            task_duration = finish_time - launch_time

            if min_time is None or launch_time < min_time:
                min_time = launch_time
            if max_time is None or finish_time > max_time:
                max_time = finish_time

            if min_task_duration is None or task_duration < min_task_duration:
                min_task_duration = task_duration
            if max_task_duration is None or task_duration > max_task_duration:
                max_task_duration = task_duration

            total_tasks += 1
            cumulative_task_duration += task_duration

    total_duration = max_time - min_time
    cluster_utilization = cumulative_task_duration / total_duration / total_cores

    print("Total cores: {}".format(total_cores))
    print("Total duration: {:.1f}s".format(total_duration / 1000))
    print("Number of tasks: {}".format(total_tasks))
    print("Min task duration: {:.1f}s".format(min_task_duration / 1000))
    print("Max task duration: {:.1f}s".format(max_task_duration / 1000))
    print("Cluster utilization: {:.2f}%".format(cluster_utilization * 100))

    # Second pass: generate the SVG visualization
    print("Drawing events...")
    output_image = SvgOutput(
        output_file_path,
        total_duration,
        max_task_duration * 0.8,
        total_cores,
        (
            "Total duration: {:.1f}s, Cluster utilization: {:.2f}%"
            .format(total_duration / 1000, cluster_utilization * 100)
        )
    )

    active_task_core = {}

    if time_uncertainty_ms <= 0:
        events = read_events(events_file_path)
    else:
        events = anticipate_task_end(time_uncertainty_ms, read_events(events_file_path))

    for data in events:
        if data["Event"] == "SparkListenerTaskStart":
            task_info = data["Task Info"]
            task_id = task_info["Task ID"]
            executor_id = task_info["Executor ID"]

            free_cores = executor_free_cores[executor_id]
            if not free_cores:
                raise CliException(
                    (
                        "ERROR: There is an overlap of more than {:.3f}s (task ID {} has no free core). "
                        "Increase parameter '--time-uncertainty' to something over {}."
                    ).format(time_uncertainty_ms / 1000, task_id, time_uncertainty_ms)
                )
            core_id = random.sample(free_cores, 1)[0]
            free_cores.remove(core_id)
            active_task_core[task_id] = core_id

        elif data["Event"] == "SparkListenerTaskEnd":
            task_info = data["Task Info"]
            task_id = task_info["Task ID"]
            executor_id = task_info["Executor ID"]

            core_id = active_task_core.pop(task_id, None)
            if core_id is None:
                raise CliException(
                    (
                        "ERROR: We encountered the end-event of task ID {} before its start-event. "
                        "Increase parameter '--time-uncertainty' to something over {}."
                    ).format(task_id, time_uncertainty_ms)
                )
            executor_free_cores[executor_id].add(core_id)

            stage_id = data["Stage ID"]
            stage_attempt_id = data["Stage Attempt ID"]
            task_end_reason = data["Task End Reason"]["Reason"]
            launch_time = int(task_info["Launch Time"])
            finish_time = int(task_info["Finish Time"])
            task_duration = finish_time - launch_time
            start_time = launch_time - min_time
            end_time = finish_time - min_time

            output_image.draw_task(
                core_id,
                start_time,
                task_duration,
                task_end_reason,
                (
                    "Task ID {}, Stage ID {}, attempt {} ({:.1f}s)"
                    .format(task_id, stage_id, stage_attempt_id, task_duration / 1000)
                )
            )

    output_image.save()
