from dataclasses import dataclass, field
from typing import Type, List, Dict, TypeVar, Generic, Any, Iterator, Optional
from .specs import ParamSpec

# Generic type variable for the entity base class (e.g., CoreEngine or Actor)
T = TypeVar("T")

@dataclass(frozen=True)
class EntityManifest(Generic[T]):
    """
    A Manifest bridges a Domain Class with the metadata required by UI and CLI layers.
    
    Attributes:
        id: Unique identifier for the entity.
        display_name: Human-readable name for UI display.
        cls: The actual class to be instantiated (Game or Agent).
        params: A list of parameter specifications defining how to configure the entity.
        description: Optional long-form description of the entity's purpose.
    """
    id: str
    display_name: str
    cls: Type[T]
    params: List[ParamSpec] = field(default_factory=list)
    description: str = ""

class GenericRegistry(Generic[T]):
    """
    A generic storage system for Entity Manifests.
    
    Provides dictionary-like access and implements the Iterable protocol 
    to allow seamless integration with UI components and discovery logic.
    """

    def __init__(self, registry_name: str):
        """
        Initializes the registry with a specific name for logging/error purposes.
        """
        self._name = registry_name
        self._entities: Dict[str, EntityManifest[T]] = {}

    def register(self, manifest: EntityManifest[T]) -> None:
        """
        Registers a new manifest.
        
        Args:
            manifest: The EntityManifest instance to store.
            
        Raises:
            ValueError: If an entity with the same ID is already registered.
        """
        if manifest.id in self._entities:
            raise ValueError(
                f"[{self._name}] Entity with id '{manifest.id}' is already registered."
            )
        self._entities[manifest.id] = manifest

    def get(self, entity_id: str) -> EntityManifest[T]:
        """
        Retrieves a manifest by its unique ID.
        
        Args:
            entity_id: The ID of the manifest to retrieve.
            
        Returns:
            EntityManifest[T]: The requested manifest.
            
        Raises:
            ValueError: If the entity_id does not exist in the registry.
        """
        if entity_id not in self._entities:
            raise ValueError(
                f"[{self._name}] Entity '{entity_id}' not found in registry."
            )
        return self._entities[entity_id]

    def list_ids(self) -> List[str]:
        """Returns a list of all registered entity identifiers."""
        return list(self._entities.keys())

    def __iter__(self) -> Iterator[EntityManifest[T]]:
        """Allows direct iteration over manifests: for manifest in registry."""
        return iter(self._entities.values())

    def __len__(self) -> int:
        """Returns the number of registered entities."""
        return len(self._entities)

    def __getitem__(self, entity_id: str) -> EntityManifest[T]:
        """Allows dictionary-style access: registry['id']."""
        return self.get(entity_id)

    def __contains__(self, entity_id: str) -> bool:
        """Allows usage of 'in' operator: if 'id' in registry."""
        return entity_id in self._entities