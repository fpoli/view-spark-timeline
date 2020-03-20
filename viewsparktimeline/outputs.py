import svgwrite
from colorsys import hsv_to_rgb
from viewsparktimeline.utils import transition3


class AbstractOutputImage:
    """Base class to generate and save a visualization of Spark tasks.
    """
    def __init__(self, output_path, total_duration, slow_task_duration, total_cores, description,
                 spacing=0, task_height=5, total_width=1500):
        self.output_path = output_path
        self.total_duration = total_duration
        self.slow_task_duration = slow_task_duration
        self.total_cores = total_cores
        self.description = description
        self.spacing = spacing
        self.task_height = task_height
        self.total_width = total_width

        self.total_height = spacing + total_cores * (spacing + task_height)
        self.time_scale = (total_width - 2 * spacing) / total_duration
        # self.fast_task_color = (-0.35, 1.0, 200 / 255)  # blue
        self.fast_task_color = (0.33, 1.0, 150 / 255)   # green
        self.slow_task_color = (0.0, 1.0, 200 / 255)    # red

    def task_color(self, task_duration, task_end_reason):
        """Computes the color of a task.
        """
        if task_end_reason != "Success":
            return (0, 0, 0)
        else:
            r, g, b = hsv_to_rgb(*transition3(
                min(task_duration, self.slow_task_duration),
                self.slow_task_duration,
                self.fast_task_color,
                self.slow_task_color
            ))
            return (r * 255, g * 255, b * 255)

    def draw_task(self, x, y, task_width, task_color):
        """Draw one more task on the image.
        """
        raise NotImplementedError

    def save(self):
        """Save the image to disk.
        """
        raise NotImplementedError


class SvgOutput(AbstractOutputImage):
    """Class to generate and save an SVG visualization of Spark tasks.
    """
    def __init__(self, output_path, total_duration, slow_task_duration, total_cores, description,
                 spacing=0, task_height=5, total_width=1500):
        super().__init__(output_path, total_duration, slow_task_duration,
                         total_cores, description, spacing, task_height, total_width)

        dwg = svgwrite.Drawing(self.output_path, debug=False)
        viewport = dwg.g(id="viewport")
        tasks_dwg = dwg.g(id="tasks")

        bg_rect = dwg.rect(
            (0, 0), (self.total_width, self.total_height), fill="rgb(229,252,255)")
        bg_rect.set_desc(self.description)

        viewport.add(bg_rect)
        viewport.add(tasks_dwg)
        dwg.add(viewport)

        self.dwg = dwg
        self.tasks_dwg = tasks_dwg

    def draw_task(self, core_id, start_time, task_duration, task_end_reason, task_description):
        """Draw one more task on the image.
        """
        y = self.spacing + core_id * (self.spacing + self.task_height)
        x = self.spacing + start_time * self.time_scale
        task_width = task_duration * self.time_scale
        color = "rgb({:.0f},{:.0f},{:.0f})".format(
            *self.task_color(task_duration, task_end_reason)
        )
        task_rect = self.dwg.rect(
            (x, y),
            (task_width, self.task_height),
            fill=color
            # , **{"fill-opacity": "0.2"}
        )
        task_rect.set_desc(task_description)
        self.tasks_dwg.add(task_rect)

    def save(self):
        """Save the image to disk.
        """
        if False:
            # Enable pan and zoom actions in a browser.
            # TODO: Embed JS in SVG, to avoid having an external dependency.
            self.dwg.add(self.dwg.script("../lib/svgpan.js"))
        else:
            self.dwg.update({
                "preserveAspectRatio": "none",
                "viewBox": "0 0 {} {}".format(self.total_width, self.total_height)
            })

        print("SVG size: {} {}".format(self.total_width, self.total_height))
        print("Saving SVG...")
        self.dwg.save()


# TODO: class PngOutput(AbstractOutputImage)
