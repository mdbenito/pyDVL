"""
All value functions return a dictionary of {index: value} and some status /
historical information of the algorithm. This module provides utility functions
to run these in parallel and multiple times, then gather the results for later
processing / reporting.
"""
import multiprocessing as mp
import os
import queue

from collections import OrderedDict
from joblib import Parallel, delayed
from tqdm import tqdm, trange
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type


def available_cpus():
    return len(os.sched_getaffinity(0))


def run_and_gather(fun: Callable[..., Tuple[OrderedDict, List]],
                   num_runs: int,
                   progress: bool = False) \
        -> Tuple[List[OrderedDict], List]:
    """ Runs fun num_runs times and gathers results in a sorted OrderedDict for
    each run, then returns them in a list.

    All results in one run are merged and sorted by value in ascending order.

    :param fun: A callable accepting either no arguments, e.g. a procedure
                wrapped with `valuation.parallel.parallel_wrap()`, which is
                basically `Parallel(delayed(...)(...))(...)`, or exactly one
                integer argument, the run_id, for display purposes.
    :param num_runs: number of times to repeat the whole procedure.
    :param progress: True to display a progress bar at the top of the
                         terminal.
    :return: tuple of 2 lists of length num_runs each, one containing per-run
             results sorted by increasing value, the other historic information
             ("converged") FIXME.
    """

    import inspect
    if 'run_id' not in inspect.signature(fun).parameters.keys():
        _fun = lambda run_id: fun()
    else:
        _fun = fun

    all_values = []
    all_histories = []

    runs = trange(num_runs, position=0) if progress else range(num_runs)
    for i in runs:
        ret = _fun(run_id=i)
        # HACK: Merge results from calls to Parallel
        values = {}
        history = []
        if isinstance(ret, list):
            for vv, hh in ret:
                values.update(vv)
                history.append(hh)
            values = OrderedDict(sorted(values.items(),
                                        key=lambda item: item[1]))
        # Or don't...
        else:
            values, history = ret
        # TODO: checkpoint

        all_values.append(values)
        all_histories.append(history)

    return all_values, all_histories


def parallel_wrap(fun: Callable[[Iterable], Dict[int, float]],
                  arg: Tuple[str, List],
                  num_jobs: int,
                  job_id_arg: str = None) -> Callable:
    """ Wraps an embarrassingly parallelizable fun to run in num_jobs parallel
    jobs, splitting arg into the same number of chunks, one for each job.

    Use later with run_and_gather() to collect results of multiple runs.

    :param fun: A function taking one named argument, with name given in
                `arg[0]`. The argument's value should be a list, given in
                `arg[1]`. Each job will receive a chunk of the complete list.
    :param arg: ("fun_arg_name", [values to split across jobs])
    :param num_jobs: number of parallel jobs to run. Does not accept -1
    :param job_id_arg: argument name to pass the job id for display purposes
                       (e.g. progress bar position). The value passed will be
                       job_id + 1 (to allow for a global bar at position=0). Set
                       to None if not supported by the function.
    """
    # Chunkify the list of values
    n = len(arg[1])
    chunk_size = 1 + int(n / num_jobs)
    values = [list(arg[1][i:min(i + chunk_size, n)])
              for i in arg[1][0:n:chunk_size]]

    if job_id_arg is not None:
        jobs = [delayed(fun)(**{arg[0]: vv, job_id_arg: i + 1})
                for i, vv in enumerate(values)]
    else:
        jobs = [delayed(fun)(**{arg[0]: vv}) for i, vv in enumerate(values)]

    return lambda: Parallel(n_jobs=num_jobs)(jobs)


class InterruptibleWorker(mp.Process):
    """ A simple consumer worker using two queues.

    To use, subclass and implement `_run(self, task) -> result`. See e.g.
    `ShapleyWorker`, then instantiate using `Coordinator` and the methods
     therein.

     TODO: use shared memory to avoid copying data
     FIXME: I don't need both the abort flag and the None task
     """

    def __init__(self,
                 worker_id: int,
                 tasks: mp.Queue,
                 results: mp.Queue,
                 abort: mp.Value):
        """
        :param worker_id: mostly for display purposes
        :param tasks: queue of incoming tasks for the Worker. A task of `None`
                      signals that there is no more processing to do and the
                      worker should exit after finishing its current task.
        :param results: queue of outgoing results.
        :param abort: shared flag to signal that the worker must stop in the
                      next iteration of the inner loop
        """
        # Mark as daemon, so we are killed when the parent exits (e.g. Ctrl+C)
        super().__init__(daemon=True)

        self.id = worker_id
        self.tasks = tasks
        self.results = results
        self._abort = abort

    def run(self):
        task = self.tasks.get(timeout=1.0)  # Wait a bit during start-up (yikes)
        while True:
            if task is None:  # Indicates we are done
                self.tasks.put(None)
                return

            result = self._run(task)

            # Check whether the None flag was sent during _run().
            # This throws away our last results, but avoids a deadlock (can't
            # join the process if a queue has items)
            try:
                task = self.tasks.get_nowait()
                if task is not None:
                    self.results.put(result)
            except queue.Empty:
                return

    def aborted(self):
        return self._abort.value is True

    def _run(self, task: Any) -> Any:
        raise NotImplementedError("Please reimplement")


class Coordinator:
    """ Meh... """
    def __init__(self, processer: Callable[[Any], None]):
        self.tasks_q = mp.Queue()
        self.results_q = mp.Queue()
        self.abort_flag = mp.Value('b', False)
        self.workers = []
        self.process_result = processer

    def instantiate(self, n: int, cls: Type[InterruptibleWorker], **kwargs):
        if not self.workers:
            self.workers = [cls(worker_id=i+1,
                                tasks=self.tasks_q,
                                results=self.results_q,
                                abort=self.abort_flag,
                                **kwargs)
                            for i in range(n)]
        else:
            raise ValueError("Workers already instantiated")

    def put(self, task: Any):
        self.tasks_q.put(task)

    def get_and_process(self, timeout: float = None):
        """"""
        try:
            result = self.results_q.get(timeout=timeout)
            self.process_result(result)
        except queue.Empty as e:
            # TODO: do something here?
            raise e

    def clear_tasks(self):
        # Clear the queue of pending tasks
        try:
            while True:
                self.tasks_q.get_nowait()
        except queue.Empty:
            pass

    def clear_results(self, pbar: Optional[tqdm] = None):
        if pbar:
            pbar.set_description_str("Gathering pending results")
            pbar.total = len(self.workers)
            pbar.reset()
        try:
            while True:
                self.get_and_process(timeout=1.0)
                if pbar:
                    pbar.update()
        except queue.Empty:
            pass

    def start_shift(self):
        for w in self.workers:
            w.start()

    def end_shift(self, pbar: Optional[tqdm] = None):
        self.clear_tasks()
        # Any workers still running won't post their results after the
        # None task has been placed...
        self.tasks_q.put(None)
        self.abort_flag.value = True

        # ... But maybe someone put() some result while we were completing
        # the last iteration of the loop above:
        self.clear_results(pbar)

        # results_q should be empty now
        assert self.results_q.empty(), \
            f"WTF? {self.results_q.qsize()} pending results"
        # HACK: the peeking in workers' run() might empty the queue temporarily
        #  between the peeking and the restoring temporarily, so we allow for
        #  some timeout.
        assert self.tasks_q.get(timeout=0.1) is None, \
            f"WTF? {self.tasks_q.qsize()} pending tasks"

        for w in self.workers:
            w.join()
            w.close()
