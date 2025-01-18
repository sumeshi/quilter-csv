import re
from qsv.controllers.LogController import LogController
from qsv.controllers.QuiltController import QuiltController

def quilt(dfc, config: str, path: tuple[str], debug: bool = False) -> None:
    """[quilter] Loads the specified quilt batch files."""
    LogController.debug(f"config: {config}")
    LogController.debug(f"{len(path)} files are loaded. [{', '.join(path)}]")

    q = QuiltController()
    configs = q.load_configs(config)
    q.print_configs(configs)

    for c in configs:
        for k, v in c.get('rules').items():
            # for allow duplicated rulenames.
            k = k if not k.endswith('_') else re.sub(r'_+$', '', k) 

            if debug:
                print(f"{k}: {v}")

            if k == 'load':
                dfc.load(*path)
            elif v:
                getattr(dfc, k)(**v)
            else:
                getattr(dfc, k)()

            if debug:
                print(dfc.df.collect())
                print()
