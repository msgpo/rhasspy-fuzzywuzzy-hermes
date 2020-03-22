"""Hermes MQTT service for rhasspy fuzzywuzzy"""
import argparse
import asyncio
import logging
import typing
from pathlib import Path

import paho.mqtt.client as mqtt
import rhasspyhermes.cli as hermes_cli

from . import NluHermesMqtt

_LOGGER = logging.getLogger("rhasspyfuzzywuzzy_hermes")

# -----------------------------------------------------------------------------


def main():
    """Main method."""
    parser = argparse.ArgumentParser(prog="rhasspy-fuzzywuzzy-hermes")
    parser.add_argument("--examples", help="Path to examples JSON file")
    parser.add_argument("--intent-graph", help="Path to intent graph JSON file")
    parser.add_argument(
        "--casing",
        choices=["upper", "lower", "ignore"],
        default="ignore",
        help="Case transformation for input text (default: ignore)",
    )
    parser.add_argument(
        "--replace-numbers",
        action="store_true",
        help="Replace digits with words in queries (75 -> seventy five)",
    )
    parser.add_argument(
        "--language", help="Language/locale used for number replacement (default: en)"
    )

    hermes_cli.add_hermes_args(parser)
    args = parser.parse_args()

    hermes_cli.setup_logging(args)
    _LOGGER.debug(args)

    try:
        # Convert to Paths
        if args.examples:
            args.examples = Path(args.examples)

        if args.intent_graph:
            args.intent_graph = Path(args.intent_graph)

        loop = asyncio.get_event_loop()

        # Listen for messages
        client = mqtt.Client()
        hermes = NluHermesMqtt(
            client,
            intent_graph_path=args.intent_graph,
            examples_path=args.examples,
            replace_numbers=args.replace_numbers,
            language=args.language,
            siteIds=args.siteId,
            loop=loop,
        )

        _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
        hermes_cli.connect(client, args)
        client.loop_start()

        # Run event loop
        hermes.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.debug("Shutting down")


# -----------------------------------------------------------------------------


def get_word_transform(name: str) -> typing.Callable[[str], str]:
    """Gets a word transformation function by name."""
    if name == "upper":
        return str.upper

    if name == "lower":
        return str.lower

    return lambda s: s


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
