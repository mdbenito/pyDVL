Search.setIndex({"docnames": ["getting-started", "index", "knn_shapley", "valuation/cli", "valuation/dist_shapley", "valuation/index", "valuation/loo", "valuation/loo/naive", "valuation/reporting", "valuation/reporting/plots", "valuation/reporting/scores", "valuation/shapley", "valuation/shapley/knn", "valuation/shapley/montecarlo", "valuation/shapley/naive", "valuation/utils", "valuation/utils/caching", "valuation/utils/dataset", "valuation/utils/logging", "valuation/utils/numeric", "valuation/utils/parallel", "valuation/utils/progress", "valuation/utils/types", "valuation/utils/utility"], "filenames": ["getting-started.rst", "index.rst", "knn_shapley.ipynb", "valuation/cli.rst", "valuation/dist_shapley.rst", "valuation/index.rst", "valuation/loo.rst", "valuation/loo/naive.rst", "valuation/reporting.rst", "valuation/reporting/plots.rst", "valuation/reporting/scores.rst", "valuation/shapley.rst", "valuation/shapley/knn.rst", "valuation/shapley/montecarlo.rst", "valuation/shapley/naive.rst", "valuation/utils.rst", "valuation/utils/caching.rst", "valuation/utils/dataset.rst", "valuation/utils/logging.rst", "valuation/utils/numeric.rst", "valuation/utils/parallel.rst", "valuation/utils/progress.rst", "valuation/utils/types.rst", "valuation/utils/utility.rst"], "titles": ["Getting started", "valuation", "KNN Shapley", "cli", "dist_shapley", "valuation", "loo", "naive", "reporting", "plots", "scores", "shapley", "knn", "montecarlo", "naive", "utils", "caching", "dataset", "logging", "numeric", "parallel", "progress", "types", "utility"], "terms": {"welcom": 0, "valuat": [0, 2, 15, 16, 17, 18, 19, 20], "librari": [0, 15, 20], "see": [0, 15, 19, 20], "project": 0, "s": [0, 9, 15, 16, 19], "repositori": 0, "more": [0, 11, 13], "inform": [0, 20], "get": 1, "start": [1, 9, 20], "knn": [1, 5, 11], "shaplei": [1, 5, 10, 12, 13, 14, 19], "cli": [1, 5], "dist_shaplei": [1, 5], "loo": [1, 5, 7], "naiv": [1, 5, 6, 11, 13, 21], "report": [1, 5, 20], "plot": [1, 2, 5, 8], "score": [1, 5, 7, 8, 11, 13, 15, 22, 23], "montecarlo": [1, 5, 11, 19], "util": [1, 2, 5, 11, 13, 14, 16, 18, 19, 20], "cach": [1, 5, 15, 20], "dataset": [1, 2, 5, 7, 10, 11, 12, 13, 15, 23], "log": [1, 5, 15], "numer": [1, 5, 15], "parallel": [1, 5, 10, 13, 15, 19], "progress": [1, 5, 7, 10, 11, 12, 13, 14, 15, 20, 23], "type": [1, 5, 15, 20], "index": [1, 9, 11, 13, 15, 17, 20], "search": 1, "page": 1, "1": [2, 9, 11, 13, 15, 16, 19, 20, 22], "load_ext": 2, "autoreload": 2, "2": [2, 15, 19, 20], "import": [2, 15, 16, 19], "os": 2, "sy": 2, "from": [2, 9, 10, 11, 12, 13, 15, 17, 18, 19], "pathlib": 2, "path": 2, "matplotlib": [2, 9], "pyplot": 2, "plt": [2, 9], "numpi": 2, "np": [2, 15, 20], "sklearn": [2, 10, 15, 17], "neighbor": 2, "kneighborsclassifi": [2, 12], "exact_knn_shaplei": [2, 12], "3": [2, 15, 16, 18], "add": [2, 10, 11, 13, 15, 20], "notebook": 2, "directori": 2, "abl": 2, "py": [2, 12, 15, 17], "first": [2, 11, 13], "one": [2, 11, 13, 15, 20], "need": [2, 15, 16, 20], "when": [2, 11, 13, 15, 16], "run": [2, 9, 11, 13, 15, 19, 20], "directli": 2, "insert": 2, "0": [2, 9, 10, 11, 13, 15, 16, 17, 19, 20, 23], "fspath": 2, "resolv": 2, "second": [2, 15, 16], "test": [2, 10, 11, 13, 18], "4": [2, 18], "plot_iri": 2, "5": 2, "data": [2, 7, 9, 10, 11, 12, 13, 15, 17, 20, 23], "from_sklearn": [2, 15, 17], "load_iri": 2, "6": 2, "n_neighbor": 2, "valu": [2, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21], "7": 2, "effect": 2, "k": [2, 19], "v": 2, "item": [2, 10, 16], "ab": 2, "arrai": 2, "8": [2, 15, 17, 18], "9": [2, 15, 20], "plot_test": 2, "true": [2, 7, 11, 12, 13, 14, 15, 16, 18, 19, 21, 23], "maybe_init_task": 3, "task_nam": 3, "str": [3, 9, 15, 16, 17, 18, 20, 22], "clearml_config": 3, "dict": [3, 9, 10, 11, 13, 15, 16, 22], "task_param": 3, "sourc": [3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], "fixm": [3, 15, 16, 20], "task": [3, 20], "connect": 3, "work": [3, 15, 17], "copi": [3, 13, 20], "param": [3, 15, 20], "naive_loo": 7, "model": [7, 10, 11, 12, 13, 15, 23], "supervisedmodel": [7, 10, 15, 22, 23], "bool": [7, 11, 12, 13, 14, 15, 16, 19, 21, 23], "ordereddict": [7, 9, 10, 11, 12, 13, 14], "int": [7, 9, 10, 11, 13, 15, 17, 18, 19, 20, 21, 22, 23], "float": [7, 9, 10, 11, 13, 15, 16, 17, 19, 20, 22, 23], "comput": [7, 9, 10, 11, 12, 13, 14, 15, 16, 19], "each": [7, 9, 10, 11, 13, 15, 18, 20], "train": [7, 10], "point": [7, 10, 11, 13], "shaded_mean_std": 9, "ndarrai": [9, 10, 15, 17, 19, 22], "color": 9, "num_std": 9, "kwarg": [9, 15, 20, 22], "The": [9, 12, 15, 16, 20], "usual": 9, "mean": [9, 11, 13, 15, 20], "x": [9, 15, 17, 19, 20, 22], "std": 9, "deviat": 9, "aggreg": [9, 15, 20], "paramet": [9, 10, 11, 12, 13, 15, 16, 19, 20, 21], "axi": 9, "i": [9, 11, 13, 15, 17, 19, 20], "e": [9, 11, 13, 15, 19, 20, 22], "number": [9, 11, 13, 15, 17, 19, 20], "standard": 9, "shade": 9, "around": 9, "ar": [9, 11, 13, 15, 16, 19, 20], "forward": [9, 10, 15, 21], "call": [9, 12, 20], "shapley_result": 9, "result": [9, 15, 20], "filenam": 9, "option": [9, 15, 16, 17, 19, 20, 23], "none": [9, 11, 13, 15, 16, 17, 18, 19, 20, 23], "For": [9, 11, 13], "savefig": 9, "set": [9, 10, 11, 13, 15, 19, 20, 21], "disabl": [9, 15, 16], "save": 9, "here": [9, 15, 22, 23], "an": [9, 11, 13, 15, 17, 19, 20, 22], "exampl": 9, "dictionari": [9, 20], "all_valu": 9, "num_run": [9, 15, 20], "num_point": 9, "backward_scor": 9, "backward_scores_revers": 9, "backward_random_scor": 9, "forward_scor": 9, "forward_scores_revers": 9, "forward_random_scor": 9, "max_iter": [9, 11, 13], "score_nam": 9, "spearman_correl": 9, "vv": 9, "list": [9, 10, 11, 13, 15, 19, 20], "num_valu": 9, "pvalu": 9, "simpl": [9, 13, 18, 20], "matrix": 9, "spearman": [9, 19], "correl": [9, 19], "pair": 9, "kei": [9, 10, 15, 16], "us": [9, 11, 12, 13, 14, 15, 16, 18, 20, 21], "onli": [9, 11, 13, 15, 22], "mani": [9, 11, 13, 19], "sort_values_arrai": 10, "sort_values_histori": 10, "map": 10, "sequenc": [10, 15, 19], "sort": 10, "sample_id": 10, "last": [10, 11, 13], "sort_valu": 10, "value_float": 10, "backward_elimin": 10, "indic": [10, 11, 13, 15, 17], "job_id": [10, 15, 20], "after": [10, 11, 13, 19], "increment": 10, "remov": 10, "duh": [10, 19], "split": [10, 12, 15, 20], "retrain": 10, "happen": 10, "bar": [10, 11, 12, 13, 15, 20, 21], "posit": [10, 15, 17, 20], "execut": [10, 15, 20], "return": [10, 11, 13, 15, 16, 17, 19, 20, 21], "forward_select": 10, "ad": 10, "addit": 10, "compute_fb_scor": 10, "dure": 10, "select": 10, "backward": 10, "elimin": 10, "increas": [10, 11, 13, 17], "implement": [10, 11, 13, 20], "fit": [10, 15, 22], "truncated_montecarlo_shaplei": [11, 13], "u": [11, 13, 14, 15, 23], "bootstrap_iter": [11, 13, 15, 23], "min_scor": [11, 13], "score_toler": [11, 13], "min_valu": [11, 13, 15, 19], "value_toler": [11, 13], "num_work": [11, 13], "run_id": [11, 13, 20], "fals": [11, 13, 15, 19, 23], "tupl": [11, 13, 15, 23], "approxim": [11, 13, 19], "instead": [11, 13, 15, 16], "expect": [11, 13, 18], "we": [11, 13], "sequenti": [11, 13], "permut": [11, 13, 14], "stop": [11, 13, 19], "perform": [11, 13], "doesn": [11, 13], "t": [11, 13, 15, 19, 20, 21], "beyond": [11, 13], "threshold": [11, 13, 15, 16], "keep": [11, 13], "sampl": [11, 13, 15, 17, 19], "updat": [11, 13, 16], "all": [11, 13, 15, 16, 19, 20, 22], "until": [11, 13], "chang": [11, 13], "move": [11, 13], "averag": [11, 13, 15, 20], "fall": [11, 13], "below": [11, 13, 15, 16], "anoth": [11, 13], "object": [11, 12, 13, 15, 16, 17, 20, 21, 22, 23], "function": [11, 13, 15, 16, 17, 19, 20], "repeat": [11, 13, 15, 20], "global_scor": [11, 13], "thi": [11, 13, 15, 16, 17, 18, 19, 20], "time": [11, 13, 15, 20], "estim": [11, 13, 19], "its": [11, 13], "varianc": [11, 13], "so": [11, 13], "order": [11, 13, 15, 16, 19], "everi": [11, 13], "within": [11, 13], "stddev": [11, 13], "bootstrap": [11, 13], "over": [11, 13], "complet": [11, 13], "least": [11, 13, 19], "deriv": [11, 13, 15, 19], "min_step": [11, 13], "ep": [11, 13, 19], "close": [11, 13, 19], "never": [11, 13], "than": [11, 12, 13], "iter": [11, 13, 15, 16, 19, 21], "total": [11, 13], "across": [11, 13, 15, 20], "worker": [11, 13, 20], "100": [11, 13], "most": [11, 13], "job": [11, 13, 15, 20], "process": [11, 13, 15, 18, 20], "g": [11, 13, 15, 19, 20, 22], "available_cpu": [11, 13, 15, 20], "thread": [11, 13, 15, 20], "displai": [11, 12, 13, 15, 20, 21], "purpos": [11, 13, 15, 20], "locat": [11, 13], "tqdm": [11, 13, 15, 20, 21], "serial_truncated_montecarlo_shaplei": [11, 13], "truncat": [11, 13], "method": [11, 13, 15, 20, 21], "cpu": [11, 13], "whether": [11, 12, 13, 19], "permutation_montecarlo_shaplei": [11, 13], "num_job": [11, 13, 15, 19, 20], "combinatorial_montecarlo_shaplei": [11, 13], "combinatori": [11, 13, 14], "definit": [11, 13, 14], "combinatorial_exact_shaplei": [11, 14], "exact": [11, 12, 14], "permutation_exact_shaplei": [11, 14], "classifi": 12, "regressor": 12, "extract": 12, "modifi": 12, "nor": 12, "other": [12, 19], "get_param": 12, "datashaplei": 13, "don": [13, 20, 21], "foolishli": 13, "rai": 13, "whatev": [13, 18], "distribut": [13, 16, 19], "multipl": [13, 18, 20], "machin": 13, "provid": [13, 20], "singl": 13, "interfac": 13, "montecarlo_shaplei": 13, "backend": [13, 15, 16, 20], "argument": [13, 15, 16, 19, 20], "multiprocess": [13, 15, 20], "serial": 13, "group": 13, "memcach": [15, 16, 19], "client_config": [15, 16, 19], "clientconfig": [15, 16, 19], "ignore_arg": [15, 16], "decor": [15, 16, 22], "callabl": [15, 16, 20], "have": [15, 16, 19], "transpar": [15, 16], "code": [15, 16], "constant": [15, 16], "except": [15, 16], "those": [15, 16], "gener": [15, 16, 19, 20], "remot": [15, 16], "due": [15, 16], "pickl": [15, 16, 18], "class": [15, 16, 17, 18, 19, 20, 21, 22, 23], "ha": [15, 16], "drawback": [15, 16], "messi": [15, 16], "docstr": [15, 16], "config": [15, 16], "pymemcach": [15, 16], "client": [15, 16, 19], "Will": [15, 16], "merg": [15, 16], "top": [15, 16], "default": [15, 16, 20], "configur": [15, 16, 18, 19, 23], "take": [15, 16, 19, 20], "do": [15, 16, 20, 21], "keyword": [15, 16], "account": [15, 16], "hash": [15, 16], "wrap": [15, 16, 21], "usag": [15, 16], "A": [15, 16, 19, 20, 21, 22, 23], "default_config": [15, 16], "server": [15, 16, 18], "localhost": [15, 16, 18], "11211": [15, 16], "connect_timeout": [15, 16], "timeout": [15, 16, 20], "small": [15, 16], "packet": [15, 16], "consolid": [15, 16], "no_delai": [15, 16], "serd": [15, 16], "pickleserd": [15, 16], "pickle_vers": [15, 16], "arg": [15, 20, 22], "base": [15, 16, 17, 18, 19, 20, 21, 22, 23], "protocol": [15, 22], "pedant": [15, 22], "hint": [15, 22], "y": [15, 19, 22], "predict": [15, 22], "x_train": [15, 17], "y_train": [15, 17], "x_test": [15, 17], "y_test": [15, 17], "feature_nam": [15, 17], "target_nam": [15, 17], "descript": [15, 17], "meh": [15, 17, 20, 22], "just": [15, 17, 18, 20], "bunch": [15, 17], "properti": [15, 17, 21], "shortcut": [15, 17], "should": [15, 17], "probabl": [15, 17, 19, 20], "ditch": [15, 17], "redesign": [15, 17], "featur": [15, 17], "name": [15, 17, 20], "indexexpress": [15, 17], "target": [15, 17], "contigu": [15, 17], "integ": [15, 17, 19], "len": [15, 17], "dim": [15, 17], "dimens": [15, 17], "classmethod": [15, 17], "train_siz": [15, 17], "random_st": [15, 17], "construct": [15, 17], "load_": [15, 17], "pd": [15, 17], "modul": [15, 17, 20], "panda": [15, 17], "home": [15, 17], "runner": [15, 17], "tox": [15, 17], "doc": [15, 17, 18], "lib": [15, 17], "python3": [15, 17], "site": [15, 17], "packag": [15, 17], "__init__": [15, 17], "from_panda": [15, 17], "df": [15, 17], "datafram": [15, 17], "That": [15, 17, 19, 23], "map_reduc": [15, 20], "fun": [15, 20], "mapreducejob": [15, 20], "collect": [15, 19, 20], "loki": [15, 20], "embarrassingli": [15, 20], "ot": [15, 20], "same": [15, 20], "chunk": [15, 20], "It": [15, 20], "alloc": [15, 20], "90": [15, 20], "10": [15, 20], "whole": [15, 20], "evenli": [15, 20], "among": [15, 20], "them": [15, 20], "If": [15, 20], "two": [15, 20], "core": [15, 20], "five": [15, 20], "success": [15, 20], "receiv": [15, 18, 20], "per": [15, 20], "reduc": [15, 20], "creat": [15, 20], "from_fun": [15, 20], "doe": [15, 20], "accept": [15, 19, 20], "etc": [15, 20], "kwd": [15, 20], "There": [15, 20], "77": [15, 20], "r": [15, 20], "static": [15, 20], "lambda": [15, 20], "job_id_arg": [15, 20], "run_id_arg": [15, 20], "Not": [15, 20], "actual": [15, 20], "oper": [15, 20, 22], "reduct": [15, 20], "itself": [15, 20], "join": [15, 20], "functool": [15, 20], "Or": [15, 20], "pass": [15, 20], "id": [15, 20], "allow": [15, 16, 20, 22], "global": [15, 20], "support": [15, 20, 21], "vanishing_deriv": [15, 19], "atol": [15, 19], "row": [15, 19], "whose": [15, 19], "empir": [15, 19], "converg": [15, 19], "zero": [15, 19], "up": [15, 19], "absolut": [15, 19], "toler": [15, 19], "unpack": [15, 22], "cl": [15, 20, 22], "attribut": [15, 22], "doubl": [15, 22], "asterisk": [15, 22], "dataclass": [15, 22], "schtuff": [15, 22], "b": [15, 22], "d": [15, 22], "scorer": [15, 23], "catch_error": [15, 23], "default_scor": [15, 23], "enable_cach": [15, 19, 23], "cache_opt": [15, 23], "memcachedconfig": [15, 16, 23], "conveni": [15, 23], "wrapper": [15, 23], "memoiz": [15, 23], "bootstrap_test_scor": [15, 23], "lack": [15, 23], "better": [15, 23], "place": [15, 23], "powerset": [15, 19], "power": [15, 19], "subset": [15, 19], "grow": [15, 19], "size": [15, 19], "random_powerset": [15, 19], "random": [15, 19], "maybe_progress": [15, 21], "union": [15, 21], "rang": [15, 21], "enumer": [15, 19, 21], "tqdm_kwarg": [15, 21], "tqdm_asyncio": [15, 21], "either": [15, 21], "mock": [15, 21], "which": [15, 20, 21], "well": [15, 21], "ignor": [15, 21], "ani": [15, 19, 20, 21], "access": [15, 21], "todo": [16, 20], "differ": 16, "0x7fa11710ad90": 16, "factori": 16, "polynomi": 17, "coeffici": 17, "polynomial_dataset": 17, "must": [17, 19], "monomi": 17, "degre": 17, "mostli": 18, "quick": 18, "hack": 18, "debug": 18, "logrecordstreamhandl": 18, "request": 18, "client_address": 18, "streamrequesthandl": 18, "handler": 18, "stream": 18, "basic": 18, "record": 18, "polici": 18, "local": 18, "cookbook": 18, "http": [18, 20], "python": 18, "org": 18, "howto": 18, "html": 18, "handl": 18, "byte": 18, "length": 18, "follow": 18, "logrecord": 18, "format": 18, "accord": 18, "handle_log_record": 18, "logrecordsocketreceiv": 18, "host": 18, "port": 18, "threadingtcpserv": 18, "tcp": 18, "socket": 18, "suitabl": 18, "almost": 18, "verbatim": 18, "allow_reuse_address": 18, "serve_until_stop": 18, "start_logging_serv": 18, "9020": 18, "set_logg": 18, "_logger": 18, "lower_bound_hoeffd": 19, "delta": 19, "score_rang": 19, "lower": 19, "bound": 19, "requir": 19, "obtain": 19, "\u03b5": 19, "\u03b4": 19, "quantiti": 19, "n": [19, 20], "taken": 19, "powersetdistribut": 19, "enum": 19, "uniform": 19, "weight": 19, "max_subset": 19, "dist": 19, "uniformli": 19, "without": 19, "pre": 19, "arbitrarili": 19, "larg": 19, "howev": 19, "ten": 19, "thousand": 19, "can": [19, 20], "veri": 19, "long": 19, "henc": 19, "abil": 19, "you": 19, "wish": 19, "determinist": 19, "step": 19, "empti": 19, "like": 19, "distinct": 19, "rank": 19, "revers": 19, "perfect": 19, "match": 19, "independ": 19, "outdat": 20, "comment": 20, "some": 20, "statu": 20, "histor": 20, "algorithm": 20, "gather": 20, "later": 20, "ident": 20, "make_nested_backend": 20, "joblib": 20, "nest": 20, "would": 20, "sequentialbackend": 20, "github": 20, "com": 20, "issu": 20, "947": 20, "chunkifi": 20, "njob": 20, "interruptiblework": 20, "worker_id": 20, "queue": 20, "abort": 20, "consum": 20, "To": 20, "subclass": 20, "_run": 20, "self": 20, "shapleywork": 20, "instanti": 20, "coordin": 20, "therein": 20, "share": 20, "memori": 20, "avoid": 20, "both": 20, "flag": 20, "sub": 20, "overridden": 20, "processor": 20, "put": 20, "get_and_process": 20, "clear_task": 20, "clear_result": 20, "pbar": 20, "end": 20, "mockprogress": 21, "anyth": 21, "minimock": 21}, "objects": {"": [[5, 0, 0, "-", "valuation"]], "valuation": [[3, 0, 0, "-", "cli"], [4, 0, 0, "-", "dist_shapley"], [6, 0, 0, "-", "loo"], [8, 0, 0, "-", "reporting"], [11, 0, 0, "-", "shapley"], [15, 0, 0, "-", "utils"]], "valuation.cli": [[3, 1, 1, "", "maybe_init_task"]], "valuation.loo": [[7, 0, 0, "-", "naive"]], "valuation.loo.naive": [[7, 1, 1, "", "naive_loo"]], "valuation.reporting": [[9, 0, 0, "-", "plots"], [10, 0, 0, "-", "scores"]], "valuation.reporting.plots": [[9, 1, 1, "", "shaded_mean_std"], [9, 1, 1, "", "shapley_results"], [9, 1, 1, "", "spearman_correlation"]], "valuation.reporting.scores": [[10, 1, 1, "", "backward_elimination"], [10, 1, 1, "", "compute_fb_scores"], [10, 1, 1, "", "forward_selection"], [10, 1, 1, "", "sort_values"], [10, 1, 1, "", "sort_values_array"], [10, 1, 1, "", "sort_values_history"]], "valuation.shapley": [[11, 1, 1, "", "combinatorial_exact_shapley"], [11, 1, 1, "", "combinatorial_montecarlo_shapley"], [12, 0, 0, "-", "knn"], [13, 0, 0, "-", "montecarlo"], [14, 0, 0, "-", "naive"], [11, 1, 1, "", "permutation_exact_shapley"], [11, 1, 1, "", "permutation_montecarlo_shapley"], [11, 1, 1, "", "serial_truncated_montecarlo_shapley"], [11, 1, 1, "", "truncated_montecarlo_shapley"]], "valuation.shapley.knn": [[12, 1, 1, "", "exact_knn_shapley"]], "valuation.shapley.montecarlo": [[13, 1, 1, "", "combinatorial_montecarlo_shapley"], [13, 1, 1, "", "permutation_montecarlo_shapley"], [13, 1, 1, "", "serial_truncated_montecarlo_shapley"], [13, 1, 1, "", "truncated_montecarlo_shapley"]], "valuation.shapley.naive": [[14, 1, 1, "", "combinatorial_exact_shapley"], [14, 1, 1, "", "permutation_exact_shapley"]], "valuation.utils": [[15, 2, 1, "", "Dataset"], [15, 2, 1, "", "MapReduceJob"], [15, 2, 1, "", "SupervisedModel"], [15, 2, 1, "", "Utility"], [15, 1, 1, "", "available_cpus"], [15, 1, 1, "", "bootstrap_test_score"], [16, 0, 0, "-", "caching"], [17, 0, 0, "-", "dataset"], [18, 0, 0, "-", "logging"], [15, 1, 1, "", "map_reduce"], [15, 1, 1, "", "maybe_progress"], [15, 1, 1, "", "memcached"], [19, 0, 0, "-", "numeric"], [20, 0, 0, "-", "parallel"], [15, 1, 1, "", "powerset"], [21, 0, 0, "-", "progress"], [22, 0, 0, "-", "types"], [15, 1, 1, "", "unpackable"], [23, 0, 0, "-", "utility"], [15, 1, 1, "", "vanishing_derivatives"]], "valuation.utils.Dataset": [[15, 3, 1, "", "dim"], [15, 4, 1, "", "feature"], [15, 4, 1, "", "from_pandas"], [15, 4, 1, "", "from_sklearn"], [15, 3, 1, "", "indices"], [15, 5, 1, "", "pd"], [15, 4, 1, "", "target"]], "valuation.utils.MapReduceJob": [[15, 4, 1, "", "from_fun"], [15, 4, 1, "", "reduce"]], "valuation.utils.SupervisedModel": [[15, 4, 1, "", "fit"], [15, 4, 1, "", "predict"], [15, 4, 1, "", "score"]], "valuation.utils.Utility": [[15, 5, 1, "", "data"], [15, 5, 1, "", "model"], [15, 5, 1, "", "scoring"]], "valuation.utils.caching": [[16, 2, 1, "", "ClientConfig"], [16, 2, 1, "", "MemcachedConfig"], [16, 1, 1, "", "memcached"]], "valuation.utils.caching.ClientConfig": [[16, 5, 1, "", "connect_timeout"], [16, 4, 1, "", "items"], [16, 4, 1, "", "keys"], [16, 5, 1, "", "no_delay"], [16, 5, 1, "", "serde"], [16, 5, 1, "", "server"], [16, 5, 1, "", "timeout"], [16, 4, 1, "", "update"]], "valuation.utils.caching.MemcachedConfig": [[16, 5, 1, "", "client_config"], [16, 5, 1, "", "ignore_args"], [16, 4, 1, "", "items"], [16, 4, 1, "", "keys"], [16, 5, 1, "", "threshold"], [16, 4, 1, "", "update"]], "valuation.utils.dataset": [[17, 2, 1, "", "Dataset"], [17, 1, 1, "", "polynomial"], [17, 1, 1, "", "polynomial_dataset"]], "valuation.utils.dataset.Dataset": [[17, 3, 1, "", "dim"], [17, 4, 1, "", "feature"], [17, 4, 1, "", "from_pandas"], [17, 4, 1, "", "from_sklearn"], [17, 3, 1, "", "indices"], [17, 5, 1, "", "pd"], [17, 4, 1, "", "target"]], "valuation.utils.logging": [[18, 2, 1, "", "LogRecordSocketReceiver"], [18, 2, 1, "", "LogRecordStreamHandler"], [18, 1, 1, "", "set_logger"], [18, 1, 1, "", "start_logging_server"]], "valuation.utils.logging.LogRecordSocketReceiver": [[18, 5, 1, "", "allow_reuse_address"], [18, 4, 1, "", "serve_until_stopped"]], "valuation.utils.logging.LogRecordStreamHandler": [[18, 4, 1, "", "handle"], [18, 4, 1, "", "handle_log_record"]], "valuation.utils.numeric": [[19, 2, 1, "", "PowerSetDistribution"], [19, 1, 1, "", "lower_bound_hoeffding"], [19, 1, 1, "", "powerset"], [19, 1, 1, "", "random_powerset"], [19, 1, 1, "", "spearman"], [19, 1, 1, "", "vanishing_derivatives"]], "valuation.utils.numeric.PowerSetDistribution": [[19, 5, 1, "", "UNIFORM"], [19, 5, 1, "", "WEIGHTED"]], "valuation.utils.parallel": [[20, 2, 1, "", "Coordinator"], [20, 1, 1, "", "Identity"], [20, 2, 1, "", "InterruptibleWorker"], [20, 2, 1, "", "MapReduceJob"], [20, 1, 1, "", "available_cpus"], [20, 1, 1, "", "chunkify"], [20, 1, 1, "", "make_nested_backend"], [20, 1, 1, "", "map_reduce"]], "valuation.utils.parallel.Coordinator": [[20, 4, 1, "", "clear_results"], [20, 4, 1, "", "clear_tasks"], [20, 4, 1, "", "end"], [20, 4, 1, "", "get_and_process"], [20, 4, 1, "", "instantiate"], [20, 4, 1, "", "put"], [20, 4, 1, "", "start"]], "valuation.utils.parallel.InterruptibleWorker": [[20, 4, 1, "", "aborted"], [20, 4, 1, "", "run"]], "valuation.utils.parallel.MapReduceJob": [[20, 4, 1, "", "from_fun"], [20, 4, 1, "", "reduce"]], "valuation.utils.progress": [[21, 2, 1, "", "MockProgress"], [21, 1, 1, "", "maybe_progress"]], "valuation.utils.progress.MockProgress": [[21, 2, 1, "", "MiniMock"]], "valuation.utils.types": [[22, 2, 1, "", "SupervisedModel"], [22, 1, 1, "", "unpackable"]], "valuation.utils.types.SupervisedModel": [[22, 4, 1, "", "fit"], [22, 4, 1, "", "predict"], [22, 4, 1, "", "score"]], "valuation.utils.utility": [[23, 2, 1, "", "Utility"], [23, 1, 1, "", "bootstrap_test_score"]], "valuation.utils.utility.Utility": [[23, 5, 1, "", "data"], [23, 5, 1, "", "model"], [23, 5, 1, "", "scoring"]]}, "objtypes": {"0": "py:module", "1": "py:function", "2": "py:class", "3": "py:property", "4": "py:method", "5": "py:attribute"}, "objnames": {"0": ["py", "module", "Python module"], "1": ["py", "function", "Python function"], "2": ["py", "class", "Python class"], "3": ["py", "property", "Python property"], "4": ["py", "method", "Python method"], "5": ["py", "attribute", "Python attribute"]}, "titleterms": {"get": 0, "start": 0, "valuat": [1, 5], "guid": 1, "tutori": 1, "modul": 1, "indic": 1, "tabl": 1, "knn": [2, 12], "shaplei": [2, 11], "cli": 3, "dist_shaplei": 4, "loo": 6, "naiv": [7, 14], "report": 8, "plot": 9, "score": 10, "montecarlo": 13, "todo": 13, "util": [15, 23], "cach": 16, "dataset": 17, "log": 18, "numer": 19, "parallel": 20, "progress": 21, "type": 22}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 6, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx.ext.todo": 2, "nbsphinx": 4, "sphinx": 56}})