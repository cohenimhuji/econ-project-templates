import json
from pathlib import Path

import pytask

from src.config import BLD

STATA_MODEL_COMMENT = """//
// Header with configuration for model:
//    {model_name}
//
// Automatically generated by pytask, do not change!
//
// Adjust model parameters in:
//    {path}
//\n\n\n"""


model_names = ["baseline", "rmconj"]


@pytask.mark.parametrize(
    "depends_on, produces",
    [[Path(f"{m}.json"), BLD / "model_specs" / f"{m}.do"] for m in model_names],
)
def task_model_json_to_do_file(depends_on, produces):
    """Convert a JSON model specification in ``depends_on`` to a Stata
    do-file, storing dictionary entries in globals.

    Require the JSON file to contain a single, non-nested, dictionary.

    Simply write its entries as Stata globals to the target file.

    """

    model_pars = json.load(depends_on.open())
    model_name = depends_on.stem

    tgt_content = STATA_MODEL_COMMENT.format(model_name=model_name, path=depends_on)
    tgt_content += f'global MODEL_NAME = "{model_name}"\n\n'
    for key, val in sorted(model_pars.items()):
        # Adjust for Stata string notation
        if isinstance(val, str):
            val = f'"{val}"'
        tgt_content += f"global {key} = {val}\n"
    return produces.write_text(tgt_content)


@pytask.mark.depends_on(Path("geography.json"))
@pytask.mark.produces(BLD / "model_specs" / "geography.do")
def task_geography_json_to_do_file(depends_on, produces):
    """Convert the geography model specification in ``depends_on`` to
    a Stata do-file.

    The geography.json file has a different structure than the other ones,
    we get numbers from the order of the list of dictionaries.

    """

    geo_dict_list = json.load(depends_on.open())
    model_name = depends_on.stem

    tgt_content = STATA_MODEL_COMMENT.format(model_name=model_name, path=depends_on)
    i = 1
    for geo_dict in geo_dict_list:
        for key, val in geo_dict.items():
            # Adjust for Stata string notation
            if isinstance(val, str):
                val = f'"{val}"'
            tgt_content += f"global {key}_{i} = {val}\n"
        i += 1
    return produces.write_text(tgt_content)