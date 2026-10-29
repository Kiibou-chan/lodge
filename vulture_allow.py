from lodge.main import main

main  # noqa: B018  console script entry point

from lodge.core.yamlio import _TextLoader  # noqa: E402

_TextLoader.yaml_implicit_resolvers  # noqa: B018  PyYAML reads this class attribute

from lodge.core.snapshot import Tree  # noqa: E402

Tree.rev  # noqa: B018  the store port reports the revision a tree was read at

from tests.gitstore.conftest import isolated_git  # noqa: E402

isolated_git  # noqa: B018  pytest runs this autouse fixture

from lodge.viewer.server import _Handler, _Server  # noqa: E402

_Server.allow_reuse_address  # noqa: B018  http.server reads this class attribute
_Server.daemon_threads  # noqa: B018  socketserver reads this class attribute
_Handler.do_GET  # noqa: B018  http.server dispatches to do_<METHOD> by name
_Handler.do_HEAD  # noqa: B018
_Handler.do_PUT  # noqa: B018
_Handler.do_PATCH  # noqa: B018
_Handler.do_DELETE  # noqa: B018
_Handler.do_OPTIONS  # noqa: B018
_Handler.log_message  # noqa: B018  http.server calls this to log a request
