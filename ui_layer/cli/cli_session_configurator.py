import argparse
import sys
from typing import Optional

from app_layer.registries.manager import get_game_registry, get_agent_registry
from app_layer.building.session_config import SessionConfig
from .register_param import register_param
from app_layer.registries.generic_registry import EntityManifest

class CLISessionConfigurator:
    """
    Orchestrates the discovery of domain entities and the dynamic construction 
    of the CLI environment to produce a validated SessionConfig.
    """

    def __init__(self):
        self.game_reg = get_game_registry()
        self.agent_reg = get_agent_registry()

    def get_session_config(self) -> SessionConfig:
        """
        Parses command-line arguments using a two-pass approach. 
        
        The first pass identifies the selected game and agent without triggering 
        validation errors, allowing the second pass to inject dynamic parameters 
        specific to those entities into the help menu and parser.
        
        Returns:
            SessionConfig: A validated configuration object for the session.
        """
        # 1. Discovery Phase
        pre_parser = argparse.ArgumentParser(add_help=False)
        pre_parser.add_argument("--game")
        pre_parser.add_argument("--agent")
        pre_parser.add_argument("--user_input", action="store_true")
        
        args_init, _ = pre_parser.parse_known_args()

        # 2. Construction Phase
        description = "Game Session Launcher"
        epilog = (
            "Note: Game-specific and Agent-specific options are only displayed "
            "when the --game and --agent arguments are provided.\n"
            "Example: python main.py --game <game_id> --help"
        )
        
        parser = argparse.ArgumentParser(
            description=description,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            "--game", 
            choices=self.game_reg.list_ids(), 
            required=True, 
            help="Unique identifier of the game to play."
        )
        parser.add_argument(
            "--agent", 
            choices=self.agent_reg.list_ids(), 
            help="AI agent strategy identifier."
        )
        parser.add_argument(
            "--user_input", 
            action="store_true", 
            help="Enable manual control mode (disables AI agent)."
        )

        # Dynamic injection for Game parameters
        game_manifest = None
        if args_init.game in self.game_reg.list_ids():
            game_manifest = self.game_reg.get(args_init.game)
            game_group = parser.add_argument_group(f"Settings: {game_manifest.display_name}")
            for spec in game_manifest.params:
                register_param(game_group, spec, prefix="g")

        # Dynamic injection for Agent parameters
        agent_manifest = None
        if not args_init.user_input and args_init.agent in self.agent_reg.list_ids():
            agent_manifest = self.agent_reg.get(args_init.agent)
            agent_group = parser.add_argument_group(f"Settings: {agent_manifest.display_name}")
            for spec in agent_manifest.params:
                register_param(agent_group, spec, prefix="a")

        # 3. Final Parse
        full_args = parser.parse_args()

        return self._build_config(full_args, game_manifest, agent_manifest)

    def _build_config(
        self, 
        args: argparse.Namespace, 
        game_manifest: EntityManifest, 
        agent_manifest: Optional[EntityManifest]
    ) -> SessionConfig:
        """
        Transforms parsed CLI arguments into a clean domain SessionConfig object.
        
        Args:
            args: Parsed command-line arguments.
            game_manifest: Metadata of the selected game.
            agent_manifest: Metadata of the selected agent (if any).
            
        Returns:
            SessionConfig: The domain-specific configuration.
        """
        game_params = {
            s.id: getattr(args, f"g_{s.id}") 
            for s in game_manifest.params
        }

        agent_params = None
        if agent_manifest:
            agent_params = {
                s.id: getattr(args, f"a_{s.id}") 
                for s in agent_manifest.params
            }

        return SessionConfig(
            game_name=game_manifest.id,
            is_human=args.user_input,
            agent_name=agent_manifest.id if agent_manifest else None,
            game_params=game_params,
            agent_params=agent_params
        )