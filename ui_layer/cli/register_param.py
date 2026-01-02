# cli_layer/cli_adapter.py

import argparse
from app_layer.registries.specs import (
    ParamSpec, IntParamSpec, FloatParamSpec, ChoiceParamSpec, BoolParamSpec
)

def register_param(group: argparse._ArgumentGroup, spec: ParamSpec, prefix: str) -> None:
    """
    Binds a domain ParamSpec to an argparse group, handling CLI-specific 
    naming conventions and type casting.
    """
    param_id = spec.id
    
    # Prefix logic for booleans to ensure they read like predicates
    if isinstance(spec, BoolParamSpec):
        if not (param_id.startswith("is_") or param_id.startswith("has_")):
            param_id = f"is_{param_id}"

    arg_name = f"--{prefix}_{param_id}"
    destination = f"{prefix}_{spec.id}" # Matches domain SessionConfig key
    help_text = spec.description

    match spec:
        case IntParamSpec(default=val, min_value=mi, max_value=ma):
            range_hint = f" [{mi}-{ma}]" if mi is not None or ma is not None else ""
            group.add_argument(
                arg_name, dest=destination, type=int, default=val,
                help=f"{help_text} (Default: {val}){range_hint}"
            )

        case FloatParamSpec(default=val, min_value=mi, max_value=ma, step=s):
            range_hint = f" [{mi}-{ma}]" if mi is not None or ma is not None else ""
            group.add_argument(
                arg_name, dest=destination, type=float, default=val,
                help=f"{help_text} (Default: {val}){range_hint} [Step: {s}]"
            )

        case ChoiceParamSpec(default=val, choices=opts):
            group.add_argument(
                arg_name, dest=destination, type=str, default=val,
                choices=opts, help=f"{help_text} (Default: {val})"
            )

        case BoolParamSpec(default=val):
            # Industry standard for toggles: provides --flag and --no-flag
            group.add_argument(
                arg_name, dest=destination, default=val,
                action=argparse.BooleanOptionalAction,
                help=f"{help_text} (Default: {val})"
            )

        case _:
            group.add_argument(
                arg_name, dest=destination, type=str, default=str(spec.default),
                help=f"{help_text} (Default: {spec.default})"
            )