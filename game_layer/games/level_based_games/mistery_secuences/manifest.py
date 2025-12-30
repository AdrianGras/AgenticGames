from app_layer.registries.generic_registry import EntityManifest
from app_layer.registries.specs import IntParamSpec
from .mistery_secuences import MisterySecuences

# The discovery system will identify this instance via type inspection
manifest = EntityManifest(
    id="mystery_sequences",
    display_name="Mystery Sequences",
    cls=MisterySecuences,
    description=(
        "A logic-based challenge where players must deduce hidden rules governing "
        "binary sequences through iterative hypothesis testing and feedback."
    ),
    params=[
        IntParamSpec(
            id="max_consecutive_failed_attempts",
            label="Max Failed Attempts",
            description="The number of allowed consecutive incorrect inputs to prevent endless loops.",
            default=50,
            min_value=1,
            max_value=float('inf')
        )
    ]
)