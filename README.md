# Password Manager: generator-only prototype

A small Python CLI that generates random passwords using the standard library's
`secrets` module. **This is not a password vault.** It cannot store, encrypt,
retrieve, search, or sync passwords, and it has not received a security audit.

> **Important correction:** the original prototype printed the same hard-coded
> value for every `generate` command. Its `add` and `get` commands did not store
> or retrieve anything. Earlier claims about encrypted storage, a master
> password, categories, strength checking, and auto-lock were incorrect. If you
> used that old generated value for an account, replace that account's password
> using a trusted password manager. Do not rely on this project as a vault.

## Install from this repository

Python 3.8 or later is required. Use an isolated virtual environment:

```bash
git clone https://github.com/Master-626/password-manager.git
cd password-manager
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install .
```

These instructions install this repository. A similarly named package on a
package index is not a verified distribution of this project.

## Generate a password

```bash
passman generate                  # 20 characters by default
passman generate --length 32      # 8 to 1024 characters
passman generate --no-symbols     # letters and digits only
passman --help
```

Each command prints one password followed by a newline, with no label or color
formatting. Every result includes lowercase letters, uppercase letters, and
digits; symbols are also included unless `--no-symbols` is selected. Generation
uses the operating system's randomness through Python's `secrets.choice`, not a
fixed example or the `random` module.

Passwords are not written to a file or sent over the network by this program.
They are visible in your terminal and can be captured by terminal logs, screen
sharing, or a command that receives redirected output. Choose a length and
character set accepted by the destination service, and store passwords in an
established password manager.

The old `add` and `get` commands now exit with an explicit error. `add` never
prompts for a password. There is no master-password or encryption setup.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Tests cover output length and character classes, use of `secrets`, input
validation, CLI output, and rejection of the former storage placeholders.
The implementation is small and uses only Click and the Python standard
library. No cryptography implementation is included.

## License

[MIT License](LICENSE), retaining the original copyright notice.
