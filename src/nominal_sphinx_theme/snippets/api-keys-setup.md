% Source: fern-docs 1b72bbf5, fern/docs/pages/core/sdk/python/getting-started.mdx
% Inlined: fern/snippets/api-key.mdx, fern/snippets/python/auth.mdx

There is a one-time setup of API-keys required to use   Nominal clients. There are 2 steps: 

## 1. Create the config file. 

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: windows

Save it as `%USERPROFILE%\.config\nominal\config.yml`:

```yaml
version: 2
profiles:
  default:
    token: API_KEY
    base_url: BASE_URL
    workspace_rid: WORKSPACE_RID
```
:::

:::{tab-item} Linux
:sync: linux

Save it as `~/.config/nominal/config.yml`:

```yaml
version: 2
profiles:
  default:
    token: API_KEY
    base_url: BASE_URL
    workspace_rid: WORKSPACE_RID
```
:::

:::{tab-item} macOS
:sync: macos

Save it as `~/.config/nominal/config.yml`:

```yaml
version: 2
profiles:
  default:
    token: API_KEY
    base_url: BASE_URL
    workspace_rid: WORKSPACE_RID
```
:::
::::



The file holds your API key in plain text, so keep it out of version control and shared folders!
## 2. Fill in your  KEYS
Next, visit your [API keys](https://app.gov.nominal.io/settings/org/api-keys) page in the cloud Nominal app, and copy three values to store in your config file.   


```{image} api-keys.png
:alt: The API keys page in Nominal settings, with the Create key button marked 1, the Copy URL button marked 2, and a workspace's Copy RID button marked 3
:align: right
:width: 469px
:class: callout-screenshot
```
There are 3 values:

{.callouts}
1. **API key:** Click **CREATE KEY**, give the key a name, set an expiration, and click **GENERATE KEY**. Note, this is only shown once.
1. **Base URL:** Find **API URL** and click **COPY URL**.
1. **Workspace RID:** Find your workspace and click **COPY RID**.


## Details
:::{dropdown} Profiles
 Each key under `profiles` (`default` in the template above) is a profile name, and you can add more profiles to connect to other workspaces or instances.
:::

 


:::::{dropdown} Store credentials with command line tools
Nominal provides two command line tools, a [Rust-based](https://github.com/nominal-io/nominal-client-rs#nomctl-cli) one, `nomctl`, and a [Python-based](https://github.com/nominal-io/nominal-client#-install) one. Use `nomctl` unless you already use the Python client or IT restrictions make the Python CLI easier to install.

**Rust: nomctl**

To install, run:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: windows

In PowerShell:

```powershell
irm https://raw.githubusercontent.com/nominal-io/nominal-client-rs/main/scripts/install.ps1 | iex
```

The installer also adds nomctl to your `PATH`.
:::

:::{tab-item} Linux
:sync: linux

```bash
curl -fsSL https://raw.githubusercontent.com/nominal-io/nominal-client-rs/main/scripts/install.sh | sh
```

If you get an error that `nomctl` is not found when running the steps below, either call `~/.local/bin/nomctl` directly or add `~/.local/bin` to your `PATH` and open a new terminal:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```
:::

:::{tab-item} macOS
:sync: macos

```zsh
curl -fsSL https://raw.githubusercontent.com/nominal-io/nominal-client-rs/main/scripts/install.sh | sh
```

If you get an error that `nomctl` is not found when running the steps below, either call `~/.local/bin/nomctl` directly or add `~/.local/bin` to your `PATH` and open a new terminal:

```zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```
:::
::::

Finally, to create the credential file using the three credentials collected above, run:

```shell
nomctl config profile add default -t <1:api-key> -u <2:base-url> -w <3:workspace-rid>
```

To check the profile was saved:

```shell
nomctl config profile list
```

:::{tip}
`nomctl config init` creates the profile interactively instead, and lets you pick your workspace from a list rather than pasting its RID.
:::

**Python: nominal.cli**

To install, run `pip install nominal`. If your system Python blocks `pip install`, as on some Linux distributions and with Homebrew's Python on macOS, install into a virtual environment, or use `uv tool install nominal` or `pipx install nominal` and run `nom` in place of `python -m nominal.cli` below.

Then, using the three credentials collected above, run the first command below. The second checks the profile was saved.

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: windows

```powershell
python -m nominal.cli config profile add default -t <1:api-key> -u <2:base-url> -w <3:workspace-rid>
python -m nominal.cli config profile list
```
:::

:::{tab-item} Linux
:sync: linux

```bash
python3 -m nominal.cli config profile add default -t <1:api-key> -u <2:base-url> -w <3:workspace-rid>
python3 -m nominal.cli config profile list
```
:::

:::{tab-item} macOS
:sync: macos

```zsh
python3 -m nominal.cli config profile add default -t <1:api-key> -u <2:base-url> -w <3:workspace-rid>
python3 -m nominal.cli config profile list
```
:::
::::
:::::
