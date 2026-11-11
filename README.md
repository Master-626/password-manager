# Password Manager: generator-only prototype

## 简要说明

这是一个用 Python `secrets` 生成随机密码的命令行工具，**不是密码库**。它不能保存、加密、查询或同步密码。默认打印一条 20 位密码，包含大小写字母和数字，并默认包含符号。可用 `--length`（8–1024）、`--no-symbols` 和 `--count`（1–100，每行一条）调整。安装：`python -m pip install .`，然后执行 `passman generate`。测试：`python -m pip install -e ".[dev]"` 后运行 `python -m pytest`。请把密码存进可靠的密码管理器；不要把本工具当作保险库。

## What this is

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
passman generate                  # one password, 20 characters
passman generate --length 32      # 8 to 1024 characters
passman generate --no-symbols     # letters and digits only
passman generate --count 5        # five passwords, one per line
passman generate -l 16 -n 3 --no-symbols
passman --help
passman generate --help
```

Each invocation prints the requested passwords and nothing else: no label and
no color formatting. Every password includes lowercase letters, uppercase
letters, and digits. Symbols are included unless `--no-symbols` is selected.
Generation uses the operating system's randomness through Python's
`secrets.choice`, not a fixed example or the `random` module.

### Options

| Option | Short | Default | Meaning |
| --- | --- | --- | --- |
| `--length` | `-l` | `20` | Length from 8 to 1024 |
| `--symbols` / `--no-symbols` | | symbols on | Include or omit ASCII punctuation |
| `--count` | `-n` | `1` | How many passwords to print (1 to 100), one per line |

Passwords are not written to a file or sent over the network by this program.
They are visible in your terminal and can be captured by terminal logs, screen
sharing, or a command that receives redirected output. Choose a length and
character set accepted by the destination service, and store passwords in an
established password manager.

The old `add` and `get` commands now exit with an explicit error. `add` never
prompts for a password. There is no master-password or encryption setup. If a
command line is rejected, the program does not print the extra text you typed,
so a password passed by mistake is not copied into the error.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
```

`pytest` runs the suite (including the original unittest modules). `ruff`
checks `src` and `tests`. Continuous integration does both: ruff on Python
3.12, and pytest on Python 3.8, 3.9, 3.10, 3.11, 3.12, and 3.13.

Tests cover output length and character classes, use of `secrets`, input
validation, CLI output, rejection of the former storage placeholders, a bound
on unlucky sampling, and exact output when the password is captured. The
implementation uses only Click and the Python standard library. No
cryptography implementation is included. Pytest and Ruff are development
dependencies.

## License

[MIT License](LICENSE), retaining the original copyright notice.
