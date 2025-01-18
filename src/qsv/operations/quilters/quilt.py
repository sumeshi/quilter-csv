import re
from typing import Union, Optional, Literal
from qsv.controllers.LogController import LogController
from qsv.controllers.QuiltController import QuiltController
import polars as pl

def process(dfc, steps: dict, path: tuple[str], source: Optional[pl.LazyFrame] = None) -> pl.LazyFrame:
    default_path = path

    # drop dataframe before each stage
    dfc.drop()

    # pipeline
    if source is not None:
        dfc.df = source

    for k, v in steps:
        # for allow duplicated rulenames.
        k = k if not k.endswith('_') else re.sub(r'_+$', '', k) 

        if k == 'load':
            dfc.load(*path)
        elif v:
            getattr(dfc, k)(**v)
        else:
            getattr(dfc, k)()
    
    return dfc.df


def concat(
        df_list: list[pl.LazyFrame],
        how: Literal['vertical', 'vertical_relaxed', 'horizontal', 'diagonal', 'align']
    ) -> pl.LazyFrame:
    return pl.concat(df_list, how=how)


def join(
        df_list: list[pl.LazyFrame],
        how: Literal['inner', 'left', 'right', 'full', 'semi', 'anti', 'cross'],
        key: Union[str, list[str]],
        coalesce: bool
    ) -> pl.LazyFrame:
    return df_list[0].join(df_list[1], how=how, on=key, coalesce=coalesce)


def quilt(dfc, config: str, path: tuple[str]) -> None:
    """[quilter] Loads the specified quilt batch files."""
    LogController.debug(f"config: {config}")
    LogController.debug(f"{len(path)} files are loaded. [{', '.join(path)}]")

    q = QuiltController()
    configs = q.load_configs(config)
    q.print_configs(configs)

    # per config file
    for config in configs:
        # per stage
        df_dict = dict()

        for stage_key, stage_values in config.get('stages').items():
            stage_type = stage_values.get('type')

            if stage_type == "process":
                if 'source' in stage_values:
                    # pipeline
                    df_dict[stage_key] = process(
                        dfc=dfc,
                        steps=stage_values.get('steps').items(),
                        path=path,
                        source=df_dict[stage_values.get('source')],
                    )
                else:
                    # load from file
                    df_dict[stage_key] = process(
                        dfc=dfc,
                        steps=stage_values.get('steps').items(),
                        path=path
                    )

            elif stage_type == "concat":
                sources = stage_values.get('sources')
                how = stage_values.get('params', dict()).get('how', 'vertical')
                df_dict[stage_key] = concat(
                    df_list=[df_dict.get(source) for source in sources],
                    how=how
                )

            elif stage_type == "join":
                sources = stage_values.get('sources')
                how = stage_values.get('params', dict()).get('how', 'full')
                key = stage_values.get('params', dict()).get('key')
                coalesce = stage_values.get('params', dict()).get('coalesce', True)

                df_dict[stage_key] = join(
                    df_list=[df_dict.get(source) for source in sources],
                    how=how,
                    key=key,
                    coalesce=coalesce
                )
